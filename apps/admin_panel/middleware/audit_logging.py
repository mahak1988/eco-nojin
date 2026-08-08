"""Security and audit logging middleware for admin panel."""

import logging
import time
from datetime import datetime

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from apps.admin_panel.service import AdminService
from apps.users.models import User

logger = logging.getLogger(__name__)


class AuditLoggingMiddleware:
    """Middleware for logging admin panel activities and security events."""

    def __init__(self, admin_service: AdminService):
        self.admin_service = admin_service
        self.security_logger = logging.getLogger("security")

    async def __call__(self, request: Request, call_next):
        # Record start time for performance monitoring
        start_time = time.time()

        # Get user info if available
        user: User | None = getattr(request.state, "user", None)

        # Log the incoming request
        await self.log_request(request, user)

        try:
            response = await call_next(request)
        except HTTPException as e:
            # Log security violations
            await self.log_security_event(
                request=request,
                user=user,
                event_type="security_violation",
                event_data={
                    "status_code": e.status_code,
                    "detail": e.detail,
                    "path": request.url.path,
                    "method": request.method,
                },
            )
            raise
        except Exception as e:
            # Log unexpected errors
            await self.log_security_event(
                request=request,
                user=user,
                event_type="system_error",
                event_data={"error": str(e), "path": request.url.path, "method": request.method},
            )
            response = JSONResponse(status_code=500, content={"detail": "Internal server error"})

        # Calculate processing time
        processing_time = time.time() - start_time

        # Log the response
        await self.log_response(request, response, processing_time, user)

        # Add security headers to response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"

        return response

    async def log_request(self, request: Request, user: User | None):
        """Log incoming request for audit purposes."""
        event_data = {
            "method": request.method,
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "user_agent": request.headers.get("user-agent"),
            "ip_address": self.get_client_ip(request),
            "timestamp": datetime.utcnow().isoformat(),
        }

        event_type = f"request_{request.method.lower()}"

        await self.record_audit_event(event_type=event_type, event_data=event_data, user=user)

    async def log_response(
        self, request: Request, response: Response, processing_time: float, user: User | None
    ):
        """Log outgoing response for audit purposes."""
        event_data = {
            "status_code": response.status_code,
            "processing_time_ms": round(processing_time * 1000, 2),
            "path": request.url.path,
            "method": request.method,
            "timestamp": datetime.utcnow().isoformat(),
        }

        event_type = f"response_{response.status_code}"

        await self.record_audit_event(event_type=event_type, event_data=event_data, user=user)

    async def log_security_event(
        self, request: Request, user: User | None, event_type: str, event_data: dict
    ):
        """Log security-related events."""
        event_data.update(
            {
                "path": request.url.path,
                "method": request.method,
                "ip_address": self.get_client_ip(request),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        await self.record_audit_event(event_type=event_type, event_data=event_data, user=user)

        # Log to security logger as well
        self.security_logger.warning(f"Security event: {event_type} - {event_data}")

    async def record_audit_event(self, event_type: str, event_data: dict, user: User | None):
        """Record audit event using admin service."""
        try:
            await self.admin_service.record_audit_event(
                event_type=event_type,
                event_data=str(event_data),  # Convert to string for storage
                actor=user,
            )
        except Exception as e:
            # Don't let audit logging failures break the main flow
            logger.error(f"Failed to record audit event: {e}")

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers first (behind proxies/load balancers)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"


# Role-Based Access Control (RBAC) utilities
class RBAC:
    """Role-based access control utilities for admin panel."""

    ADMIN_PERMISSIONS = {
        "dashboard.view",
        "settings.read",
        "settings.write",
        "users.manage",
        "audit.logs.read",
        "reports.generate",
        "system.health.check",
    }

    SUPERUSER_PERMISSIONS = ADMIN_PERMISSIONS.union(
        {"users.create", "users.delete", "system.configure", "security.manage"}
    )

    @staticmethod
    async def check_permission(user: User, permission: str) -> bool:
        """Check if user has specific permission."""
        if user.is_superuser:
            return True

        # For regular admins, check against allowed permissions
        if user.role == "admin":
            return permission in RBAC.ADMIN_PERMISSIONS

        return False

    @staticmethod
    async def require_permission(user: User, permission: str):
        """Raise HTTP exception if user doesn't have permission."""
        if not await RBAC.check_permission(user, permission):
            raise HTTPException(status_code=403, detail="Insufficient permissions")

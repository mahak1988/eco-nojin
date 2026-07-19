"""
Audit Logging Middleware
=========================
Logs all authentication-related requests for security monitoring.
Based on patterns from OWASP API Security guidelines.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger("audit")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """
    Audit logging middleware for security compliance.
    
    Logs all auth requests with:
    - User ID (from token if available)
    - IP address
    - Request method and path
    - Response status
    - Timestamp
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        # Log auth-related endpoints
        audit_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }
        
        # Try to extract user ID from JWT token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            audit_data["has_token"] = True
        
        response = await call_next(request)
        
        audit_data["status_code"] = response.status_code
        audit_data["response_time_ms"] = response.headers.get("x-process-time", "0")
        
        # Log to structured JSON
        if request.url.path.startswith("/api/v1/auth") or auth_header:
            logger.info(json.dumps(audit_data, ensure_ascii=False))
        
        return response
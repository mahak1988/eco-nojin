"""Role-Based Access Control (RBAC) middleware for admin panel."""

import logging
from typing import List, Optional

from fastapi import HTTPException, Request

from apps.users.models import User
from .audit_logging import RBAC

logger = logging.getLogger(__name__)


class RBACMiddleware:
    """Middleware for enforcing role-based access control."""
    
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions
    
    async def __call__(self, request: Request):
        # Get user from request state (should be set by auth middleware)
        user: Optional[User] = getattr(request.state, 'user', None)
        
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Check each required permission
        for permission in self.required_permissions:
            has_permission = await RBAC.check_permission(user, permission)
            if not has_permission:
                logger.warning(
                    f"Access denied for user {user.email} to {request.url.path} "
                    f"with permission {permission}"
                )
                raise HTTPException(
                    status_code=403,
                    detail=f"Insufficient permissions: {permission}"
                )
        
        # Add user permissions to request state for use in handlers
        request.state.user_permissions = await self.get_user_permissions(user)
        
        return request
    
    async def get_user_permissions(self, user: User) -> List[str]:
        """Get all permissions for the user."""
        if user.is_superuser:
            return list(RBAC.SUPERUSER_PERMISSIONS)
        elif user.role == "admin":
            return list(RBAC.ADMIN_PERMISSIONS)
        else:
            return []


def require_permission(permission: str):
    """Decorator to require specific permission for a route."""
    def decorator(func):
        # Store required permissions in function attribute
        if not hasattr(func, '_required_permissions'):
            func._required_permissions = []
        func._required_permissions.append(permission)
        return func
    return decorator


def require_any_permission(*permissions: str):
    """Decorator to require at least one of the specified permissions."""
    def decorator(func):
        # Store required permissions in function attribute
        if not hasattr(func, '_any_permissions'):
            func._any_permissions = []
        func._any_permissions.extend(permissions)
        return func
    return decorator


def check_route_permissions(route_func, user: User) -> bool:
    """Check if user has permissions for a specific route."""
    # Check all required permissions
    if hasattr(route_func, '_required_permissions'):
        for perm in route_func._required_permissions:
            if not RBAC.check_permission(user, perm):
                return False
    
    # Check any-of permissions
    if hasattr(route_func, '_any_permissions'):
        any_perm_granted = False
        for perm in route_func._any_permissions:
            if RBAC.check_permission(user, perm):
                any_perm_granted = True
                break
        if not any_perm_granted:
            return False
    
    return True
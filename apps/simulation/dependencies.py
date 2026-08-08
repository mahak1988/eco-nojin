"""
simulation dependencies | وابستگی‌های simulation
===============================================
FastAPI dependency injections for the simulation module.

NOTE: Adjust to match your project's auth/permission system.
"""

import logging

logger = logging.getLogger(__name__)
from typing import Annotated

from fastapi import Depends, HTTPException, status

# Import the real user dependency from the users module
from apps.users.dependencies import get_current_user as get_real_current_user

CurrentUser = Annotated[dict, Depends(get_real_current_user)]


def require_role(*roles: str) -> None:
    """Dependency factory: require the user to have one of the given roles."""
    async def _check(user: CurrentUser) -> dict:
        """Handle _check (user)."""
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Insufficient permissions.",
            )
        return user
    return Depends(_check)


def require_permission(permission: str):
    """Dependency factory: require the user to have a specific permission."""
    # This relies on the underlying implementation in shared_core.rbac
    # which should fetch permissions for the user from the database/session.
    from apps.shared_core.rbac.deps import require_permission as rbac_require_permission
    return rbac_require_permission(permission)
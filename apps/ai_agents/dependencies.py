"""
ai_agents dependencies | وابستگی‌های ai_agents
===============================================
FastAPI dependency injections for the ai_agents module.

NOTE: Adjust to match your project's auth/permission system.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status


# Example: a stub for the current user dependency.
# Replace with your real auth dependency (e.g., from apps.users.dependencies).
async def get_current_user() -> dict:
    """Return the current authenticated user."""
    # TODO: integrate with apps.users.auth_router / JWT validation
    return {"id": 1, "email": "anonymous@example.com", "role": "user"}


CurrentUser = Annotated[dict, Depends(get_current_user)]


def require_role(*roles: str):
    """Dependency factory: require the user to have one of the given roles."""
    async def _check(user: CurrentUser) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(roles)}",
            )
        return user
    return _check

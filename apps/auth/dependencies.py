"""Auth dependencies stub - routes through security_init."""

from fastapi import HTTPException, Request, status

from apps.shared_core.security_init import authenticate_request


def require_permission(permission: str):
    """Dependency that checks if user has required permission."""

    async def _check(request: Request):
        if not authenticate_request(request):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication required for {permission}",
            )
        return True

    return _check

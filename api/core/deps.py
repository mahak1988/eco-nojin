from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from api.core.config import settings
from api.core.security import decode_token, security


async def require_write_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    if not settings.REQUIRE_AUTH_FOR_WRITES:
        return "system"
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for this operation",
        )
    return decode_token(credentials.credentials)

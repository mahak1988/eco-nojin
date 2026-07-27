"""FastAPI dependencies — auth & session (python-jose only, no PyJWT)."""

from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session
from apps.shared_core.security import decode_token

logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)

SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
TokenDep = Annotated[str | None, Depends(reusable_oauth2)]


async def get_current_user(
    session: SessionDep,
    token: TokenDep,
) -> dict[str, Any]:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    try:
        from sqlalchemy import select

        from apps.users.models import User

        # sub may be email or id
        if str(sub).isdigit():
            result = await session.execute(select(User).where(User.id == int(sub)))
        else:
            result = await session.execute(select(User).where(User.email == str(sub)))
        user = result.scalar_one_or_none()
        if user is None:
            return {
                "id": sub,
                "email": str(sub) if not str(sub).isdigit() else None,
                "is_authenticated": True,
                "is_active": True,
                "is_superuser": False,
            }
        return {
            "id": user.id,
            "email": getattr(user, "email", None),
            "is_authenticated": True,
            "is_active": bool(getattr(user, "is_active", True)),
            "is_superuser": bool(getattr(user, "is_superuser", False)),
        }
    except Exception as e:
        logger.debug("user lookup fallback: %s", e)
        return {
            "id": sub,
            "is_authenticated": True,
            "is_active": True,
            "is_superuser": False,
        }


CurrentUser = Annotated[dict, Depends(get_current_user)]


async def get_current_active_user(current_user: CurrentUser) -> dict[str, Any]:
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


CurrentActiveUser = Annotated[dict, Depends(get_current_active_user)]


async def get_current_superuser(current_user: CurrentActiveUser) -> dict[str, Any]:
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentSuperUser = Annotated[dict, Depends(get_current_superuser)]


async def require_write_auth(
    token: TokenDep = None,
    session: SessionDep = None,
) -> dict[str, Any] | None:
    """When REQUIRE_AUTH_FOR_WRITES is False (local default), allow without token."""
    if not settings.REQUIRE_AUTH_FOR_WRITES:
        return None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for write operations",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await get_current_user(session, token)

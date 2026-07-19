"""
Econojin - Dependency Injection Module
========================================
Adapted from fastapi/full-stack-fastapi-template with async SQLAlchemy support.
Provides reusable FastAPI dependencies for authentication, database sessions,
and authorization.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session, AsyncSession
from apps.shared_core.security import decode_token

# ── OAuth2 Scheme ──────────────────────────────────────────────
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)

# ── Type Aliases ───────────────────────────────────────────────
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
TokenDep = Annotated[str | None, Depends(reusable_oauth2)]


async def get_current_user(
    session: SessionDep,
    token: TokenDep,
) -> dict:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        session: Database session
        token: JWT token from Authorization header
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException 401: If token is invalid or user not found
        HTTPException 403: If token validation fails
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    # Try to get user from database
    try:
        from apps.users.models import User
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
    except Exception:
        # Fallback: return basic user info from token
        return {"id": user_id, "is_authenticated": True}
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]


async def get_current_active_user(
    current_user: CurrentUser,
) -> dict:
    """
    Verify the current user is active.
    
    Args:
        current_user: User data from get_current_user
        
    Returns:
        User data if active
        
    Raises:
        HTTPException 400: If user is inactive
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


CurrentActiveUser = Annotated[dict, Depends(get_current_active_user)]


async def get_current_superuser(
    current_user: CurrentActiveUser,
) -> dict:
    """
    Verify the current user is a superuser.
    
    Args:
        current_user: Active user data
        
    Returns:
        User data if superuser
        
    Raises:
        HTTPException 403: If user is not a superuser
    """
    if not current_user.get("is_superuser", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
    return current_user


CurrentSuperUser = Annotated[dict, Depends(get_current_superuser)]


async def require_write_auth(
    current_user: CurrentActiveUser,
) -> dict:
    """
    Require authentication for write operations when configured.
    Used as a dependency for POST/PUT/DELETE endpoints.
    
    Args:
        current_user: Active user data
        
    Returns:
        User data if authorized
    """
    if settings.REQUIRE_AUTH_FOR_WRITES and not current_user.get("is_authenticated"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required for write operations",
        )
    return current_user
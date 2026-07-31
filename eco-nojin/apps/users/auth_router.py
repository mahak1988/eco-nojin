"""Authentication — HttpOnly cookies + RS256/HS256 via shared security module."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db
from apps.shared_core.security import (
    cookie_kwargs,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from apps.shared_core.token_store import is_refresh_revoked, revoke_refresh
from apps.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer(auto_error=False)

ACCESS_COOKIE = settings.JWT_COOKIE_NAME
REFRESH_COOKIE = settings.REFRESH_COOKIE_NAME
ALLOWED_ROLES = {"farmer", "expert", "viewer"}


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str

    @model_validator(mode="before")
    @classmethod
    def check_email_or_username(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if not values.get("email") and not values.get("username"):
                raise ValueError("Either email or username must be provided")
            if values.get("username") and not values.get("email") and "@" in str(values["username"]):
                values["email"] = values["username"]
        return values


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    full_name: str | None = Field(None, max_length=255)
    phone: str | None = Field(None, max_length=40)
    organization: str | None = Field(None, max_length=255)
    role: Literal["farmer", "expert", "viewer"] = "farmer"
    accept_terms: bool = False

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @model_validator(mode="after")
    def must_accept_terms(self) -> RegisterRequest:
        if not self.accept_terms:
            raise ValueError("You must accept the Terms of Service and Privacy Policy")
        return self


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    phone: str | None = None
    organization: str | None = None
    role: str = "farmer"
    is_active: bool
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    refreshToken: str | None = None


def _user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=getattr(user, "full_name", None),
        phone=getattr(user, "phone", None),
        organization=getattr(user, "organization", None),
        role=getattr(user, "role", None) or "farmer",
        is_active=bool(getattr(user, "is_active", True)),
        is_superuser=bool(getattr(user, "is_superuser", False)),
        created_at=getattr(user, "created_at", None),
        updated_at=getattr(user, "updated_at", None),
    )


def _set_auth_cookies(response: Response, access: str, refresh: str) -> None:
    access_max = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_max = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    response.set_cookie(ACCESS_COOKIE, access, **cookie_kwargs(access_max))
    response.set_cookie(REFRESH_COOKIE, refresh, **cookie_kwargs(refresh_max))


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")


def _token_from_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None,
) -> str | None:
    if credentials and credentials.credentials:
        return credentials.credentials
    return request.cookies.get(ACCESS_COOKIE)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _token_from_request(request, credentials)
    if not token:
        raise credentials_exception
    try:
        payload = decode_token(token)
        email: str | None = payload.get("sub")
        if email is None or payload.get("type") != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    role = body.role if body.role in ALLOWED_ROLES else "farmer"
    new_user = User(
        email=str(body.email).lower(),
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        phone=body.phone,
        organization=body.organization,
        role=role,
        is_active=True,
        is_superuser=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    access = create_access_token(new_user.email)
    refresh = create_refresh_token(new_user.email)
    _set_auth_cookies(response, access, refresh)

    return AuthResponse(
        accessToken=access,
        refreshToken=refresh,
        user=_user_response(new_user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    identifier = body.email or body.username
    if not identifier:
        raise HTTPException(status_code=400, detail="Invalid login credentials")

    result = await db.execute(select(User).where(User.email == str(identifier).lower()))
    user = result.scalar_one_or_none()
    stored = getattr(user, "hashed_password", None) if user else None
    if not user or not stored or not verify_password(body.password, stored):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access = create_access_token(user.email)
    refresh = create_refresh_token(user.email)
    _set_auth_cookies(response, access, refresh)

    return AuthResponse(
        accessToken=access,
        refreshToken=refresh,
        user=_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _user_response(current_user)


@router.post("/logout")
async def logout(request: Request, response: Response) -> dict[str, str]:
    raw = request.cookies.get(REFRESH_COOKIE)
    if raw:
        try:
            payload = decode_token(raw)
            jti = payload.get("jti")
            if jti:
                revoke_refresh(str(jti))
        except JWTError:
            pass
    _clear_auth_cookies(response)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    response: Response,
    request: Request,
    body: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    raw = None
    if body and body.refreshToken:
        raw = body.refreshToken
    if not raw:
        raw = request.cookies.get(REFRESH_COOKIE)
    if not raw:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = decode_token(raw)
        email = payload.get("sub")
        jti = payload.get("jti")
        if payload.get("type") != "refresh" or not email:
            raise HTTPException(status_code=401, detail="Invalid token type")
        if jti and is_refresh_revoked(str(jti)):
            raise HTTPException(status_code=401, detail="Refresh token revoked")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # rotation: revoke old jti
    if jti:
        revoke_refresh(str(jti))

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token(user.email)
    refresh = create_refresh_token(user.email)
    _set_auth_cookies(response, access, refresh)

    return AuthResponse(
        accessToken=access,
        refreshToken=refresh,
        user=_user_response(user),
    )

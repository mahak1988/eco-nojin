"""Authentication router — JWT in HttpOnly cookies (R4/R5) + optional body tokens."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db
from apps.shared_core.security import cookie_kwargs
from apps.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

ACCESS_COOKIE = settings.JWT_COOKIE_NAME
REFRESH_COOKIE = settings.REFRESH_COOKIE_NAME

ALLOWED_ROLES = {"farmer", "expert", "viewer"}


class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
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
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=40)
    organization: Optional[str] = Field(None, max_length=255)
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
    full_name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
    role: str = "farmer"
    is_active: bool
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshRequest(BaseModel):
    refreshToken: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.ALGORITHM)


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
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.ALGORITHM])
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

    access = create_access_token({"sub": new_user.email})
    refresh = create_refresh_token({"sub": new_user.email})
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

    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})
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
async def logout(response: Response) -> dict[str, str]:
    _clear_auth_cookies(response)
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(
    response: Response,
    request: Request,
    body: Optional[RefreshRequest] = None,
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
        payload = jwt.decode(raw, settings.jwt_secret, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if payload.get("type") != "refresh" or not email:
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    access = create_access_token({"sub": user.email})
    refresh = create_refresh_token({"sub": user.email})
    _set_auth_cookies(response, access, refresh)

    return AuthResponse(
        accessToken=access,
        refreshToken=refresh,
        user=_user_response(user),
    )

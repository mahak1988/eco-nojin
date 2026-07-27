"""Authentication router — login/register/refresh (HS256; RS256 later)."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, model_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db
from apps.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


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
    password: str
    full_name: Optional[str] = None
    role: str = "farmer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool
    is_superuser: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: UserResponse


class RefreshRequest(BaseModel):
    refreshToken: str


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
        role=getattr(user, "role", "user") or "user",
        is_active=bool(getattr(user, "is_active", True)),
        is_superuser=bool(getattr(user, "is_superuser", False)),
        created_at=getattr(user, "created_at", None),
        updated_at=getattr(user, "updated_at", None),
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise credentials_exception
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.ALGORITHM],
        )
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
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
        full_name=request.full_name,
        role=request.role,
        is_active=True,
        is_superuser=False,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return AuthResponse(
        accessToken=create_access_token({"sub": new_user.email}),
        refreshToken=create_refresh_token({"sub": new_user.email}),
        user=_user_response(new_user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    identifier = request.email or request.username
    if not identifier:
        raise HTTPException(status_code=400, detail="Invalid login credentials")

    result = await db.execute(select(User).where(User.email == identifier))
    user = result.scalar_one_or_none()
    stored = getattr(user, "hashed_password", None) if user else None
    if not user or not stored or not verify_password(request.password, stored):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return AuthResponse(
        accessToken=create_access_token({"sub": user.email}),
        refreshToken=create_refresh_token({"sub": user.email}),
        user=_user_response(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return _user_response(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)) -> dict[str, str]:
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)) -> AuthResponse:
    try:
        payload = jwt.decode(
            request.refreshToken,
            settings.jwt_secret,
            algorithms=[settings.ALGORITHM],
        )
        email = payload.get("sub")
        if payload.get("type") != "refresh" or not email:
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return AuthResponse(
        accessToken=create_access_token({"sub": user.email}),
        refreshToken=create_refresh_token({"sub": user.email}),
        user=_user_response(user),
    )

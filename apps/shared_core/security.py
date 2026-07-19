"""
Econojin - Security Module
===========================
Adapted from fastapi/full-stack-fastapi-template with Argon2 + Bcrypt password hashing
and JWT token management. Extended with OTP support for EcoNojin.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from apps.shared_core.config import settings

# ── Password Hashing (Argon2 primary, Bcrypt fallback) ──────────
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=102400,   # 100 MB
    argon2__time_cost=2,
    argon2__parallelism=8,
)

ALGORITHM = settings.ALGORITHM


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        subject: The user ID or identifier to encode in the token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: The password to verify
        hashed_password: The stored hash to verify against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using Argon2 with Bcrypt fallback.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def decode_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        jwt.InvalidTokenError: If token is invalid or expired
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def generate_otp(length: int = 6) -> str:
    """
    Generate a numeric OTP code.
    
    Args:
        length: Number of digits (default: 6)
        
    Returns:
        OTP string
    """
    import random
    return ''.join(str(random.randint(0, 9)) for _ in range(length))
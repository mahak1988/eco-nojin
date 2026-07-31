"""JWT helpers — RS256 when keys present, else HS256 (local)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from apps.shared_core.config import settings
from apps.shared_core.jwt_keys import algorithms, signing_key, verify_key
from apps.shared_core.token_store import remember_refresh

try:
    import bcrypt as _bcrypt

    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return _bcrypt.checkpw(plain.encode("utf-8")[:72], hashed.encode("utf-8"))
        except Exception:
            return False

    def get_password_hash(password: str) -> str:
        return _bcrypt.hashpw(password.encode("utf-8")[:72], _bcrypt.gensalt(rounds=12)).decode()

except Exception:  # pragma: no cover
    from passlib.context import CryptContext

    _ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain: str, hashed: str) -> bool:
        return _ctx.verify(plain, hashed)

    def get_password_hash(password: str) -> str:
        return _ctx.hash(password)


def create_access_token(subject: str | int, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: dict[str, Any] = {"sub": str(subject), "type": "access", "exp": expire}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, signing_key(), algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str | int, jti: str | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_jti = jti or str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": "refresh",
        "exp": expire,
        "jti": token_jti,
    }
    token = jwt.encode(payload, signing_key(), algorithm=settings.ALGORITHM)
    ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600
    remember_refresh(token_jti, ttl)
    return token


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, verify_key(), algorithms=algorithms())


def cookie_kwargs(max_age: int) -> dict[str, Any]:
    return {
        "httponly": True,
        "secure": settings.COOKIE_SECURE or settings.ENVIRONMENT == "production",
        "samesite": settings.COOKIE_SAMESITE,
        "max_age": max_age,
        "path": "/",
    }

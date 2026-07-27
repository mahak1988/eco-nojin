"""Refresh token jti allow/deny list (rotation + revoke)."""

from __future__ import annotations

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)

# process-local fallback
_revoked: dict[str, float] = {}
_active: dict[str, float] = {}


def _redis():
    try:
        from apps.shared_core.config import settings

        import redis

        url = settings.REDIS_URL or ""
        if not url:
            return None
        return redis.from_url(url, decode_responses=True, socket_connect_timeout=0.5)
    except Exception:
        return None


def remember_refresh(jti: str, ttl_seconds: int) -> None:
    exp = time.time() + ttl_seconds
    r = _redis()
    if r:
        try:
            r.setex(f"rt:active:{jti}", ttl_seconds, "1")
            return
        except Exception:
            pass
    _active[jti] = exp


def revoke_refresh(jti: str, ttl_seconds: int = 14 * 24 * 3600) -> None:
    r = _redis()
    if r:
        try:
            r.setex(f"rt:revoked:{jti}", ttl_seconds, "1")
            r.delete(f"rt:active:{jti}")
            return
        except Exception:
            pass
    _revoked[jti] = time.time() + ttl_seconds
    _active.pop(jti, None)


def is_refresh_revoked(jti: str) -> bool:
    r = _redis()
    if r:
        try:
            if r.get(f"rt:revoked:{jti}"):
                return True
            # if we track active and missing, treat as invalid after rotation
            return False
        except Exception:
            pass
    exp = _revoked.get(jti)
    if exp and exp > time.time():
        return True
    return False

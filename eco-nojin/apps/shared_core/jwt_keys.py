"""RS256 / HS256 key material for JWT (R4)."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from apps.shared_core.config import settings

logger = logging.getLogger(__name__)


@lru_cache
def _read_file(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def signing_key() -> Any:
    """Private key for RS256 or shared secret for HS*."""
    algo = (settings.ALGORITHM or "HS256").upper()
    if algo.startswith("RS"):
        path = getattr(settings, "JWT_PRIVATE_KEY_PATH", None)
        pem = getattr(settings, "JWT_PRIVATE_KEY", None)
        if path:
            return _read_file(path)
        if pem:
            return pem.replace("\\n", "\n")
        logger.warning("RS* configured but no private key — falling back to SECRET_KEY")
        return settings.jwt_secret
    return settings.jwt_secret


def verify_key() -> Any:
    algo = (settings.ALGORITHM or "HS256").upper()
    if algo.startswith("RS"):
        path = getattr(settings, "JWT_PUBLIC_KEY_PATH", None)
        pem = getattr(settings, "JWT_PUBLIC_KEY", None)
        if path:
            return _read_file(path)
        if pem:
            return pem.replace("\\n", "\n")
        # try private (jose can derive in some setups) — prefer explicit public
        return signing_key()
    return settings.jwt_secret


def algorithms() -> list[str]:
    return [settings.ALGORITHM or "HS256"]

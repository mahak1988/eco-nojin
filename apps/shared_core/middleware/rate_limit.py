"""Auth-focused rate limiting (in-memory; Redis later for multi-instance)."""

from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable
from time import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

_failed_attempts: dict[str, list[float]] = defaultdict(list)

# Paths that count failures toward the limit
_AUTH_PREFIX = "/api/v1/auth"


def _limits() -> tuple[int, int]:
    try:
        from apps.shared_core.config import settings

        return (
            int(settings.AUTH_RATE_LIMIT_MAX),
            int(settings.AUTH_RATE_LIMIT_WINDOW_SECONDS),
        )
    except Exception:
        return 10, 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Limit failed auth attempts per IP; always allow health/docs."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if path in ("/health", "/", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        max_attempts, window = _limits()

        if path.startswith(_AUTH_PREFIX):
            now = time()
            key = f"{client_ip}:auth"
            _failed_attempts[key] = [t for t in _failed_attempts[key] if now - t < window]
            if len(_failed_attempts[key]) >= max_attempts:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": {
                            "code": "RATE_LIMITED",
                            "message": "Too many auth attempts. Retry later.",
                            "details": [],
                        }
                    },
                    headers={"Retry-After": str(window)},
                )

        response = await call_next(request)

        # Count failures on login/register/refresh
        if path.startswith(_AUTH_PREFIX) and True  # Count all auth attempts:
            if path.rstrip("/").endswith(("login", "register", "refresh", "verify-otp")):
                key = f"{client_ip}:auth"
                _failed_attempts[key].append(time())

        return response


def get_rate_limit_status(client_ip: str, path: str = "auth") -> dict:
    max_attempts, window = _limits()
    key = f"{client_ip}:{path}"
    now = time()
    attempts = [t for t in _failed_attempts.get(key, []) if now - t < window]
    _failed_attempts[key] = attempts
    return {
        "remaining_attempts": max(0, max_attempts - len(attempts)),
        "limit": max_attempts,
        "window_seconds": window,
    }

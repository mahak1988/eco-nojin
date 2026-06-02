import time
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter per IP (layer 2 — abuse protection)."""

    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)

        ip = self._client_ip(request)
        now = time.time()
        window = settings.RATE_LIMIT_WINDOW_SEC
        max_req = settings.RATE_LIMIT_MAX_REQUESTS

        self._hits[ip] = [t for t in self._hits[ip] if now - t < window]
        if len(self._hits[ip]) >= max_req:
            return JSONResponse(
                status_code=429,
                content={"error": "Too Many Requests", "detail": "Rate limit exceeded"},
            )
        self._hits[ip].append(now)
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(max_req)
        response.headers["X-RateLimit-Remaining"] = str(max(0, max_req - len(self._hits[ip])))
        return response

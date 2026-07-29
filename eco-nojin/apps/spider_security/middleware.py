"""SpiderGuard: minimal FastAPI middleware to detect basic crawlers and do simple per-IP rate-limiting.

This implementation is intentionally small and dependency-free so you can review and extend it.
"""
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import time
import re
from collections import defaultdict

BOT_UA_PATTERNS = [
    r"bot",
    r"crawler",
    r"spider",
    r"curl",
    r"wget",
    r"ahrefs",
    r"bingbot",
    r"googlebot",
    r"slurp",
    r"facebot",
    r"ia_archiver",
]


class SpiderGuardMiddleware(BaseHTTPMiddleware):
    """A small middleware that blocks requests with obvious crawler user-agents and
    enforces a simple in-memory rate limit per client IP.

    Notes:
      - In-memory store is for single-instance/dev only. Use Redis or another shared
        store in production for clustered deployments.
      - This is a defensive layer, not a replacement for full WAF/CDN protection.
    """

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60, block_after: bool = True):
        super().__init__(app)
        self.max_requests = int(max_requests)
        self.window = int(window_seconds)
        self.block_after = bool(block_after)
        # Map client_ip -> list[timestamps]
        self._hits = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ua = (request.headers.get("user-agent") or "").lower()
        client = request.client.host if request.client else "unknown"

        # Basic UA heuristics
        for p in BOT_UA_PATTERNS:
            if re.search(p, ua):
                return JSONResponse({"detail": "bot-detected"}, status_code=403)

        now = time.time()
        hits = self._hits[client]
        # Remove timestamps outside the window
        threshold = now - self.window
        while hits and hits[0] <= threshold:
            hits.pop(0)
        hits.append(now)

        if len(hits) > self.max_requests:
            if self.block_after:
                return JSONResponse({"detail": "rate-limited"}, status_code=429)

        response = await call_next(request)
        # Observability header
        response.headers["X-SpiderGuard-Checked"] = "1"
        return response

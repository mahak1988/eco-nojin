"""SpiderGuard: bot UA heuristics + simple per-IP rate limit.

Does NOT treat curl/wget/httpie as bots (API clients / CI).
"""

from __future__ import annotations

import re
import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# Real crawlers only — not developer tools
BOT_UA_PATTERNS = [
    r"googlebot",
    r"bingbot",
    r"yandexbot",
    r"baiduspider",
    r"duckduckbot",
    r"slurp",
    r"facebot",
    r"ia_archiver",
    r"semrushbot",
    r"ahrefsbot",
    r"dotbot",
    r"mj12bot",
    r"petalbot",
]


class SpiderGuardMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        max_requests: int = 120,
        window_seconds: int = 60,
        block_after: bool = True,
    ):
        super().__init__(app)
        self.max_requests = int(max_requests)
        self.window = int(window_seconds)
        self.block_after = bool(block_after)
        self._hits: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        path = request.url.path
        if path in ("/health", "/", "/docs", "/redoc", "/openapi.json"):
            return await call_next(request)

        ua = (request.headers.get("user-agent") or "").lower()
        client = request.client.host if request.client else "unknown"

        for p in BOT_UA_PATTERNS:
            if re.search(p, ua):
                return JSONResponse({"detail": "bot-detected"}, status_code=403)

        now = time.time()
        hits = self._hits[client]
        threshold = now - self.window
        while hits and hits[0] <= threshold:
            hits.pop(0)
        hits.append(now)

        if len(hits) > self.max_requests and self.block_after:
            return JSONResponse({"detail": "rate-limited"}, status_code=429)

        response = await call_next(request)
        response.headers["X-SpiderGuard-Checked"] = "1"
        return response

"""SpiderGuard: bot UA heuristics + simple per-IP rate limit.

Does NOT treat curl/wget/httpie as bots (API clients / CI).
"""

from __future__ import annotations

import re
import time
from collections import defaultdict
from collections.abc import Callable

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

# Enhanced attack pattern detection
SQL_INJECTION_PATTERNS = [
    "union select", "or 1=1", "'; drop", "'; insert", "'; update", "'; delete",
    "exec(", "execute(", "sp_", "xp_", "information_schema", "sysobjects",
    "0x", "char(", "concat(", "group_concat", "load_file", "into outfile",
]

XSS_PATTERNS = [
    "<script", "javascript:", "onerror=", "onload=", "onclick=", "onmouseover=",
    "<iframe", "<object", "<embed", "<svg onload", "alert(", "prompt(",
    "document.cookie", "document.write", "eval(", "expression(",
]

PATH_TRAVERSAL_PATTERNS = [
    "../", "..\\", "..%2f", "..%5c", "%2e%2e/", "%2e%2e\\",
    "/etc/passwd", "/etc/shadow", "/proc/self", "c:\\windows\\",
    "....//", "..../\\",
]

SSRF_PATTERNS = [
    "169.254.169.254", "metadata.google.internal", "localhost", "127.0.0.1",
    "0.0.0.0", "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
    "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.", "172.27.",
    "172.28.", "172.29.", "172.30.", "172.31.", "192.168.", "fd", "fc",
]

COMMAND_INJECTION_PATTERNS = [
    "; cat ", "| cat ", "; ls ", "| ls ", "; wget ", "| wget ",
    "; curl ", "| curl ", "; bash ", "| bash ", "; sh ", "| sh ",
    "$(", "`", "; nc ", "| nc ", "; python ", "| python ",
]

BLOCKED_PATTERNS = SQL_INJECTION_PATTERNS + XSS_PATTERNS + PATH_TRAVERSAL_PATTERNS + SSRF_PATTERNS + COMMAND_INJECTION_PATTERNS


def detect_attack_pattern(url_path: str, query_string: str, headers: dict) -> str | None:
    """Detect attack patterns in request. Returns attack type if found."""
    combined = f"{url_path}?{query_string}".lower()
    
    # Check URL and query for SQL injection
    for pattern in SQL_INJECTION_PATTERNS:
        if pattern in combined:
            return f"SQL_INJECTION: {pattern}"
    
    # Check for XSS
    for pattern in XSS_PATTERNS:
        if pattern in combined:
            return f"XSS: {pattern}"
    
    # Check for path traversal
    for pattern in PATH_TRAVERSAL_PATTERNS:
        if pattern in combined:
            return f"PATH_TRAVERSAL: {pattern}"
    
    # Check for SSRF in headers
    user_agent = headers.get("user-agent", "").lower()
    referer = headers.get("referer", "").lower()
    for pattern in SSRF_PATTERNS:
        if pattern in referer:
            return f"SSRF: {pattern}"
    
    # Check for command injection
    for pattern in COMMAND_INJECTION_PATTERNS:
        if pattern in combined:
            return f"COMMAND_INJECTION: {pattern}"
    
    return None
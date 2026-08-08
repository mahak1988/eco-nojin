"""Spider Web Security - FastAPI Security Middleware (Layers 3-4)."""

from __future__ import annotations

import os
import re
import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

CONFIG = {
    "rate_limit_per_minute": 120,
    "rate_limit_login_per_minute": 30,  # was 5 — too strict for FE hydrate + retries
    "max_request_size": 10 * 1024 * 1024,
    "blocked_agents": [
        "sqlmap",
        "nikto",
        "nmap",
        "masscan",
        "dirbuster",
        "gobuster",
        "wfuzz",
        "hydra",
        "burp",
        "zap",
        "scrapy",
    ],
    "suspicious_patterns": [
        r"(?i)(union\s+select|insert\s+into|drop\s+table|delete\s+from)",
        r"(?i)(<script|javascript:|vbscript:|on\w+\s*=)",
        r"(?i)(\.\./|\.\.\\|%2e%2e)",
        r"(?i)(cmd\.exe|/bin/sh|/bin/bash|powershell)",
    ],
    "security_headers": {
        "X-Frame-Options": "SAMEORIGIN",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Cache-Control": "no-store, no-cache, must-revalidate",
    },
}


class RateLimiter:
    def __init__(self) -> None:
        self._req: dict[str, list[float]] = defaultdict(list)

    def allowed(self, key: str, limit: int, window: int = 60) -> bool:
        now = time.time()
        self._req[key] = [t for t in self._req[key] if now - t < window]
        if len(self._req[key]) >= limit:
            return False
        self._req[key].append(now)
        return True


def _is_local() -> bool:
    return (os.getenv("ENVIRONMENT") or os.getenv("APP_ENV") or "local").lower() in {
        "local",
        "dev",
        "development",
        "test",
    }


class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, config=None):
        super().__init__(app)
        self.cfg = config or CONFIG
        self.rl = RateLimiter()
        self._patterns = [re.compile(p) for p in self.cfg["suspicious_patterns"]]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        ip = request.client.host if request.client else "unknown"
        ua = (request.headers.get("user-agent") or "").lower()
        if not ua:
            return JSONResponse(status_code=403, content={"detail": "User-Agent required"})
        for b in self.cfg["blocked_agents"]:
            if b in ua:
                return JSONResponse(status_code=403, content={"detail": "Access denied"})

        path = request.url.path
        method = request.method.upper()

        # Rate-limit only sensitive auth *writes* (not GET /auth/me)
        is_auth_write = method in {"POST", "PUT", "PATCH"} and (
            path.endswith("/auth/login")
            or path.endswith("/auth/register")
            or path.endswith("/login")
            or path.endswith("/register")
        )

        if not _is_local():
            limit = (
                self.cfg["rate_limit_login_per_minute"]
                if is_auth_write
                else self.cfg["rate_limit_per_minute"]
            )
            key = f"{ip}:auth" if is_auth_write else ip
            if not self.rl.allowed(key, limit):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"},
                    headers={"Retry-After": "60"},
                )
        else:
            # Local: soft limit only on auth writes
            if is_auth_write and not self.rl.allowed(f"{ip}:auth", 60):
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"},
                    headers={"Retry-After": "30"},
                )

        cl = request.headers.get("content-length")
        if cl and int(cl) > self.cfg["max_request_size"]:
            return JSONResponse(status_code=413, content={"detail": "Request too large"})

        check = f"{request.url.path}?{request.query_params}"
        for pat in self._patterns:
            if pat.search(check):
                return JSONResponse(status_code=403, content={"detail": "Suspicious request"})

        response = await call_next(request)
        for h, v in self.cfg["security_headers"].items():
            response.headers[h] = v
        if "server" in response.headers:
            del response.headers["server"]
        return response

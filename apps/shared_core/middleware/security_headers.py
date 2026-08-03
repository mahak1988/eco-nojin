"""Helmet-like security headers middleware for FastAPI.

Adds security-related HTTP response headers and removes server fingerprinting.
Inspired by Helmet.js (Express) but implemented as pure ASGI middleware.
"""

from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


_STRICT_CSP = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "connect-src 'self' https:; "
    "frame-ancestors 'self'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "object-src 'none'; "
    "upgrade-insecure-requests; "
)

PRODUCTION_HEADERS = {
    "Content-Security-Policy": _STRICT_CSP,
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
    "Pragma": "no-cache",
    "X-DNS-Prefetch-Control": "off",
    "Permissions-Policy": (
        "camera=(), "
        "microphone=(), "
        "geolocation=(self), "
        "payment=(), "
        "usb=(), "
        "magnetometer=(), "
        "gyroscope=()"
    ),
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
}

DEVELOPMENT_HEADERS = {
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' http: https: ws: wss:; frame-ancestors 'self'",
    "X-Frame-Options": "SAMEORIGIN",
    "X-Content-Type-Options": "nosniff",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-DNS-Prefetch-Control": "off",
}

_CACHEABLE_PREFIXES = (
    "/static/",
    "/assets/",
    "/favicon.ico",
    "/robots.txt",
    "/manifest.json",
    "/sw.js",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add Helmet-like security headers to every response."""

    def __init__(self, app, environment: str = "production") -> None:
        super().__init__(app)
        self.environment = environment
        self.headers = (
            PRODUCTION_HEADERS if environment == "production" else DEVELOPMENT_HEADERS
        )

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        path = request.url.path

        for header_name, header_value in self.headers.items():
            if header_name == "Cache-Control" and any(
                path.startswith(p) for p in _CACHEABLE_PREFIXES
            ):
                continue
            if header_name == "Strict-Transport-Security" and request.url.scheme != "https":
                continue
            if header_name not in response.headers:
                response.headers[header_name] = header_value

        # Strip server fingerprint headers
        for h in ("server", "X-Powered-By", "X-AspNet-Version"):
            if h in response.headers:
                del response.headers[h]

        return response

"""
Rate Limiting Middleware
=========================
Prevents brute force attacks on authentication endpoints.
Uses in-memory store by default, Redis for production.
"""

from time import time
from collections import defaultdict
from typing import Callable

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# In-memory store (for production use Redis)
_failed_attempts: dict[str, list[float]] = defaultdict(list)

# Configuration
RATE_LIMIT_WINDOW_SECONDS = 60  # Time window in seconds
MAX_FAILED_ATTEMPTS = 5  # Max failed attempts before rate limiting
RATE_LIMIT_PATHS = ["/api/v1/auth/login", "/api/v1/auth/otp/request"]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent brute force attacks.
    
    Tracks failed authentication attempts and blocks IPs that exceed
    the maximum number of attempts within the time window.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path
        
        # Only apply to authentication endpoints
        if path in RATE_LIMIT_PATHS or path.startswith("/api/v1/auth"):
            now = time()
            key = f"{client_ip}:{path}"
            attempts = _failed_attempts[key]
            
            # Clean up old attempts outside the window
            _failed_attempts[key] = [
                attempt_time for attempt_time in attempts 
                if now - attempt_time < RATE_LIMIT_WINDOW_SECONDS
            ]
            
            # Check if rate limited
            if len(_failed_attempts[key]) >= MAX_FAILED_ATTEMPTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many failed attempts. Please try again later.",
                    headers={"Retry-After": str(RATE_LIMIT_WINDOW_SECONDS)},
                )
        
        response = await call_next(request)
        
        # Record failed authentication attempts
        if path in RATE_LIMIT_PATHS and response.status_code == 401:
            key = f"{client_ip}:{path}"
            _failed_attempts[key].append(time())
        
        return response


def get_rate_limit_status(client_ip: str, path: str) -> dict:
    """
    Get current rate limit status for debugging.
    
    Args:
        client_ip: Client IP address
        path: Request path
        
    Returns:
        Dictionary with remaining attempts and reset time
    """
    key = f"{client_ip}:{path}"
    attempts = _failed_attempts.get(key, [])
    now = time()
    
    # Clean up
    _failed_attempts[key] = [
        t for t in attempts if now - t < RATE_LIMIT_WINDOW_SECONDS
    ]
    
    return {
        "remaining_attempts": max(0, MAX_FAILED_ATTEMPTS - len(attempts)),
        "limit": MAX_FAILED_ATTEMPTS,
        "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
        "reset_in_seconds": RATE_LIMIT_WINDOW_SECONDS - (now - min(attempts)) if attempts else RATE_LIMIT_WINDOW_SECONDS,
    }
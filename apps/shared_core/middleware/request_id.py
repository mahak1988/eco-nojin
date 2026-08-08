"""
X-Request-ID Middleware
=======================
Phase 0: Adds unique request ID to every request for tracing.
"""

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("econojin.request_id")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generate or propagate X-Request-ID for every request."""

    async def dispatch(self, request: Request, call_next):
        # Propagate if client sent one, otherwise generate
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
        request.state.request_id = request_id

        response: Response = await call_next(request)

        # Set header on response
        response.headers[REQUEST_ID_HEADER] = request_id
        return response

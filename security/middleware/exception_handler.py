
"""OWASP A10:2025 — Mishandling of Exceptional Conditions."""
from __future__ import annotations
import logging
import traceback
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("security.exceptions")

async def security_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """جلوگیری از نشت اطلاعات در خطاها."""
    # لاگ کامل برای تیم توسعه
    logger.error(
        "Unhandled exception: %s %s\n%s",
        request.method, request.url.path,
        traceback.format_exc(),
        extra={"ip": request.client.host if request.client else "unknown"},
    )
    # پاسخ امن به کاربر (بدون stack trace)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "server_error",
        },
        headers={"X-Content-Type-Options": "nosniff"},
    )

async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """مدیریت امن خطاهای validation."""
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "type": "validation_error"},
    )

async def not_found_handler(request: Request, exc) -> JSONResponse:
    """جلوگیری از نشت اطلاعات مسیر."""
    return JSONResponse(
        status_code=404,
        content={"detail": "Not found"},
    )

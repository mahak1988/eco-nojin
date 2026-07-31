
"""OWASP A10:2025 — Mishandling of Exceptional Conditions."""
from __future__ import annotations

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("security.exceptions")

async def security_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """جلوگیری از نشت اطلاعات در خطاها."""
    # لاگ خطا برای استفاده تیم توسعه
    logger.error("API Error: %s - Path: %s - Method: %s", str(exc), request.url.path, request.method)

    # پاسخ عمومی بدون جزئیات حساس
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
            }
        },
    )

async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    """مدیریت امن خطاهای validation."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
            }
        },
    )

async def not_found_handler(request: Request, exc) -> JSONResponse:
    """جلوگیری از نشت اطلاعات مسیر."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": "Resource not found",
            }
        },
    )

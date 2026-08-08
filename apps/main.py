#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Econojin API entrypoint."""

from __future__ import annotations

import logging
import os
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import core security components
from apps.shared_core.security_init import (
    initialize_security,
    apply_response_security_headers,
    authenticate_request,
)
from apps.shared_core.config import settings

# Import security middlewares
from apps.shared_core.middleware.rate_limit import RateLimitMiddleware
from apps.spider_security.middleware import SpiderGuardMiddleware
from apps.shared_core.middleware.audit_log import AuditLogMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("econojin")

_db_status = {"ok": False, "detail": "not_initialized"}
_OPTIONAL_MODULE_HINTS = ("numba", "psycopg2", "langchain")
_loaded_routers: list[str] = []
_failed_routers: list[dict[str, str]] = []
_security_stack: list[str] = []


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Econojin API v%s starting (%s)", settings.VERSION, settings.ENVIRONMENT)
    logger.info("PROJECT_ROOT=%s", PROJECT_ROOT)
    logger.info("Security stack: %s", _security_stack)
    start_time = time.time()
    try:
        from apps.shared_core.database.session import init_db

        await init_db()
        _db_status["ok"] = True
        _db_status["detail"] = "ok"
        logger.info("Database initialized")
    except Exception as e:
        _db_status["ok"] = False
        _db_status["detail"] = str(e)[:200]
        logger.warning("init_db failed: %s", e)
    try:
        from apps.shared_core.database.session import get_engine
        from apps.shared_core.geo.postgis import ensure_farms_spatial, ensure_postgis

        eng = get_engine()
        await ensure_postgis(eng)
        spatial = await ensure_farms_spatial(eng)
        if spatial.get("ok"):
            logger.info("Farms spatial index: %s", spatial.get("steps"))
    except Exception as e:
        logger.debug("PostGIS skip: %s", e)
    try:
        from apps.ml.service import get_bundle

        get_bundle()
        logger.info("ML models ready")
    except Exception as e:
        logger.debug("ML warmup skip: %s", e)
    try:
        from apps.shared_ai.ai.llm_factory import LLMFactory  # noqa: F401

        logger.info("AI module loaded (provider: %s)", settings.LLM_PROVIDER)
    except Exception as e:
        logger.debug("AI module unavailable: %s", e)
    try:
        from apps.shared_core.monitoring.sentry import init_sentry

        init_sentry(app)
        logger.info("Sentry initialized")
    except Exception as e:
        logger.debug("Sentry unavailable: %s", e)
    try:
        from apps.admin_panel.integrations.cms import init_cms_service_from_env

        init_cms_service_from_env()
        logger.info("CMS integration client ready")
    except Exception as e:
        logger.debug("CMS integration skip: %s", e)
    logger.info(
        "Routers loaded=%s failed=%s",
        len(_loaded_routers),
        [f["label"] for f in _failed_routers],
    )
    logger.info("Startup complete in %.2fs", time.time() - start_time)
    yield
    try:
        from apps.shared_core.database.session import close_db

        await close_db()
    except Exception as e:
        logger.debug("close_db failed: %s", e)


_docs = "/docs" if settings.ENVIRONMENT != "production" else None
_redoc = "/redoc" if settings.ENVIRONMENT != "production" else None

# Create FastAPI instance with minimal initial setup
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agriculture, water, environment and economy platform",
    version=settings.VERSION,
    lifespan=lifespan,
    # Disable docs in production for security
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
)

_security_stack.extend(initialize_security(app))

_cors_origins = list(settings.all_cors_origins)
for extra in (
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
):
    if extra not in _cors_origins:
        _cors_origins.append(extra)

# Apply security middlewares in the correct order
# 1. Audit Log - logs all requests
if settings.ENABLE_AUDIT_LOG:
    app.add_middleware(AuditLogMiddleware)
    logger.info("AuditLog middleware enabled.")

# 2. Rate Limiting - prevents abuse
if settings.ENABLE_RATE_LIMIT:
    app.add_middleware(RateLimitMiddleware)
    logger.info("RateLimit middleware enabled.")

# 3. SpiderGuard - protects against bots
if settings.ENABLE_SPIDERGUARD:
    app.add_middleware(SpiderGuardMiddleware)
    logger.info("SpiderGuard middleware enabled.")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "X-Request-ID",
    ],
    expose_headers=["X-Total-Count", "X-Page-Count", "X-Request-ID", "X-Process-Time"],
    max_age=600,
)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if request.method == "OPTIONS":
        return await call_next(request)

    if not authenticate_request(request):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Authentication required"},
        )

    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.time() - start_time:.4f}"
    apply_response_security_headers(response.headers)
    return response


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred.",
                "details": [],
                "request_id": _request_id(request),
            }
        },
    )


@app.exception_handler(429)
def ratelimit_handler(request: Request, exc):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded"},
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": {
                "code": "NOT_FOUND",
                "message": f"Path {request.url.path} was not found",
                "details": [],
                "request_id": _request_id(request),
            }
        },
    )
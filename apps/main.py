#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Econojin API entrypoint."""

from security.middleware.security_middleware import SecurityMiddleware
from apps.shared_core.middleware.request_id import RequestIDMiddleware
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("econojin")

from apps.shared_core.config import settings

_db_status = {"ok": False, "detail": "not_initialized"}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Econojin API v%s starting (%s)", settings.VERSION, settings.ENVIRONMENT)
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
        from apps.shared_ai.ai.llm_factory import LLMFactory  # noqa: F401

        logger.info("AI module loaded (provider: %s)", settings.LLM_PROVIDER)
    except Exception as e:
        logger.warning("AI module unavailable: %s", e)

    try:
        from apps.shared_core.monitoring.sentry import init_sentry

        init_sentry(app)
        logger.info("Sentry initialized")
    except Exception as e:
        logger.warning("Sentry unavailable: %s", e)

    logger.info("Startup complete in %.2fs", time.time() - start_time)
    yield

    try:
        from apps.shared_core.database.session import close_db

        await close_db()
    except Exception as e:
        logger.warning("close_db failed: %s", e)


_docs = "/docs" if settings.ENVIRONMENT != "production" else None
_redoc = "/redoc" if settings.ENVIRONMENT != "production" else None

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agriculture, water, environment and economy platform",
    version=settings.VERSION,
    docs_url=_docs,
    redoc_url=_redoc,
    lifespan=lifespan,
)

app.add_middleware(SecurityMiddleware)
app.add_middleware(RequestIDMiddleware)

if settings.ENVIRONMENT != "local":
    try:
        from apps.shared_core.middleware.rate_limit import RateLimitMiddleware
        from apps.shared_core.middleware.audit_log import AuditLogMiddleware

        app.add_middleware(RateLimitMiddleware)
        app.add_middleware(AuditLogMiddleware)
    except Exception as e:
        logger.warning("Security middleware failed: %s", e)

# Broad local CORS so Vite (any port) works
_cors = list(settings.all_cors_origins)
for extra in ("http://127.0.0.1:5173", "http://localhost:4173", "http://127.0.0.1:4173"):
    if extra not in _cors:
        _cors.append(extra)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors if settings.ENVIRONMENT == "production" else ["*"] if settings.ENVIRONMENT == "local" else _cors,
    allow_credentials=settings.ENVIRONMENT != "local",
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page-Count", "X-Request-ID", "X-Process-Time"],
    max_age=600,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    start_time = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time"] = f"{time.time() - start_time:.4f}"
    return response


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None) or request.headers.get("x-request-id")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An internal error occurred.",
            "request_id": _request_id(request),
        },
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "Not Found",
            "message": f"Path {request.url.path} was not found",
            "request_id": _request_id(request),
        },
    )


def _include(label: str, loader: Any, **kwargs: Any) -> None:
    try:
        router = loader()
        app.include_router(router, **kwargs)
        logger.info("%s: router loaded", label)
    except Exception as e:
        logger.warning("%s: %s", label, e)


_include("users", lambda: __import__("apps.users.router", fromlist=["router"]).router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"])
_include("auth", lambda: __import__("apps.users.auth_router", fromlist=["router"]).router, prefix=settings.API_V1_STR, tags=["Authentication"])
_include("ai_agents", lambda: __import__("apps.ai_agents.router", fromlist=["router"]).router, prefix=f"{settings.API_V1_STR}/ai-agents", tags=["AI Agents"])
_include("accounting", lambda: __import__("apps.api.routes.accounting", fromlist=["router"]).router)
_include("ecocoin", lambda: __import__("apps.api.routes.ecocoin", fromlist=["router"]).router)
_include("monitoring", lambda: __import__("apps.api.routes.monitoring", fromlist=["router"]).router)
_include("simulator", lambda: __import__("apps.api.routes.simulator", fromlist=["router"]).router)
_include("admin_panel", lambda: __import__("apps.admin_panel.router", fromlist=["router"]).router, prefix=settings.API_V1_STR, tags=["Admin"])
_include("simulation", lambda: __import__("apps.simulation.router", fromlist=["router"]).router, prefix=f"{settings.API_V1_STR}/simulation", tags=["Simulation"])
_include("data", lambda: __import__("apps.simulation.data.router", fromlist=["router"]).router)
_include("advisory", lambda: __import__("apps.simulation.advisory.router", fromlist=["router"]).router)
_include("runs", lambda: __import__("apps.simulation.runs.router", fromlist=["router"]).router)
_include("scenario", lambda: __import__("apps.simulation.scenario.router", fromlist=["router"]).router)
_include("validation", lambda: __import__("apps.simulation.validation.router", fromlist=["router"]).router)
_include("agriculture_schools", lambda: __import__("apps.api.routes.agriculture_schools", fromlist=["router"]).router)
_include("education", lambda: __import__("apps.api.routes.education", fromlist=["router"]).router)
_include("community", lambda: __import__("apps.api.routes.community", fromlist=["router"]).router)
_include("games", lambda: __import__("apps.api.routes.games", fromlist=["router"]).router)
_include("chain", lambda: __import__("apps.simulation.chain.router", fromlist=["router"]).router)
_include("reports", lambda: __import__("apps.simulation.reports.router", fromlist=["router"]).router)


@app.get("/", tags=["Root"])
async def root() -> dict[str, Any]:
    return {
        "name": settings.PROJECT_NAME,
        "status": "running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": _docs,
    }


@app.get("/health", tags=["Health"])
async def health() -> dict[str, Any]:
    db_live = False
    db_detail = _db_status.get("detail", "unknown")
    try:
        from apps.shared_core.database.session import get_engine

        eng = get_engine()
        async with eng.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_live = True
        db_detail = "ok"
    except Exception as e:
        db_live = False
        db_detail = str(e)[:200]

    return {
        "status": "healthy" if db_live else "degraded",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "ok" if db_live else "fail",
        "database_detail": db_detail,
    }


@app.get("/modules", tags=["Modules"])
async def list_modules() -> dict[str, Any]:
    modules = [
        "users", "auth", "ai_agents", "accounting", "ecocoin",
        "monitoring", "simulator", "admin_panel", "simulation",
        "agriculture_schools", "education", "community", "games", "chain", "reports",
    ]
    return {"modules": modules, "total": len(modules)}


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = settings.ENVIRONMENT == "local"
    uvicorn.run("apps.main:app", host=host, port=port, reload=reload, log_level="info", access_log=True)

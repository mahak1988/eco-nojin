#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Econojin Backend - FastAPI Entry Point"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.core.config import settings
from api.core.database import init_db
from api.core.middleware import SecurityHeadersMiddleware, RateLimitMiddleware
from api.agents.orchestrator import EconojinOrchestrator

from api.modules.weather.router import router as weather_router
from api.modules.accounting.router import router as accounting_router
from api.modules.gis.router import router as gis_router
from api.modules.calendar.router import router as calendar_router
from api.modules.store.router import router as store_router
from api.modules.library.router import router as library_router
from api.modules.desktop.router import router as desktop_router
from api.modules.education.router import router as education_router
from api.modules.psychology.router import router as psychology_router
from api.modules.ecomining.router import router as ecomining_router
from api.modules.community.router import router as community_router
from api.modules.games.router import router as games_router
from api.modules.settings.router import router as settings_router
from api.modules.auth.router import router as auth_router
from api.modules.farmer.router import router as farmer_router
from api.modules.dashboard.router import router as dashboard_router
from api.modules.simulation.router import router as simulation_router
from api.modules.ai.router import router as ai_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    await init_db()
    app.state.orchestrator = EconojinOrchestrator()
    print(f"Ready on http://{settings.HOST}:{settings.PORT}")
    yield
    print("Shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Econojin platform API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Econojin",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running",
    }


@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "modules": [
            "weather",
            "accounting",
            "gis",
            "calendar",
            "auth",
            "farmer",
            "education",
            "psychology",
            "ecomining",
            "community",
            "games",
            "settings",
        ],
    }


@app.get("/api/v1/modules")
async def list_modules():
    modules = [
        "weather",
        "accounting",
        "gis",
        "calendar",
        "auth",
        "farmer",
        "education",
        "psychology",
        "ecomining",
        "community",
        "games",
        "settings",
        "store",
        "library",
        "desktop",
    ]
    return {"modules": [{"id": m, "name": m, "status": "active"} for m in modules]}


@app.exception_handler(Exception)
async def global_error(request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Server Error",
            "detail": str(exc) if settings.DEBUG else "Try later",
        },
    )


app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(simulation_router, prefix="/api/v1/simulation", tags=["Simulation"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(farmer_router, prefix="/api/v1/farmers", tags=["Farmers"])
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])
app.include_router(accounting_router, prefix="/api/v1/accounting", tags=["Accounting"])
app.include_router(gis_router, prefix="/api/v1/gis", tags=["GIS"])
app.include_router(calendar_router, prefix="/api/v1/calendar", tags=["Calendar"])
app.include_router(store_router, prefix="/api/v1/store", tags=["Store"])
app.include_router(library_router, prefix="/api/v1/library", tags=["Library"])
app.include_router(desktop_router, prefix="/api/v1/desktop", tags=["Desktop"])
app.include_router(education_router, prefix="/api/v1/education", tags=["Education"])
app.include_router(psychology_router, prefix="/api/v1/psychology", tags=["Psychology"])
app.include_router(ecomining_router, prefix="/api/v1/ecomining", tags=["EcoCoin"])
app.include_router(community_router, prefix="/api/v1/community", tags=["Community"])
app.include_router(games_router, prefix="/api/v1/games", tags=["Games"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)

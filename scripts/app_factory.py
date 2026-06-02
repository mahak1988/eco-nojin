"""
Application factory for Economugin API.

This file is introduced to support a Clean-Architecture-like layout
and versioned routing without breaking existing endpoints.
"""

from fastapi import FastAPI

from scripts.api.routers.auth import router as auth_router
from scripts.api.routers.farmer import router as farmer_router


def create_app() -> FastAPI:
    app = FastAPI(title="Economugin API", version="1.0.0", docs_url="/docs")

    # Keep existing core endpoints from scripts/api/main.py in this phase.
    # Versioned routers (api/v1) will be added in a subsequent step.
    app.include_router(auth_router)
    app.include_router(farmer_router, prefix="/farmer")

    return app

"""API V1 Router"""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, modules, health,
    projects, data_points, kpis,
    models, scientific_models
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(data_points.router, prefix="/data-points", tags=["DataPoints"])
api_router.include_router(kpis.router, prefix="/kpis", tags=["KPIs"])
api_router.include_router(models.router, prefix="/models", tags=["Scientific Models"])
api_router.include_router(scientific_models.router, prefix="/scientific-models", tags=["Scientific Models Management"])
api_router.include_router(modules.router, prefix="/modules", tags=["Modules"])

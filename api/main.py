"""
Econojin API - Main Application
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings, validate_settings

# Import routers
from api.modules.auth.router import router as auth_router
from api.modules.farmer.router import router as farmer_router
from api.modules.ecocoin.router import router as ecocoin_router
from api.modules.ecomining.router import router as ecomining_router
from api.modules.dashboard.router import router as dashboard_router
from api.modules.desktop.router import router as desktop_router
from api.modules.weather.router import router as weather_router
from api.modules.drought.router import router as drought_router
from api.modules.soil_water.router import router as soil_water_router
from api.modules.mrv.router import router as mrv_router
from api.modules.iot.router import router as iot_router
from api.modules.store.router import router as store_router
from api.modules.financial.router import router as financial_router
from api.modules.accounting.router import router as accounting_router
from api.modules.academy.router import router as academy_router
from api.modules.education.router import router as education_router
from api.modules.library.router import router as library_router
from api.modules.community.router import router as community_router
from api.modules.newsletter.router import router as newsletter_router
from api.modules.psychology.router import router as psychology_router
from api.modules.games.router import router as games_router
from api.modules.maintenance.router import router as maintenance_router
from api.modules.simulation.router import router as simulation_router
from api.modules.ai.router import router as ai_router
from api.scientific_core.router import router as scientific_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events - with error handling"""
    print("🚀 Starting Econojin v2.0.0...")
    
    # Validate settings
    try:
        validate_settings()
    except Exception as e:
        print(f"⚠️  Settings validation error: {e}")
    
    # Initialize database
    try:
        from api.core.database import init_db
        await init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        import traceback
        traceback.print_exc()
    
    # Start Early Warning Engine (optional)
    try:
        from api.services.early_warning_engine import ews_engine
        import asyncio
        asyncio.create_task(ews_engine.start())
        print("✅ Early Warning Engine started")
    except Exception as e:
        print(f"⚠️  EWS skipped: {e}")
    
    print("✅ Ready on http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    
    yield
    
    print("🛑 Shutting down...")


app = FastAPI(
    title="Econojin API",
    description="Econojin Platform API",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "name": "Econojin API",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "version": "2.0.0"}


# Register all routers
ROUTERS = [
    (auth_router, "/api/v1"),
    (farmer_router, "/api/v1/farmers"),
    (ecocoin_router, "/api/v1"),
    (ecomining_router, "/api/v1"),
    (dashboard_router, "/api/v1"),
    (desktop_router, "/api/v1"),
    (weather_router, "/api/v1"),
    (drought_router, "/api/v1"),
    (soil_water_router, "/api/v1"),
    (mrv_router, "/api/v1"),
    (iot_router, "/api/v1"),
    (scientific_router, "/api/v1"),
    (store_router, "/api/v1"),
    (financial_router, "/api/v1"),
    (accounting_router, "/api/v1"),
    (academy_router, "/api/v1"),
    (education_router, "/api/v1"),
    (library_router, "/api/v1"),
    (community_router, "/api/v1"),
    (newsletter_router, "/api/v1"),
    (psychology_router, "/api/v1"),
    (games_router, "/api/v1"),
    (maintenance_router, "/api/v1"),
    (simulation_router, "/api/v1"),
    (ai_router, "/api/v1"),
]

for router_instance, prefix in ROUTERS:
    app.include_router(router_instance, prefix=prefix)

print(f"✅ All {len(ROUTERS)} routers registered")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

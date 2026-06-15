"""
Econojin Platform - Main FastAPI Application
Integrated Landscape Management across 12 global pilots
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ========================================================================
# Create FastAPI app
# ========================================================================
app = FastAPI(
    title="Econojin Platform",
    description="Integrated Landscape Management Platform - Hydroma Nojin",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ========================================================================
# CORS Middleware
# ========================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================================================================
# Import Domain Routers
# ========================================================================
try:
    # Core domains (always available)
    from api.domains.drought.routers.drought_router import router as drought_router
    from api.domains.soil_water.routers.soil_water_router import router as soil_water_router
    from api.domains.financial.routers.financial_router import router as financial_router
    
    # Extended domains (may be added progressively)
    from api.domains.psychology.routers.psychology_router import router as psychology_router
    from api.domains.iot.routers.iot_router import router as iot_router
    from api.domains.hydrology.routers.hydrology_router import router as hydrology_router
    from api.domains.dashboard.routers.dashboard_router import router as dashboard_router
    from api.domains.training.routers.training_router import router as training_router
    from api.domains.remote_sensing.routers.remote_sensing_router import router as remote_sensing_router
    from api.domains.mrv.routers.mrv_router import router as mrv_router
    from api.domains.safeguards.routers.safeguards_router import router as safeguards_router
    from api.domains.pilots.routers.pilot_router import router as pilots_router
    from api.domains.logframe.routers.logframe_router import router as logframe_router
    
    # Register all routers
    app.include_router(drought_router, prefix="/api/drought", tags=["Drought"])
    app.include_router(soil_water_router, prefix="/api/soil-water", tags=["Soil & Water"])
    app.include_router(financial_router, prefix="/api/financial", tags=["Financial"])
    app.include_router(psychology_router, prefix="/api/psychology", tags=["Psychology"])
    app.include_router(iot_router, prefix="/api/iot", tags=["IoT"])
    app.include_router(hydrology_router, prefix="/api/hydrology", tags=["Hydrology"])
    app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
    app.include_router(training_router, prefix="/api/training", tags=["Training"])
    app.include_router(remote_sensing_router, prefix="/api/remote-sensing", tags=["Remote Sensing"])
    app.include_router(mrv_router, prefix="/api/mrv", tags=["MRV"])
    app.include_router(safeguards_router, prefix="/api/safeguards", tags=["Safeguards"])
    app.include_router(pilots_router, prefix="/api/pilots", tags=["Pilots"])
    app.include_router(logframe_router, prefix="/api/logframe", tags=["LogFrame"])
    
    print("✅ All domain routers registered successfully")
    
except ImportError as e:
    print(f"⚠️  Some routers could not be imported: {e}")
    print("   Continuing with available routers...")

# ========================================================================
# Gateway Router (if available)
# ========================================================================
try:
    from api.gateway.api_gateway import router as gateway_router
    app.include_router(gateway_router, prefix="/gateway", tags=["Gateway"])
    print("✅ Gateway router registered")
except ImportError:
    print("⚠️  Gateway router not available")

# ========================================================================
# Root Endpoints
# ========================================================================
@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Econojin Platform - Hydroma Nojin",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "platform": "Econojin",
        "version": "1.0.0"
    }


@app.get("/api/info")
def api_info():
    """API information"""
    return {
        "name": "Econojin Platform API",
        "version": "1.0.0",
        "description": "Integrated Landscape Management Platform",
        "domains": [
            "drought",
            "soil_water",
            "financial",
            "psychology",
            "iot",
            "hydrology",
            "dashboard",
            "training",
            "remote_sensing",
            "mrv",
            "safeguards",
            "pilots",
            "logframe"
        ],
        "total_pilots": 12,
        "frameworks": ["CSA", "IWRM", "SLM", "LDN", "NbS"]
    }


# ========================================================================
# Startup Event
# ========================================================================
@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("=" * 80)
    print("🚀 Econojin Platform Starting...")
    print("=" * 80)
    print("📍 Platform: Integrated Landscape Management")
    print("🌍 Pilots: 12 global sites")
    print("📊 Frameworks: CSA, IWRM, SLM, LDN, NbS")
    print("=" * 80)
    
    # Optional: Create database tables on startup
    try:
        from api.core.database import create_tables
        # Uncomment the next line to auto-create tables on startup
        # create_tables()
        pass
    except Exception as e:
        print(f"⚠️  Could not initialize database: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Econojin Platform shutting down...")

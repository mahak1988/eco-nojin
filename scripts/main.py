# -*- coding: utf-8 -*-
"""
Econojin API - Main FastAPI Application
Scientific platform for ecological modeling + Gaia Protocol integration
"""

import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

# افزودن مسیر پروژه به sys.path
_project_root = Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(__project_root))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import routers
from scripts.api.routers import auth, farmer, gaia

# Import logger
try:
    from scripts.core.logger import UnifiedLogger

    logger = UnifiedLogger.get_logger(__name__)
except Exception:
    import logging

    logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan (startup/shutdown events)
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """مدیریت چرخه حیات برنامه"""
    logger.info("🌱 Econojin API starting up...")
    logger.info("🔬 Scientific models ready")
    logger.info("🌍 Gaia Protocol integration active")
    yield
    logger.info("👋 Econojin API shutting down")


# ============================================================================
# FastAPI App
# ============================================================================

app = FastAPI(
    title="Econojin API",
    description="""
# 🌱 Econojin - Scientific Ecological Platform

**Econojin** یک پلتفرم علمی برای مدل‌سازی اکولوژیکی و اتصال به **Gaia Protocol** است.

## ✨ ویژگی‌های اصلی

### 🔐 Authentication
- احراز هویت JWT
- مدیریت پروفایل
- اتصال کیف پول Web3

### 👨‍🌾 Farmers Management
- مدیریت کشاورزان
- ثبت فعالیت‌های کشاورزی
- پایش مزارع

### 🌍 Gaia Protocol Integration
- **محاسبه علمی کربن** با مدل‌های RothC، AquaCrop، SWAT+
- **ثبت فعالیت‌های اکوسیستمی** روی blockchain
- **تولید NFT گواهی** (Living NFTs)
- **Impact Scoring** چندبعدی
- **Portfolio tracking** برای کاربران

### 🧪 Scientific Models
- RothC (Soil Carbon)
- AquaCrop (Crop Growth)
- SWAT+ (Hydrology)

---

## 🔗 Links
- 📚 [Documentation](https://docs.econojin.com)
- 🌍 [Website](https://econojin.com)
- 💚 [Gaia Protocol](https://gaia.protocol.eco)
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Econojin Team",
        "email": "team@econojin.com",
    },
    license_info={
        "name": "MIT",
    },
)


# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://econojin.com",
        "https://staging.econojin.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Global Exception Handler
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """مدیریت خطاهای پیش‌بینی نشده"""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


# ============================================================================
# Include Routers
# ============================================================================

# Auth endpoints
app.include_router(auth.router, tags=["auth"])

# Farmer endpoints
app.include_router(farmer.router, prefix="/farmer", tags=["farmers"])

# Gaia Protocol endpoints (NEW!)
app.include_router(gaia.router, tags=["Gaia Protocol"])


# ============================================================================
# Root & Health Endpoints
# ============================================================================


@app.get("/", tags=["default"])
async def root():
    """Root endpoint"""
    return {
        "name": "Econojin API",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Authentication",
            "Farmers Management",
            "Gaia Protocol Integration",
            "Scientific Carbon Calculation",
            "Living NFT Certificates",
        ],
        "docs": "/docs",
        "gaia": "/docs#/Gaia Protocol",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health", tags=["default"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "database": "up",
            "gaia_oracle": "simulation",
            "scientific_models": "up",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/models", tags=["default"])
async def list_models():
    """لیست مدل‌های علمی موجود"""
    return {
        "models": [
            {
                "name": "RothC",
                "type": "soil_carbon",
                "description": "Rothamsted Carbon Model for soil organic carbon",
                "status": "active",
            },
            {
                "name": "AquaCrop",
                "type": "crop_growth",
                "description": "FAO crop water productivity model",
                "status": "active",
            },
            {
                "name": "SWAT+",
                "type": "hydrology",
                "description": "Soil and Water Assessment Tool",
                "status": "active",
            },
        ],
        "count": 3,
    }


# ============================================================================
# Run (for local development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "scripts.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

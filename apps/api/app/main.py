"""EcoNojin API - Main Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api_router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("🚀 EcoNojin API starting up...")
    await init_db()
    print("✅ Database initialized")
    yield
    print("👋 EcoNojin API shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Digital Twin of Hydroma Nojin",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to EcoNojin API",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "econojin-api"}

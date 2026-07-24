#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin - نقطه ورود اصلی بک‌اند
==================================
"""

import sys
from pathlib import Path

# اضافه کردن ریشه پروژه به sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# ============================================================
# پیکربندی Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("econojin")

# ============================================================
# بارگذاری ماژول‌های امنیتی عنکبوتی
# ============================================================
try:
    from apps.shared_core.security.middleware import (
        SpiderSecurityMiddleware,
        SecurityHeadersMiddleware,
        RateLimitMiddleware,
    )
    from apps.shared_core.security.protection import (
        InputSanitizer,
        SQLInjectionProtector,
        XSSProtector,
    )
    from apps.shared_core.security.fingerprint import RequestFingerprinter
    from apps.shared_core.security.anomaly import AnomalyDetector
    
    SECURITY_ENABLED = True
    logger.info("✅ ماژول‌های امنیت عنکبوتی بارگذاری شدند")
except Exception as e:
    SECURITY_ENABLED = False
    logger.warning(f"⚠️  ماژول‌های امنیتی بارگذاری نشدند: {e}")

load_dotenv(PROJECT_ROOT / ".env")

# ============================================================
# Lifespan Event Handlers
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("=" * 60)
    logger.info("🚀 Econojin API - شروع راه‌اندازی")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        from apps.shared_core.database.session import init_db
        await init_db()
        logger.info("✅ دیتابیس مقداردهی اولیه شد")
    except Exception as e:
        logger.warning(f"⚠️  init_db خطا: {e}")
    
    try:
        from apps.shared_ai.ai.llm_factory import LLMFactory
        logger.info("✅ ماژول AI بارگذاری شد")
    except Exception as e:
        logger.warning(f"⚠️  ماژول AI در دسترس نیست: {e}")
    
    logger.info(f"✅ راه‌اندازی در {time.time() - start_time:.2f} ثانیه کامل شد")
    logger.info("=" * 60)
    
    yield  # اینجا اپلیکیشن در حال اجرا است
    
    logger.info("=" * 60)
    logger.info("🛑 Econojin API - در حال خاموش شدن")
    logger.info("=" * 60)
    
    try:
        from apps.shared_core.database.session import close_db
        await close_db()
        logger.info("✅ اتصال دیتابیس بسته شد")
    except Exception as e:
        logger.warning(f"⚠️  close_db خطا: {e}")
    
    logger.info("✅ خاموش شدن کامل شد")
    logger.info("=" * 60)

# ============================================================
# ایجاد اپلیکیشن FastAPI
# ============================================================
app = FastAPI(
    title="Econojin API",
    description="پلتفرم جامع کشاورزی، آب، محیط‌زیست و اقتصاد",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================
# Middlewareها - لایه‌های امنیتی عنکبوتی
# ============================================================

# ۱. CORS Middleware (لایه اول - کنترل دسترسی)
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://localhost:8000").split(",")
allowed_origins = [o.strip() for o in origins if o.strip()]

# Validate origins to prevent security issues
def is_valid_origin(origin: str) -> bool:
    """Validate origin URL to prevent wildcard or insecure origins."""
    if not origin:
        return False
    # Reject wildcards
    if "*" in origin:
        return False
    # Must start with http:// or https://
    if not (origin.startswith("http://") or origin.startswith("https://")):
        return False
    return True

# Filter valid origins
valid_origins = [o for o in allowed_origins if is_valid_origin(o)]
if len(valid_origins) != len(allowed_origins):
    logger.warning(f"Some origins were filtered out for security. Valid: {valid_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=valid_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept", "Origin"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=600,
)

# ۲. Spider Security Middleware (لایه اصلی امنیت عنکبوتی)
if SECURITY_ENABLED:
    try:
        app.add_middleware(SpiderSecurityMiddleware)
        logger.info("🕸️ Spider Security Middleware فعال شد")
    except Exception as e:
        logger.warning(f"⚠️  خطا در فعال‌سازی Spider Security: {e}")

# ۳. Process Time Header (برای مانیتورینگ)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    
    # ثبت درخواست برای تحلیل ناهنجاری (اگر امنیت فعال باشد)
    if SECURITY_ENABLED:
        try:
            from apps.shared_core.security.anomaly import AnomalyDetector
            # این فقط برای نمونه است - در production باید به درستی پیاده‌سازی شود
        except Exception:
            pass
    
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"❌ خطای پیش‌بینی‌نشده: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "message": "یک خطای داخلی رخ داد."},
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Not Found", "message": f"مسیر {request.url.path} یافت نشد"},
    )

# ============================================================
# ثبت Routerهای ماژول‌ها (بخش اصلاح شده و تمیز)
# ============================================================

# ۱. ماژول Users
try:
    from apps.users.router import router as users_router
    app.include_router(users_router, prefix="/api/v1/users", tags=["👤 Users"])
    logger.info("✅ users: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  users: {e}")

# ۲. ماژول Auth (جدید)
try:
    from apps.users.auth_router import router as auth_router
    app.include_router(auth_router, prefix="/api/v1", tags=["🔐 Authentication"])
    logger.info("✅ auth: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  auth: {e}")

# ۳. ماژول AI Agents
try:
    from apps.ai_agents.router import router as ai_agents_router
    app.include_router(ai_agents_router, prefix="/api/v1/ai-agents", tags=["🤖 AI Agents"])
    logger.info("✅ ai_agents: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  ai_agents: {e}")

# ۴. ماژول Admin Panel
try:
    from apps.admin_panel.router import router as admin_router
    app.include_router(admin_router, prefix="/api/v1", tags=["🛠️ Admin"])
    logger.info("✅ admin_panel: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  admin_panel: {e}")

# ۵. ماژول Simulation
try:
    from apps.simulation.router import router as simulation_router
    app.include_router(simulation_router, prefix="/api/v1/simulation", tags=["🔬 Simulation"])
    logger.info("✅ simulation: روتر بارگذاری شد")
except Exception:
    logger.info("ℹ️  simulation: روتر یافت نشد (اختیاری)")

# ============================================================
# مسیرهای عمومی
# ============================================================
@app.get("/", tags=["🏠 Root"])
async def root():
    return {"name": "Econojin API", "status": "running", "version": "2.0.0", "docs": "/docs"}

@app.get("/health", tags=["🏥 Health"])
async def health():
    return {"status": "healthy", "version": "2.0.0"}

# ============================================================
# اجرای مستقیم
# ============================================================
if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("ENV_STATE", "development") == "development"
    
    logger.info(f"🚀 شروع سرور توسعه روی {host}:{port}")
    logger.info(f"📚 مستندات: http://localhost:{port}/docs")
    
    uvicorn.run(
        "apps.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
        access_log=True,
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin - نقطه ورود اصلی بک‌اند
==================================
Adapted from fastapi/full-stack-fastapi-template with centralized config.
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
# بارگذاری تنظیمات متمرکز
# ============================================================
from apps.shared_core.config import settings

# ============================================================
# Lifespan Event Handlers
# ============================================================
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("=" * 60)
    logger.info(f"🚀 Econojin API v{settings.VERSION} - شروع راه‌اندازی")
    logger.info(f"🌍 Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 60)

    start_time = time.time()

    # مقداردهی اولیه دیتابیس
    try:
        from apps.shared_core.database.session import init_db
        await init_db()
        logger.info("✅ دیتابیس مقداردهی اولیه شد")
    except Exception as e:
        logger.warning(f"⚠️  init_db خطا: {e}")

    # بارگذاری ماژول AI
    try:
        from apps.shared_ai.ai.llm_factory import LLMFactory
        logger.info(f"✅ ماژول AI بارگذاری شد (provider: {settings.LLM_PROVIDER})")
    except Exception as e:
        logger.warning(f"⚠️  ماژول AI در دسترس نیست: {e}")

    # راه‌اندازی Sentry
    try:
        from apps.shared_core.monitoring.sentry import init_sentry
        init_sentry(app)
        logger.info("✅ Sentry monitoring مقداردهی اولیه شد")
    except Exception as e:
        logger.warning(f"⚠️  Sentry در دسترس نیست: {e}")

    logger.info(f"✅ راه‌اندازی در {time.time() - start_time:.2f} ثانیه کامل شد")
    logger.info("=" * 60)

    yield  # اپلیکیشن در حال اجرا است

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
    title=settings.PROJECT_NAME,
    description="پلتفرم جامع کشاورزی، آب، محیط‌زیست و اقتصاد",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ============================================================
# Middlewareها
# ============================================================
# Rate Limiting (Brute Force Protection)
if settings.ENVIRONMENT != "local":
    try:
        from apps.shared_core.middleware.rate_limit import RateLimitMiddleware
        from apps.shared_core.middleware.audit_log import AuditLogMiddleware
        app.add_middleware(RateLimitMiddleware)
        app.add_middleware(AuditLogMiddleware)
        logger.info("✅ Security middlewares added")
    except Exception as e:
        logger.warning(f"⚠️ Security middleware failed: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With", "Accept", "Origin"],
    expose_headers=["X-Total-Count", "X-Page-Count"],
    max_age=600,
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
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
# ثبت Routerهای ماژول‌ها
# ============================================================

# ۱. ماژول Users
try:
    from apps.users.router import router as users_router
    app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["👤 Users"])
    logger.info("✅ users: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  users: {e}")

# ۲. ماژول Auth
try:
    from apps.users.auth_router import router as auth_router
    app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["🔐 Authentication"])
    logger.info("✅ auth: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  auth: {e}")

# ۳. ماژول AI Agents
try:
    from apps.ai_agents.router import router as ai_agents_router
    app.include_router(ai_agents_router, prefix=f"{settings.API_V1_STR}/ai-agents", tags=["🤖 AI Agents"])
    logger.info("✅ ai_agents: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  ai_agents: {e}")

# ۴. ماژول Accounting
try:
    from apps.api.routes.accounting import router as accounting_router
    app.include_router(accounting_router)
    logger.info("✅ accounting: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  accounting: {e}")

# ۵. ماژول EcoCoin
try:
    from apps.api.routes.ecocoin import router as ecocoin_router
    app.include_router(ecocoin_router)
    logger.info("✅ ecocoin: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  ecocoin: {e}")

# ۶. ماژول Monitoring
try:
    from apps.api.routes.monitoring import router as monitoring_router
    app.include_router(monitoring_router)
    logger.info("✅ monitoring: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  monitoring: {e}")

# ۷. ماژول Simulator
try:
    from apps.api.routes.simulator import router as simulator_router
    app.include_router(simulator_router)
    logger.info("✅ simulator: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  simulator: {e}")

# ۸. ماژول Admin Panel
try:
    from apps.admin_panel.router import router as admin_router
    app.include_router(admin_router, prefix=settings.API_V1_STR, tags=["🛠️ Admin"])
    logger.info("✅ admin_panel: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  admin_panel: {e}")

# ۹. ماژول Simulation
try:
    from apps.simulation.router import router as simulation_router
    app.include_router(simulation_router, prefix=f"{settings.API_V1_STR}/simulation", tags=["🔬 Simulation"])
    logger.info("✅ simulation: روتر بارگذاری شد")
except Exception:
    logger.info("ℹ️  simulation: روتر یافت نشد (اختیاری)")

# ماژول Real-World Data (NASA POWER / Open-Meteo / Open-Elevation / World Bank)
try:
    from apps.simulation.data.router import router as data_router
    app.include_router(data_router)
    logger.info("✅ data: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  data: {e}")

# ماژول Advisory (تحلیل + توصیه + سناریو)
try:
    from apps.simulation.advisory.router import router as advisory_router
    app.include_router(advisory_router)
    logger.info("✅ advisory: روتر بارگذاری شد")

except Exception as e:
    pass

# ماژول Saved Runs (داشبورد کاربر)
try:
    from apps.simulation.runs.router import router as runs_router
    app.include_router(runs_router)
    logger.info("✅ runs: روتر بارگذاری شد")
except Exception as e:
    pass


# ماژول Scenario & Comparison
try:
    from apps.simulation.scenario.router import router as scenario_router
    app.include_router(scenario_router)
    logger.info("✅ scenario: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  scenario: {e}")

# ماژول Validation (کالیبراسیون + عدم قطعیت + حساسیت)
try:
    from apps.simulation.validation.router import router as validation_router
    app.include_router(validation_router)
    logger.info("✅ validation: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  validation: {e}")
    logger.warning(f"⚠️  runs: {e}")
    logger.warning(f"⚠️  router block: {e}")
# ۱۰. ماژول Agriculture Schools
try:
    from apps.api.routes.agriculture_schools import router as ag_schools_router
    app.include_router(ag_schools_router)
    logger.info("✅ agriculture_schools: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  agriculture_schools: {e}")

# ۱۱. ماژول Education
try:
    from apps.api.routes.education import router as education_router
    app.include_router(education_router)
    logger.info("✅ education: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  education: {e}")

# ۱۲. ماژول Community
try:
    from apps.api.routes.community import router as community_router
    app.include_router(community_router)
    logger.info("✅ community: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  community: {e}")

# ۱۳. ماژول Games
try:
    from apps.api.routes.games import router as games_router
    app.include_router(games_router)
    logger.info("✅ games: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  games: {e}")

# ۱۴. ماژول Model Chaining (زنجیرهٔ شبیه‌سازی)
try:
    from apps.simulation.chain.router import router as chain_router
    app.include_router(chain_router)
    logger.info("✅ chain: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  chain: {e}")

# ۱۵. ماژول Reports (گزارش‌گیری CSV/JSON)
try:
    from apps.simulation.reports.router import router as reports_router
    app.include_router(reports_router)
    logger.info("✅ reports: روتر بارگذاری شد")
except Exception as e:
    logger.warning(f"⚠️  reports: {e}")


# ============================================================
# مسیرهای عمومی
# ============================================================
@app.get("/", tags=["🏠 Root"])
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "running",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
    }


@app.get("/health", tags=["🏥 Health"])
async def health():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/modules", tags=["📦 Modules"])
async def list_modules():
    """لیست ماژول‌های فعال API."""
    return {
        "modules": [
            "users",
            "auth",
            "ai_agents",
            "accounting",
            "ecocoin",
            "monitoring",
            "simulator",
            "admin_panel",
            "simulation",
            "agriculture_schools",
            "alerts",
            "education",
            "library",
            "community",
            "games",
        ],
        "total": 15,
    }


# ============================================================
# اجرای مستقیم
# ============================================================
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", str(settings.API_V1_STR and "8000")))
    reload = settings.ENVIRONMENT == "local"

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
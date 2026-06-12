#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Backend Auto-Fix Script
نسخه: 1.0.0
توضیحات: اصلاح خودکار تمام فایل‌های بک‌اند برای اتصال به فرانت‌اند
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


# ============================================================================
# Configuration
# ============================================================================
BASE_DIR = Path(__file__).parent
API_DIR = BASE_DIR / "api"
BACKUP_DIR = BASE_DIR / f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# ============================================================================
# Backup Function
# ============================================================================
def create_backup():
    """ایجاد backup از فایل‌های اصلی"""
    print("📦 در حال ایجاد backup...")
    
    files_to_backup = [
        API_DIR / "main.py",
        API_DIR / "core" / "config.py",
        API_DIR / "modules" / "auth" / "router.py",
    ]
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            backup_path = BACKUP_DIR / file_path.relative_to(BASE_DIR)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"  ✅ Backup: {file_path.name}")
    
    print(f"✅ Backup کامل در: {BACKUP_DIR}\n")


# ============================================================================
# File 1: api/core/config.py
# ============================================================================
def fix_config_py():
    """اصلاح فایل config.py"""
    print("🔧 اصلاح api/core/config.py...")
    
    config_content = '''"""
Econojin Configuration - Pydantic Settings
نسخه 2.0.0 - بازسازی شده
"""
import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================================
# Base Directory
# ============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ============================================================================
# Settings Class
# ============================================================================
class Settings(BaseSettings):
    """تنظیمات اصلی پروژه"""
    
    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "api" / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ========================================================================
    # Application
    # ========================================================================
    APP_NAME: str = "Econojin API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=True, description="حالت توسعه")
    ENVIRONMENT: str = Field(default="development", description="development | production | staging")
    
    # ========================================================================
    # API Configuration
    # ========================================================================
    API_V1_PREFIX: str = "/api/v1"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # ========================================================================
    # CORS Configuration - 🔴 اصلاح: str به جای list
    # ========================================================================
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001",
        description="لیست دامنه‌های مجاز برای CORS (با کاما جدا شده)"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # ========================================================================
    # Database Configuration
    # ========================================================================
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./econojin.db",
        description="آدرس دیتابیس (async)"
    )
    DATABASE_ECHO: bool = Field(default=False, description="نمایش کوئری‌های SQL")
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # ========================================================================
    # Security & JWT
    # ========================================================================
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production-abcdef123456",
        description="کلید مخفی برای JWT"
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440, description="24 ساعت")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="7 روز")
    
    # ========================================================================
    # OTP Configuration
    # ========================================================================
    OTP_DEV_MODE: bool = Field(
        default=True,
        description="در حالت توسعه، کد OTP در response برگردانده می‌شود"
    )
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    OTP_MAX_ATTEMPTS: int = 5
    
    # ========================================================================
    # SMS Provider (Kavenegar / Twilio)
    # ========================================================================
    SMS_PROVIDER: str = Field(default="dev", description="dev | kavenegar | twilio")
    KAVENEGAR_API_KEY: Optional[str] = None
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # ========================================================================
    # EcoCoin & Blockchain
    # ========================================================================
    ECOCOIN_CONTRACT_ADDRESS: Optional[str] = None
    POLYGON_RPC_URL: Optional[str] = None
    BLOCKCHAIN_EXPLORER_URL: str = "https://polygonscan.com"
    
    # ========================================================================
    # AI & LLM
    # ========================================================================
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000
    
    # ========================================================================
    # Satellite & GIS
    # ========================================================================
    SENTINEL_HUB_CLIENT_ID: Optional[str] = None
    SENTINEL_HUB_CLIENT_SECRET: Optional[str] = None
    NASA_API_KEY: Optional[str] = None
    
    # ========================================================================
    # Weather Services
    # ========================================================================
    OPEN_METEO_ENABLED: bool = True
    WEATHER_API_KEY: Optional[str] = None
    
    # ========================================================================
    # IoT (MQTT)
    # ========================================================================
    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_USERNAME: Optional[str] = None
    MQTT_PASSWORD: Optional[str] = None
    
    # ========================================================================
    # File Storage
    # ========================================================================
    UPLOAD_DIR: Path = Field(default=BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 50
    
    # ========================================================================
    # Rate Limiting
    # ========================================================================
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 10
    
    # ========================================================================
    # Logging
    # ========================================================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # ========================================================================
    # 🔴 Computed Properties - اصلاح حیاتی
    # ========================================================================
    @property
    def cors_origins_list(self) -> list[str]:
        """تبدیل CORS_ORIGINS از string به list"""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def database_is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


# ============================================================================
# Global Settings Instance
# ============================================================================
settings = Settings()


# ============================================================================
# Utility Functions
# ============================================================================
def get_settings() -> Settings:
    """دریافت instance تنظیمات"""
    return settings


def reload_settings() -> Settings:
    """بارگذاری مجدد تنظیمات (برای توسعه)"""
    global settings
    settings = Settings()
    return settings


# ============================================================================
# Startup Validation
# ============================================================================
def validate_settings() -> None:
    """اعتبارسنجی تنظیمات در startup"""
    if settings.is_production:
        if settings.SECRET_KEY.startswith("dev-secret"):
            raise ValueError("❌ SECRET_KEY در production باید تغییر کند!")
        
        if not settings.DATABASE_URL or settings.database_is_sqlite:
            print("⚠️  هشدار: استفاده از SQLite در production توصیه نمی‌شود")
    
    # ایجاد پوشه uploads
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ Settings loaded: {settings.ENVIRONMENT} mode")
    print(f"📦 Database: {'SQLite' if settings.database_is_sqlite else 'PostgreSQL'}")
    print(f"🔐 OTP Dev Mode: {settings.OTP_DEV_MODE}")
    print(f"🌐 CORS Origins: {settings.cors_origins_list}")


if __name__ == "__main__":
    # تست تنظیمات
    validate_settings()
    print(f"\\n📋 All settings:")
    for key, value in settings.model_dump().items():
        # مخفی کردن مقادیر حساس
        if any(s in key.lower() for s in ["key", "secret", "token", "password"]):
            value = "***REDACTED***"
        print(f"  {key}: {value}")
'''
    
    config_path = API_DIR / "core" / "config.py"
    config_path.write_text(config_content, encoding="utf-8")
    print("  ✅ config.py اصلاح شد\n")


# ============================================================================
# File 2: api/main.py
# ============================================================================
def fix_main_py():
    """اصلاح فایل main.py"""
    print("🔧 اصلاح api/main.py...")
    
    main_content = '''import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.database import init_db
from api.core.config import settings

# Import all routers
from api.modules.academy.router import router as academy_router
from api.modules.ai.router import router as ai_router
from api.modules.accounting.router import router as accounting_router
from api.modules.auth.router import router as auth_router
from api.modules.community.router import router as community_router
from api.modules.drought.router import router as drought_router
from api.modules.ecocoin.router import router as ecocoin_router
from api.modules.farmer.router import router as farmer_router
from api.modules.financial.router import router as financial_router
from api.modules.games.router import router as games_router
from api.modules.iot.router import router as iot_router
from api.modules.library.router import router as library_router
from api.modules.maintenance.router import router as maintenance_router
from api.modules.mrv.router import router as mrv_router
from api.modules.newsletter.router import router as newsletter_router
from api.modules.psychology.router import router as psychology_router
from api.modules.soil_water.router import router as soil_water_router
from api.modules.store.router import router as store_router
from api.modules.weather.router import router as weather_router
from api.modules.dashboard.router import router as dashboard_router
from api.modules.desktop.router import router as desktop_router
from api.modules.ecomining.router import router as ecomining_router
from api.modules.education.router import router as education_router
from api.modules.simulation.router import router as simulation_router
from api.scientific_core.router import router as scientific_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Econojin v2.0.0...")
    await init_db()

    try:
        from api.services.early_warning_engine import ews_engine
        asyncio.create_task(ews_engine.start())
        print("✅ Early Warning Engine started")
    except Exception as e:
        print(f"⚠️ EWS skipped: {e}")

    print("✅ Ready on http://127.0.0.1:8000")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    yield
    print("🛑 Shutting down...")


app = FastAPI(
    title="Econojin API",
    description="پلتفرم علمی-فناورانه احیای مناظر خشک و نیمه‌خشک",
    version="2.0.0",
    lifespan=lifespan,
)

# 🔴 اصلاح: استفاده از cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
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


# ============================================================
# 🔴 اصلاح حیاتی: ثبت تمام routerها (بدون تکرار)
# ============================================================
ROUTERS = [
    # 🔴 Auth & User Management - اضافه شد
    (auth_router, "/api/v1"),
    (farmer_router, "/api/v1/farmers"),
    
    # Core Modules
    (ecocoin_router, "/api/v1"),
    (ecomining_router, "/api/v1"),
    (dashboard_router, "/api/v1"),
    (desktop_router, "/api/v1"),
    
    # Environmental
    (weather_router, "/api/v1"),
    (drought_router, "/api/v1"),
    (soil_water_router, "/api/v1"),
    (mrv_router, "/api/v1"),
    (iot_router, "/api/v1"),
    (scientific_router, "/api/v1"),
    
    # Business
    (store_router, "/api/v1"),
    (financial_router, "/api/v1"),
    (accounting_router, "/api/v1"),
    
    # Content & Community
    (academy_router, "/api/v1"),
    (education_router, "/api/v1"),
    (library_router, "/api/v1"),
    (community_router, "/api/v1"),
    (newsletter_router, "/api/v1"),
    (psychology_router, "/api/v1"),
    (games_router, "/api/v1"),
    
    # Operations
    (maintenance_router, "/api/v1"),
    (simulation_router, "/api/v1"),
    (ai_router, "/api/v1"),
]

for router_instance, prefix in ROUTERS:
    app.include_router(router_instance, prefix=prefix)

print(f"✅ All {len(ROUTERS)} routers registered successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
'''
    
    main_path = API_DIR / "main.py"
    main_path.write_text(main_content, encoding="utf-8")
    print("  ✅ main.py اصلاح شد\n")


# ============================================================================
# File 3: api/modules/auth/router.py
# ============================================================================
def fix_auth_router():
    """اصلاح فایل auth/router.py"""
    print("🔧 اصلاح api/modules/auth/router.py...")
    
    auth_router_content = '''"""
ماژول احراز هویت و مدیریت کاربر (OTP-based)
نسخه 2.0 - بازبینی کدها و اصول ساختار درخواست‌ها
"""
import secrets
import time
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.security import create_access_token, get_current_user_id
from api.modules.auth import crud, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

# 🔴 اصلاح: OTP Store در حافظه (برای توسعه)
_otp_store: dict[str, dict] = {}


def generate_otp(phone: str) -> str:
    """تولید کد OTP 6 رقمی"""
    code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    _otp_store[phone] = {
        "code": code,
        "expires": datetime.now() + timedelta(minutes=5),
        "attempts": 0,
    }
    return code


def verify_otp(phone: str, code: str) -> bool:
    """تأیید کد OTP"""
    stored = _otp_store.get(phone)
    if not stored:
        return False
    
    if datetime.now() > stored["expires"]:
        del _otp_store[phone]
        return False
    
    if stored["attempts"] >= 5:
        del _otp_store[phone]
        return False
    
    if stored["code"] != code:
        stored["attempts"] += 1
        return False
    
    # موفقیت - حذف OTP
    del _otp_store[phone]
    return True


@router.post("/otp/request", response_model=dict)
async def request_otp(req: schemas.OtpRequest):
    """درخواست کد OTP"""
    from api.services.sms import send_otp_sms
    from api.core.config import settings
    
    code = generate_otp(req.phone)
    
    try:
        sent = await send_otp_sms(req.phone, code)
    except Exception:
        sent = False
    
    # 🔴 در حالت توسعه، کد را برگردان
    if settings.DEBUG or settings.OTP_DEV_MODE:
        return {
            "sent": True,
            "phone": req.phone,
            "dev_code": code,
            "expires_in": 300,
            "message": "کد OTP ارسال شد (در حالت توسعه، کد در dev_code موجود است)"
        }
    
    if not sent:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="سرویس پیامک در دسترس نیست",
        )
    
    return {"sent": True, "phone": req.phone, "expires_in": 300}


@router.post("/otp/verify", response_model=schemas.TokenResponse)
async def verify_otp_login(req: schemas.OtpVerify, db: AsyncSession = Depends(get_db)):
    """تأیید کد OTP و ورود"""
    if not verify_otp(req.phone, req.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="کد وارد شده نامعتبر یا منقضی شده است",
        )
    
    # Upsert کاربر
    login_req = schemas.LoginRequest(fid=req.fid, phone=req.phone, name=req.name)
    user = await crud.upsert_user(db, login_req)
    
    # ساخت توکن
    token = create_access_token(subject=user.farmer_id)
    
    return schemas.TokenResponse(
        access_token=token,
        token_type="bearer",
        farmer_id=user.farmer_id,
    )


@router.post("/login", response_model=schemas.TokenResponse)
async def login(req: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    ورود ساده (فقط برای توسعه)
    ⚠️ هشدار: این endpoint بدون بررسی رمز، کاربر را upsert می‌کند
    """
    user = await crud.upsert_user(db, req)
    token = create_access_token(subject=user.farmer_id)
    return schemas.TokenResponse(
        access_token=token,
        token_type="bearer",
        farmer_id=user.farmer_id,
    )


@router.get("/profile", response_model=schemas.ProfileResponse)
async def get_profile(
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """دریافت پروفایل کاربر"""
    user = await crud.get_user_by_farmer_id(db, farmer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر با این شناسه یافت نشد",
        )
    
    return schemas.ProfileResponse(
        fid=user.farmer_id,
        name=user.name or user.farmer_id,
        phone=user.phone,
        registered_at=user.created_at,
        wallet_address=user.wallet_address,
    )


@router.post("/profile/wallet")
async def link_wallet(
    req: schemas.WalletLinkRequest,
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """اتصال آدرس کیف پول به حساب کاربری"""
    user = await crud.link_wallet(db, farmer_id, req.wallet_address)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد",
        )
    return {"success": True, "wallet_address": user.wallet_address}
'''
    
    auth_router_path = API_DIR / "modules" / "auth" / "router.py"
    auth_router_path.write_text(auth_router_content, encoding="utf-8")
    print("  ✅ auth/router.py اصلاح شد\n")


# ============================================================================
# File 4: api/.env
# ============================================================================
def create_env_file():
    """ایجاد فایل .env"""
    print("🔧 ایجاد api/.env...")
    
    env_content = '''# ============================================================================
# Econojin Environment Variables
# ============================================================================

# Application
ENVIRONMENT=development
DEBUG=true

# Database (SQLite برای توسعه)
DATABASE_URL=sqlite+aiosqlite:///./econojin.db

# Security
SECRET_KEY=dev-secret-key-change-in-production-abcdef123456
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OTP
OTP_DEV_MODE=true
OTP_LENGTH=6
OTP_EXPIRE_MINUTES=5

# 🔴 اصلاح: بدون quotes و brackets، فقط با کاما جدا شده
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001

# AI (اختیاری)
# OPENAI_API_KEY=sk-...

# SMS (اختیاری)
SMS_PROVIDER=dev
'''
    
    env_path = API_DIR / ".env"
    env_path.write_text(env_content, encoding="utf-8")
    print("  ✅ .env ایجاد شد\n")


# ============================================================================
# Main Execution
# ============================================================================
def main():
    print("=" * 70)
    print("🚀 Econojin Backend Auto-Fix Script")
    print("=" * 70)
    print()
    
    # بررسی وجود فایل‌ها
    if not API_DIR.exists():
        print(f"❌ خطا: پوشه api یافت نشد: {API_DIR}")
        return
    
    # ایجاد backup
    create_backup()
    
    # اعمال اصلاحات
    try:
        fix_config_py()
        fix_main_py()
        fix_auth_router()
        create_env_file()
        
        print("=" * 70)
        print("✅ تمام اصلاحات با موفقیت اعمال شدند!")
        print("=" * 70)
        print()
        print("📋 خلاصه تغییرات:")
        print("  1. ✅ config.py - CORS_ORIGINS به str تبدیل شد")
        print("  2. ✅ main.py - auth_router و farmer_router اضافه شدند")
        print("  3. ✅ auth/router.py - generate_otp و verify_otp اضافه شدند")
        print("  4. ✅ .env - فرمت صحیح CORS_ORIGINS")
        print()
        print("🚀 گام بعدی:")
        print("  1. بک‌اند را مجدداً اجرا کنید:")
        print("     uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print("  2. به http://localhost:8000/docs بروید و تست کنید")
        print()
        print(f"💾 Backup در: {BACKUP_DIR}")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا در اعمال اصلاحات: {e}")
        print(f"💾 می‌توانید از backup بازیابی کنید: {BACKUP_DIR}")
        raise


if __name__ == "__main__":
    main()
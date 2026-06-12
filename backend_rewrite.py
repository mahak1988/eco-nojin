#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Backend Complete Rewrite Script
نسخه: 2.0.0
توضیحات: بازنویسی کامل تمام فایل‌های بک‌اند برای اتصال به فرانت‌اند
"""

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
        API_DIR / "modules" / "auth" / "schemas.py",
        API_DIR / "modules" / "auth" / "crud.py",
    ]
    
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    for file_path in files_to_backup:
        if file_path.exists():
            backup_path = BACKUP_DIR / file_path.relative_to(BASE_DIR)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_path)
            print(f"  ✅ Backup: {file_path.relative_to(BASE_DIR)}")
    
    print(f"✅ Backup کامل در: {BACKUP_DIR}\n")


# ============================================================================
# File 1: api/core/config.py
# ============================================================================
def write_config_py():
    """بازنویسی کامل config.py"""
    print("🔧 بازنویسی api/core/config.py...")
    
    content = '''"""
Econojin Configuration - Pydantic Settings
نسخه 2.0.0
"""
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """تنظیمات اصلی پروژه"""
    
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / "api" / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    APP_NAME: str = "Econojin API"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS - 🔴 اصلاح: str به جای list
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./econojin.db"
    DATABASE_ECHO: bool = False
    
    # Security & JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production-abcdef123456"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # OTP
    OTP_DEV_MODE: bool = True
    OTP_LENGTH: int = 6
    OTP_EXPIRE_MINUTES: int = 5
    
    # SMS
    SMS_PROVIDER: str = "dev"
    KAVENEGAR_API_KEY: Optional[str] = None
    
    # AI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Upload
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    
    # 🔴 Computed Properties
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
    def database_is_sqlite(self) -> bool:
        return "sqlite" in self.DATABASE_URL


settings = Settings()


def validate_settings() -> None:
    """اعتبارسنجی تنظیمات"""
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✅ Settings: {settings.ENVIRONMENT} mode")
    print(f"📦 Database: {'SQLite' if settings.database_is_sqlite else 'PostgreSQL'}")
    print(f"🌐 CORS: {settings.cors_origins_list}")
'''
    
    path = API_DIR / "core" / "config.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ config.py بازنویسی شد\n")


# ============================================================================
# File 2: api/core/security.py
# ============================================================================
def write_security_py():
    """بازنویسی کامل security.py"""
    print("🔧 بازنویسی api/core/security.py...")
    
    content = '''"""
Security utilities - JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from api.core.config import settings


# 🔴 Security scheme
security = HTTPBearer(auto_error=False)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """ساخت JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """تأیید و decode کردن توکن"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        farmer_id: str = payload.get("sub")
        if farmer_id is None:
            return None
        return farmer_id
    except JWTError:
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """استخراج farmer_id از توکن JWT"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن احراز هویت ارسال نشده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    farmer_id = verify_token(credentials.credentials)
    if farmer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return farmer_id


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    """استخراج farmer_id (اختیاری - بدون خطا)"""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)
'''
    
    path = API_DIR / "core" / "security.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ security.py بازنویسی شد\n")


# ============================================================================
# File 3: api/modules/auth/schemas.py
# ============================================================================
def write_auth_schemas():
    """بازنویسی کامل auth/schemas.py"""
    print("🔧 بازنویسی api/modules/auth/schemas.py...")
    
    content = '''"""
Authentication Schemas - Pydantic models
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# Login & Register
# ============================================================================

class LoginRequest(BaseModel):
    """درخواست ورود"""
    fid: str = Field(..., min_length=3, max_length=32, description="شناسه کاربری")
    phone: str = Field(..., pattern=r"^\\+?[0-9]{10,15}$", description="شماره تلفن")
    name: str = Field(default="", max_length=100, description="نام کاربر")


class TokenResponse(BaseModel):
    """پاسخ ورود - شامل توکن"""
    access_token: str
    token_type: str = "bearer"
    farmer_id: str


# ============================================================================
# OTP
# ============================================================================

class OtpRequest(BaseModel):
    """درخواست ارسال کد OTP"""
    phone: str = Field(..., pattern=r"^\\+?[0-9]{10,15}$")
    fid: str = Field(default="", max_length=32)


class OtpRequestResponse(BaseModel):
    """پاسخ درخواست OTP"""
    sent: bool
    phone: str
    dev_code: Optional[str] = None
    expires_in: int = 300
    message: Optional[str] = None


class OtpVerify(BaseModel):
    """تأیید کد OTP"""
    phone: str = Field(..., pattern=r"^\\+?[0-9]{10,15}$")
    code: str = Field(..., min_length=4, max_length=8)
    fid: str = Field(..., min_length=3, max_length=32)
    name: str = Field(default="", max_length=100)


# ============================================================================
# Profile
# ============================================================================

class ProfileResponse(BaseModel):
    """پاسخ پروفایل کاربر"""
    fid: str
    name: str
    phone: str
    registered_at: datetime
    wallet_address: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# 🔴 Wallet - کلاس‌های جدید
# ============================================================================

class WalletLinkRequest(BaseModel):
    """درخواست اتصال کیف پول"""
    wallet_address: str = Field(..., min_length=10, max_length=128)


class WalletLinkResponse(BaseModel):
    """پاسخ اتصال کیف پول"""
    success: bool
    wallet_address: str
'''
    
    path = API_DIR / "modules" / "auth" / "schemas.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ auth/schemas.py بازنویسی شد\n")


# ============================================================================
# File 4: api/modules/auth/crud.py
# ============================================================================
def write_auth_crud():
    """بازنویسی کامل auth/crud.py"""
    print("🔧 بازنویسی api/modules/auth/crud.py...")
    
    content = '''"""
Authentication CRUD operations
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth import models, schemas


async def upsert_user(db: AsyncSession, req: schemas.LoginRequest) -> models.UserAccount:
    """ایجاد یا به‌روزرسانی کاربر"""
    # جستجوی کاربر با farmer_id
    result = await db.execute(
        select(models.UserAccount).where(models.UserAccount.farmer_id == req.fid)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # به‌روزرسانی کاربر موجود
        user.phone = req.phone
        if req.name:
            user.name = req.name
    else:
        # ایجاد کاربر جدید
        user = models.UserAccount(
            farmer_id=req.fid,
            phone=req.phone,
            name=req.name or "",
        )
        db.add(user)
    
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_farmer_id(db: AsyncSession, farmer_id: str) -> models.UserAccount | None:
    """دریافت کاربر با farmer_id"""
    result = await db.execute(
        select(models.UserAccount).where(models.UserAccount.farmer_id == farmer_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> models.UserAccount | None:
    """دریافت کاربر با شماره تلفن"""
    result = await db.execute(
        select(models.UserAccount).where(models.UserAccount.phone == phone)
    )
    return result.scalar_one_or_none()


async def link_wallet(db: AsyncSession, farmer_id: str, wallet_address: str) -> models.UserAccount | None:
    """اتصال آدرس کیف پول به کاربر"""
    user = await get_user_by_farmer_id(db, farmer_id)
    if not user:
        return None
    
    user.wallet_address = wallet_address
    await db.commit()
    await db.refresh(user)
    return user
'''
    
    path = API_DIR / "modules" / "auth" / "crud.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ auth/crud.py بازنویسی شد\n")


# ============================================================================
# File 5: api/modules/auth/router.py
# ============================================================================
def write_auth_router():
    """بازنویسی کامل auth/router.py"""
    print("🔧 بازنویسی api/modules/auth/router.py...")
    
    content = '''"""
Authentication Router - OTP-based login
"""
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.security import create_access_token, get_current_user_id
from api.modules.auth import crud, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OTP Store (in-memory for development)
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
    
    del _otp_store[phone]
    return True


@router.post("/otp/request", response_model=schemas.OtpRequestResponse)
async def request_otp(req: schemas.OtpRequest):
    """درخواست کد OTP"""
    from api.core.config import settings
    
    code = generate_otp(req.phone)
    
    # در حالت توسعه، کد را برگردان
    if settings.DEBUG or settings.OTP_DEV_MODE:
        return schemas.OtpRequestResponse(
            sent=True,
            phone=req.phone,
            dev_code=code,
            expires_in=300,
            message="کد OTP تولید شد (حالت توسعه)"
        )
    
    # TODO: ارسال SMS واقعی
    return schemas.OtpRequestResponse(
        sent=True,
        phone=req.phone,
        expires_in=300,
        message="کد OTP ارسال شد"
    )


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
    """ورود ساده (فقط برای توسعه)"""
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
            detail="کاربر یافت نشد",
        )
    
    return schemas.ProfileResponse(
        fid=user.farmer_id,
        name=user.name or user.farmer_id,
        phone=user.phone,
        registered_at=user.created_at,
        wallet_address=user.wallet_address,
    )


@router.post("/profile/wallet", response_model=schemas.WalletLinkResponse)
async def link_wallet(
    req: schemas.WalletLinkRequest,
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """اتصال آدرس کیف پول"""
    user = await crud.link_wallet(db, farmer_id, req.wallet_address)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد",
        )
    return schemas.WalletLinkResponse(
        success=True,
        wallet_address=user.wallet_address,
    )
'''
    
    path = API_DIR / "modules" / "auth" / "router.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ auth/router.py بازنویسی شد\n")


# ============================================================================
# File 6: api/main.py
# ============================================================================
def write_main_py():
    """بازنویسی کامل main.py"""
    print("🔧 بازنویسی api/main.py...")
    
    content = '''"""
Econojin API - Main Application
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.database import init_db
from api.core.config import settings, validate_settings

# Import all routers
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
    """Startup and shutdown events"""
    print("🚀 Starting Econojin v2.0.0...")
    validate_settings()
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
    description="پلتفرم علمی-فناورانه احیای مناظر خشک",
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


# ============================================================
# Register all routers
# ============================================================
ROUTERS = [
    # 🔴 Auth & User Management
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

print(f"✅ All {len(ROUTERS)} routers registered")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
'''
    
    path = API_DIR / "main.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ main.py بازنویسی شد\n")


# ============================================================================
# File 7: api/.env
# ============================================================================
def write_env_file():
    """ایجاد/بازنویسی .env"""
    print("🔧 ایجاد api/.env...")
    
    content = '''# ============================================================================
# Econojin Environment Variables
# ============================================================================

# Application
ENVIRONMENT=development
DEBUG=true

# Database
DATABASE_URL=sqlite+aiosqlite:///./econojin.db

# Security
SECRET_KEY=dev-secret-key-change-in-production-abcdef123456
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# OTP
OTP_DEV_MODE=true

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001

# SMS
SMS_PROVIDER=dev
'''
    
    path = API_DIR / ".env"
    path.write_text(content, encoding="utf-8")
    print("  ✅ .env ایجاد شد\n")


# ============================================================================
# Main Execution
# ============================================================================
def main():
    print("=" * 70)
    print("🚀 Econojin Backend Complete Rewrite")
    print("=" * 70)
    print()
    
    if not API_DIR.exists():
        print(f"❌ خطا: پوشه api یافت نشد: {API_DIR}")
        return
    
    # Backup
    create_backup()
    
    # Rewrite all files
    try:
        write_config_py()
        write_security_py()
        write_auth_schemas()
        write_auth_crud()
        write_auth_router()
        write_main_py()
        write_env_file()
        
        print("=" * 70)
        print("✅ تمام فایل‌ها با موفقیت بازنویسی شدند!")
        print("=" * 70)
        print()
        print("📋 فایل‌های بازنویسی‌شده:")
        print("  1. ✅ api/core/config.py")
        print("  2. ✅ api/core/security.py")
        print("  3. ✅ api/modules/auth/schemas.py")
        print("  4. ✅ api/modules/auth/crud.py")
        print("  5. ✅ api/modules/auth/router.py")
        print("  6. ✅ api/main.py")
        print("  7. ✅ api/.env")
        print()
        print("🚀 گام بعدی:")
        print("  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        print(f"💾 Backup در: {BACKUP_DIR}")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n💾 بازیابی از: {BACKUP_DIR}")


if __name__ == "__main__":
    main()
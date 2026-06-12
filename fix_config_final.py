import os

# مسیر فایل
config_path = r"D:\econojin.com\api\core\config.py"

# نمایش محتوای فعلی (برای دیباگ)
print("=" * 70)
print("📄 محتوای فعلی config.py (10 خط اول):")
print("=" * 70)
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:10], 1):
            print(f"{i:3d}: {line.rstrip()}")
    print(f"\n📊 تعداد کل خطوط: {len(lines)}")
except Exception as e:
    print(f"❌ خطا در خواندن فایل: {e}")

print("\n" + "=" * 70)
print("🔨 بازنویسی فایل...")
print("=" * 70)

# محتوای جدید
new_content = '''"""
Econojin Configuration - Pydantic Settings
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
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000,http://127.0.0.1:3001"
    CORS_ALLOW_CREDENTIALS: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./econojin.db"
    DATABASE_ECHO: bool = False
    
    # Security & JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production-abcdef123456"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
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
    
    @property
    def cors_origins_list(self) -> list[str]:
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
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Settings: {settings.ENVIRONMENT} mode")
    print(f"Database: SQLite" if settings.database_is_sqlite else f"Database: PostgreSQL")
    print(f"CORS: {settings.cors_origins_list}")
'''

# نوشتن فایل
try:
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"✅ فایل با موفقیت بازنویسی شد: {config_path}")
    print(f"📊 اندازه فایل: {len(new_content)} bytes")
except Exception as e:
    print(f"❌ خطا در نوشتن فایل: {e}")
    exit(1)

# تأیید بازنویسی
print("\n" + "=" * 70)
print("✅ تأیید محتوای جدید (5 خط اول):")
print("=" * 70)
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines[:5], 1):
            print(f"{i:3d}: {line.rstrip()}")
    
    # بررسی اینکه @lru_cache وجود ندارد
    full_content = ''.join(lines)
    if '@lru_cache' in full_content:
        print("\n❌ هشدار: @lru_cache هنوز در فایل وجود دارد!")
    else:
        print("\n✅ تأیید: @lru_cache در فایل وجود ندارد")
        
    if 'from pydantic_settings import BaseSettings' in full_content:
        print("✅ تأیید: import صحیح وجود دارد")
    else:
        print("❌ هشدار: import صحیح وجود ندارد!")
        
except Exception as e:
    print(f"❌ خطا در تأیید: {e}")

print("\n" + "=" * 70)
print("🚀 حالا بک‌اند را ری‌استارت کنید:")
print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
print("=" * 70)
"""
تنظیمات مرکزی پلتفرم Econojin
مدیریت متغیرهای محیطی با استفاده از Pydantic v2 Settings
سازگار شده با apps/main.py
"""
import logging

logger = logging.getLogger(__name__)
from functools import lru_cache
from typing import List, Optional, Literal
from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    کلاس اصلی تنظیمات برنامه که مقادیر را از فایل .env یا متغیرهای محیطی سیستم عامل می‌خواند.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =========================================================================
    # 1. تنظیمات عمومی برنامه (App Settings)
    # =========================================================================
    PROJECT_NAME: str = Field(default="Econojin Platform", description="نام پروژه")
    VERSION: str = Field(default="2.0.0", description="نسخه اپلیکیشن")
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(default="local", description="محیط اجرای برنامه")
    API_V1_STR: str = Field(default="/api/v1", description="پیشوند مسیرهای API")
    
    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,http://localhost:8000,https://econojin.com",
        description="لیست دامنه‌های مجاز برای CORS"
    )

    @property
    def all_cors_origins(self) -> List[str]:
        """تبدیل رشته CORS به لیست برای استفاده در FastAPI"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # =========================================================================
    # 2. تنظیمات پایگاه داده (Database)
    # =========================================================================
    DATABASE_URL: str = Field(..., description="رشته اتصال به پایگاه داده")
    DB_ECHO: bool = Field(default=False, description="نمایش کوئری‌های SQL در لاگ")

    # =========================================================================
    # 3. تنظیمات امنیت و احراز هویت (Security & Auth)
    # =========================================================================
    SECRET_KEY: str = Field(..., description="کلید محرمانه JWT")
    ALGORITHM: str = Field(default="HS256", description="الگوریتم رمزنگاری JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24, description="مدت زمان انقضای توکن دسترسی")

    # =========================================================================
    # 4. تنظیمات بلاکچین و EcoCoin (Blockchain & Web3)
    # =========================================================================
    BLOCKCHAIN_RPC_URL: str = Field(default="https://rpc-amoy.polygon.technology/", description="آدرس RPC شبکه")
    BLOCKCHAIN_CHAIN_ID: int = Field(default=80002, description="شناسه زنجیره")
    ECOCONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000001", description="آدرس قرارداد EcoCoin")
    ORACLE_CONTRACT_ADDRESS: str = Field(default="0x0000000000000000000000000000000000000002", description="آدرس قرارداد Oracle")
    BACKEND_WALLET_PRIVATE_KEY: Optional[str] = Field(default=None, description="کلید خصوصی کیف پول بک‌اند")

    # =========================================================================
    # 5. تنظیمات هوش مصنوعی (AI & LLM)
    # =========================================================================
    LLM_PROVIDER: Literal["groq", "openai", "gemini", "openrouter", "ollama", "fake"] = Field(default="fake", description="ارائه‌دهنده فعال مدل زبانی")
    LLM_API_KEY: Optional[str] = Field(default=None, description="کلید API ارائه‌دهنده مدل زبانی")
    LLM_MODEL: str = Field(default="llama3-8b-8192", description="نام مدل پیش‌فرض هوش مصنوعی")
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", description="آدرس پایه سرویس Ollama")

    # =========================================================================
    # 6. تنظیمات APIهای خارجی (External APIs)
    # =========================================================================
    OPEN_METEO_URL: str = Field(default="https://api.open-meteo.com/v1", description="آدرس پایه API آب‌وهوا")
    FAO_API_KEY: Optional[str] = Field(default=None, description="کلید API اختیاری FAOSTAT")

    # =========================================================================
    # اعتبارسنجی سراسری (Global Validation)
    # =========================================================================
    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        if self.ENVIRONMENT == "production":
            if self.SECRET_KEY == "super-secret-key-change-in-production-please":
                raise ValueError("لطفاً مقدار SECRET_KEY را در محیط production تغییر دهید.")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
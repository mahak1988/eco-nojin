"""
تنظیمات مرکزی پلتفرم Econojin
مدیریت متغیرهای محیطی با استفاده از Pydantic v2 Settings
"""
from functools import lru_cache
from typing import List, Optional, Literal
from pydantic import Field, model_validator, ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    کلاس اصلی تنظیمات برنامه که مقادیر را از فایل .env یا متغیرهای محیطی سیستم عامل می‌خواند.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # نادیده گرفتن متغیرهای محیطی تعریف‌نشده برای جلوگیری از خطا
    )

    # =========================================================================
    # 1. تنظیمات عمومی برنامه (App Settings)
    # =========================================================================
    APP_NAME: str = Field(default="Econojin API", description="نام اپلیکیشن")
    APP_VERSION: str = Field(default="2.0.0", description="نسخه اپلیکیشن")
    DEBUG: bool = Field(default=False, description="حالت دیباگ (در تولید باید False باشد)")
    ENVIRONMENT: Literal["local", "staging", "production"] = Field(
        default="local", 
        description="محیط اجرای برنامه"
    )

    # =========================================================================
    # 2. تنظیمات پایگاه داده (Database)
    # =========================================================================
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./econojin.db",
        description="رشته اتصال به پایگاه داده (SQLite یا PostgreSQL)"
    )
    DB_ECHO: bool = Field(default=False, description="نمایش کوئری‌های SQL در لاگ (فقط برای توسعه)")

    # =========================================================================
    # 3. تنظیمات امنیت و احراز هویت (Security & Auth)
    # =========================================================================
    SECRET_KEY: str = Field(
        default="super-secret-key-change-in-production-please",
        description="کلید محرمانه برای امضای JWT و نشست‌ها"
    )
    ALGORITHM: str = Field(default="HS256", description="الگوریتم رمزنگاری JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60 * 24, 
        description="مدت زمان انقضای توکن دسترسی به دقیقه (پیش‌فرض: ۲۴ ساعت)"
    )
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:5173,http://localhost:3000,https://econojin.com",
        description="لیست دامنه‌های مجاز برای CORS (با کاما جدا شوند)"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """تبدیل رشته CORS به لیست"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    # =========================================================================
    # 4. تنظیمات بلاکچین و EcoCoin (Blockchain & Web3)
    # =========================================================================
    BLOCKCHAIN_RPC_URL: str = Field(
        default="https://rpc-amoy.polygon.technology/",
        description="آدرس RPC شبکه بلاکچین (مثلاً Polygon Amoy Testnet)"
    )
    BLOCKCHAIN_CHAIN_ID: int = Field(default=80002, description="شناسه زنجیره (Chain ID)")
    
    ECOCONTRACT_ADDRESS: str = Field(
        default="0x0000000000000000000000000000000000000001",
        description="آدرس قرارداد هوشمند EcoCoin"
    )
    ORACLE_CONTRACT_ADDRESS: str = Field(
        default="0x0000000000000000000000000000000000000002",
        description="آدرس قرارداد هوشمند Verification Oracle"
    )
    
    BACKEND_WALLET_PRIVATE_KEY: Optional[str] = Field(
        default=None,
        description="کلید خصوصی کیف پول بک‌اند برای امضای خودکار تراکنش‌ها (بسیار محرمانه)"
    )

    # =========================================================================
    # 5. تنظیمات هوش مصنوعی (AI & LLM)
    # =========================================================================
    LLM_PROVIDER: Literal["groq", "openai", "gemini", "openrouter", "ollama", "fake"] = Field(
        default="fake", 
        description="ارائه‌دهنده فعال مدل زبانی"
    )
    LLM_API_KEY: Optional[str] = Field(
        default=None, 
        description="کلید API ارائه‌دهنده مدل زبانی"
    )
    LLM_MODEL: str = Field(
        default="llama3-8b-8192", 
        description="نام مدل پیش‌فرض هوش مصنوعی"
    )
    OLLAMA_BASE_URL: str = Field(
        default="http://localhost:11434", 
        description="آدرس پایه سرویس Ollama (در صورت استفاده)"
    )

    # =========================================================================
    # 6. تنظیمات APIهای خارجی (External APIs)
    # =========================================================================
    OPEN_METEO_URL: str = Field(
        default="https://api.open-meteo.com/v1", 
        description="آدرس پایه API آب‌وهوای Open-Meteo"
    )
    FAO_API_KEY: Optional[str] = Field(
        default=None, 
        description="کلید API اختیاری برای سرویس‌های FAOSTAT (در صورت نیاز)"
    )

    # =========================================================================
    # اعتبارسنجی سراسری (Global Validation)
    # =========================================================================
    @model_validator(mode='after')
    def validate_production_settings(self) -> 'Settings':
        """
        اطمینان از رعایت الزامات امنیتی در محیط Production
        """
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                raise ValueError("تنظیم DEBUG روی True در محیط production مجاز نیست.")
            if self.SECRET_KEY == "super-secret-key-change-in-production-please":
                raise ValueError("لطفاً مقدار SECRET_KEY را در محیط production تغییر دهید.")
            if not self.BACKEND_WALLET_PRIVATE_KEY:
                # هشدار: در برخی معماری‌ها بک‌اند نیاز به امضا ندارد، اما اگر نیاز دارد این خط فعال شود
                pass # raise ValueError("کلید خصوصی کیف پول بک‌اند در محیط production الزامی است.")
        
        return self


# =============================================================================
# نمونهٔ Singleton برای دسترسی سریع و بهینه به تنظیمات
# =============================================================================
@lru_cache
def get_settings() -> Settings:
    """
    بازگرداندن نمونهٔ کش‌شدهٔ تنظیمات برای جلوگیری از خواندن مکرر فایل .env
    """
    return Settings()


# نمونهٔ سراسری برای استفاده در کل پروژه
settings = get_settings()
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os
import logging

logger = logging.getLogger(__name__)

# ==========================================
# Database Configuration
# ==========================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./apps/econojin.db"  # مسیر دیتابیس درون apps/
)

# Pool Configuration - بهینه‌سازی برای Performance
# نکته: SQLite از pooling پشتیبانی نمی‌کند، بنابراین فقط برای PostgreSQL/MySQL اعمال می‌شود
IS_SQLITE = "sqlite" in DATABASE_URL

POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10")) if not IS_SQLITE else None
MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20")) if not IS_SQLITE else None
POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30")) if not IS_SQLITE else None
POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800")) if not IS_SQLITE else None  # 30 دقیقه

engine_kwargs = {
    "echo": os.getenv("DB_ECHO", "false").lower() == "true",  # Query Logging برای شناسایی Slow Queries
    "pool_pre_ping": True,
}

# اضافه کردن پارامترهای pooling فقط برای دیتابیس‌های غیر از SQLite
if not IS_SQLITE:
    engine_kwargs.update({
        "pool_size": POOL_SIZE,
        "max_overflow": MAX_OVERFLOW,
        "pool_timeout": POOL_TIMEOUT,
        "pool_recycle": POOL_RECYCLE,
    })

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ==========================================
# Base Model
# ==========================================
class Base(DeclarativeBase):
    pass

# ==========================================
# Session Dependency (برای FastAPI)
# ==========================================
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency برای تزریق Session در FastAPI endpoints.
    استفاده: async def my_endpoint(db: AsyncSession = Depends(get_db_session))
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# ==========================================
# Database Initialization
# ==========================================
async def init_db():
    """ایجاد تمام جداول دیتابیس (فقط برای توسعه اولیه)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def close_db():
    """بستن اتصال دیتابیس (در زمان shutdown)."""
    await engine.dispose()

# ============================================================
# Compatibility Aliases (Added by Phase 2 Fix)
# ============================================================

get_db = get_db_session

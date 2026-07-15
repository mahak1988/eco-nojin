from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os

# ==========================================
# Database Configuration
# ==========================================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./apps/econojin.db"  # مسیر دیتابیس درون apps/
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # در Production: False
    pool_pre_ping=True
)

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

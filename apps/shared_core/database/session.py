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

# Alias for backward compatibility
AsyncSessionLocal = async_session_maker

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
    """
    Initialize database using Alembic migrations.
    In production, this should NOT create tables directly.
    Instead, run: alembic upgrade head
    """
    import subprocess
    import sys
    
    # Check if we're in development mode
    is_development = os.getenv("DEBUG", "false").lower() == "true"
    
    if is_development:
        # For development only: try to run migrations
        try:
            logger.info("🔄 Running Alembic migrations...")
            result = subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT
            )
            if result.returncode == 0:
                logger.info("✅ Alembic migrations completed successfully")
            else:
                logger.warning(f"⚠️  Alembic migration failed: {result.stderr}")
                logger.info("Falling back to create_all (development only)")
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            logger.warning(f"⚠️  Could not run migrations: {e}")
            logger.info("Falling back to create_all (development only)")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
    else:
        # Production: Do NOT auto-create tables
        # Tables must be created via explicit migration
        logger.info("ℹ️  Production mode: Tables must be created via 'alembic upgrade head'")

async def close_db():
    """بستن اتصال دیتابیس (در زمان shutdown)."""
    await engine.dispose()

# ============================================================
# Compatibility Aliases (Added by Phase 2 Fix)
# ============================================================

get_db = get_db_session

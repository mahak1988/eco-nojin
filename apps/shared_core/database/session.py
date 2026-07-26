"""Async SQLAlchemy session, engine, and Base.

R20: DATABASE_URL from settings (Pydantic), not os.getenv.
R11: Prefer Alembic in staging/production; create_all only as local bootstrap.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)


def _database_url() -> str:
    try:
        from apps.shared_core.config import settings

        return settings.DATABASE_URL
    except Exception:
        # Bootstrap only if settings cannot load (e.g. incomplete env during tooling)
        return "sqlite+aiosqlite:///./apps/econojin.db"


DATABASE_URL = _database_url()

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_engine() -> AsyncEngine:
    return engine


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def _import_models() -> None:
    from apps.shared_core.database.model_registry import import_all_models

    loaded = import_all_models()
    logger.info("ORM models registered: %s", len(loaded))


async def init_db() -> None:
    """Local bootstrap only. Staging/production must use Alembic (R11)."""
    _import_models()
    try:
        from apps.shared_core.config import settings

        if settings.ENVIRONMENT != "local":
            logger.info("Skipping create_all (ENVIRONMENT=%s); use Alembic", settings.ENVIRONMENT)
            return
    except Exception:
        pass
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()


get_db = get_db_session

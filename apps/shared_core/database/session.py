"""Async SQLAlchemy session, engine, and Base."""

from __future__ import annotations

import logging
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./apps/econojin.db",
)

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
    """Return the shared async engine (used by /health and jobs)."""
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
    """Register ORM models on Base.metadata before create_all."""
    try:
        import apps.api.models.education  # noqa: F401
    except Exception as e:
        logger.debug("education models: %s", e)
    try:
        import apps.api.models.accounting  # noqa: F401
    except Exception as e:
        logger.debug("accounting models: %s", e)
    try:
        import apps.api.models.community  # noqa: F401
    except Exception as e:
        logger.debug("community models: %s", e)
    try:
        import apps.users.models  # noqa: F401
    except Exception as e:
        logger.debug("users models: %s", e)


async def init_db() -> None:
    _import_models()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    await engine.dispose()


get_db = get_db_session

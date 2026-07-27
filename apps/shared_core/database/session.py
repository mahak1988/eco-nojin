"""Async SQLAlchemy session — SQLite fallback when Postgres driver missing."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

DEFAULT_SQLITE = "sqlite+aiosqlite:///./apps/econojin.db"


def _has_asyncpg() -> bool:
    try:
        import asyncpg  # noqa: F401

        return True
    except ImportError:
        return False


def _resolve_database_url() -> str:
    raw = None
    try:
        from apps.shared_core.config import settings

        raw = settings.DATABASE_URL
    except Exception:
        import os

        raw = os.getenv("DATABASE_URL")

    if not raw or "***" in str(raw) or not str(raw).strip():
        logger.info("DATABASE_URL unset — using local SQLite")
        return DEFAULT_SQLITE

    url = str(raw).strip()

    if "postgres" in url.lower():
        if "+asyncpg" in url and not _has_asyncpg():
            logger.info("asyncpg not installed — local SQLite")
            return DEFAULT_SQLITE
        if url.startswith("postgresql://") or url.startswith("postgres://"):
            if "+asyncpg" not in url and "+aiosqlite" not in url:
                try:
                    from apps.shared_core.config import settings

                    if settings.ENVIRONMENT == "local":
                        logger.info("Local Postgres URL without async driver — SQLite")
                        return DEFAULT_SQLITE
                except Exception:
                    return DEFAULT_SQLITE

    if url.startswith("sqlite://") and "+aiosqlite" not in url:
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url


DATABASE_URL = _resolve_database_url()

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

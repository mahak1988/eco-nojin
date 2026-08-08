"""Async SQLAlchemy session — Postgres preferred when forced/available."""

from __future__ import annotations

import logging
import os
from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

logger = logging.getLogger(__name__)

DEFAULT_SQLITE = "sqlite+aiosqlite:///./apps/econojin.db"


def _has_asyncpg() -> bool:
    try:
        import asyncpg  # noqa: F401

        return True
    except ImportError:
        return False


def _force_postgres() -> bool:
    v = (os.getenv("FORCE_POSTGRES") or os.getenv("USE_POSTGRES") or "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _to_async_postgres(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _resolve_database_url() -> str:
    raw = None
    try:
        from apps.shared_core.config import settings

        raw = settings.DATABASE_URL
    except Exception:
        raw = os.getenv("DATABASE_URL")

    if not raw or "***" in str(raw) or not str(raw).strip():
        logger.info("DATABASE_URL unset — using local SQLite")
        return DEFAULT_SQLITE

    url = str(raw).strip()

    if "postgres" in url.lower():
        url = _to_async_postgres(url)
        if "+asyncpg" in url and not _has_asyncpg():
            if _force_postgres():
                raise RuntimeError(
                    "FORCE_POSTGRES=1 but asyncpg is not installed. pip install asyncpg"
                )
            logger.info("asyncpg not installed — local SQLite")
            return DEFAULT_SQLITE
        # Phase 3: allow Postgres on local when forced OR when asyncpg present and URL is explicit async
        if _force_postgres():
            logger.info(
                "FORCE_POSTGRES=1 — using Postgres: %s", url.split("@")[-1] if "@" in url else url
            )
            return url
        try:
            from apps.shared_core.config import settings

            if settings.ENVIRONMENT == "local" and not _force_postgres():
                # keep SQLite for zero-friction local unless user opts in
                if os.getenv("DATABASE_URL", "").strip() and _has_asyncpg() and "+asyncpg" in url:
                    # Explicit async Postgres URL in env → honor it
                    if "localhost" in url or "127.0.0.1" in url or "postgres:" in url:
                        logger.info("Local Postgres URL detected with asyncpg — using Postgres")
                        return url
                logger.info(
                    "Local without FORCE_POSTGRES — SQLite (set FORCE_POSTGRES=1 to use PG)"
                )
                return DEFAULT_SQLITE
        except Exception:
            if not _force_postgres():
                return DEFAULT_SQLITE

    if url.startswith("sqlite://") and "+aiosqlite" not in url:
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url


DATABASE_URL = _resolve_database_url()

_engine_kwargs: dict = {"echo": False, "pool_pre_ping": True}
if "sqlite" not in DATABASE_URL:
    _engine_kwargs.update({"pool_size": 5, "max_overflow": 10})

engine: AsyncEngine = create_async_engine(DATABASE_URL, **_engine_kwargs)

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


async def _table_cols(conn, table: str) -> set[str]:
    try:
        rows = await conn.execute(text(f"PRAGMA table_info({table})"))
        return {r[1] for r in rows.fetchall()}
    except Exception:
        return set()


async def _add_col(conn, table: str, name: str, ddl: str, existing: set[str]) -> None:
    if name in existing:
        return
    try:
        await conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {ddl}"))
        logger.info("SQLite schema patch: %s.%s added", table, name)
        existing.add(name)
    except Exception as e:
        logger.warning("SQLite patch %s.%s failed: %s", table, name, e)


async def _sqlite_schema_patches(conn) -> None:
    if "sqlite" not in str(engine.url):
        return

    users = await _table_cols(conn, "users")
    if users:
        await _add_col(conn, "users", "phone", "phone VARCHAR(40)", users)
        await _add_col(conn, "users", "organization", "organization VARCHAR(255)", users)
        await _add_col(conn, "users", "role", "role VARCHAR(40) DEFAULT 'farmer'", users)

    crops = await _table_cols(conn, "crops")
    if crops:
        crop_cols = [
            ("planting_method", "planting_method VARCHAR(80)"),
            ("row_spacing_cm", "row_spacing_cm FLOAT"),
            ("plant_spacing_cm", "plant_spacing_cm FLOAT"),
            ("sowing_depth_cm", "sowing_depth_cm FLOAT"),
            ("seed_rate_kg_ha", "seed_rate_kg_ha FLOAT"),
            ("irrigation_method", "irrigation_method VARCHAR(80)"),
            ("irrigation_interval_days", "irrigation_interval_days INTEGER"),
            ("kc_mid", "kc_mid FLOAT"),
            ("fertilizer_n_kg_ha", "fertilizer_n_kg_ha FLOAT"),
            ("fertilizer_p_kg_ha", "fertilizer_p_kg_ha FLOAT"),
            ("fertilizer_k_kg_ha", "fertilizer_k_kg_ha FLOAT"),
            ("soil_ph_min", "soil_ph_min FLOAT"),
            ("soil_ph_max", "soil_ph_max FLOAT"),
            ("harvest_method", "harvest_method VARCHAR(80)"),
            ("harvest_moisture_pct", "harvest_moisture_pct FLOAT"),
            ("common_pests", "common_pests TEXT"),
            ("common_diseases", "common_diseases TEXT"),
            ("care_notes", "care_notes TEXT"),
        ]
        for name, ddl in crop_cols:
            await _add_col(conn, "crops", name, ddl, crops)


async def init_db() -> None:
    _import_models()
    try:
        from apps.shared_core.config import settings

        if settings.ENVIRONMENT != "local" and not _force_postgres():
            logger.info("Skipping create_all (ENVIRONMENT=%s); use Alembic", settings.ENVIRONMENT)
            return
        if settings.ENVIRONMENT != "local" and "postgres" in DATABASE_URL:
            logger.info("Skipping create_all on Postgres staging/prod — use alembic upgrade head")
            return
    except Exception:
        pass
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await _sqlite_schema_patches(conn)


async def close_db() -> None:
    await engine.dispose()


get_db = get_db_session

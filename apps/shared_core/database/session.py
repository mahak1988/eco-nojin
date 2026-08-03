"""Async SQLAlchemy session — PostgreSQL + PostGIS preferred with SQLite fallback."""

from __future__ import annotations

import logging
import os
from typing import AsyncGenerator, Optional

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

# ---------------------------------------------------------------------------
# Engine configuration values — configurable via env
# ---------------------------------------------------------------------------
_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "40"))
_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", "30"))
_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour


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
    """Normalize a postgres:// URL to postgresql+asyncpg://."""
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def _resolve_database_url() -> str:
    """Resolve DATABASE_URL with PostgreSQL priority.

    Priority:
    1. FORCE_POSTGRES=1   → requires asyncpg, raises if missing
    2. DATABASE_URL from settings/env with postgres in URL → use PostgreSQL
    3. ENVIRONMENT=production/staging with Postgres in URL → use PostgreSQL
    4. Local environment     → PostgreSQL if URL explicitly postgres, else SQLite
    5. Fallback              → SQLite
    """
    raw: Optional[str] = None

    # Try pydantic settings first
    try:
        from apps.shared_core.config import settings
        raw = settings.DATABASE_URL
    except Exception:
        raw = os.getenv("DATABASE_URL")

    # Empty/masked URL → SQLite
    if not raw or "***" in str(raw) or not str(raw).strip():
        logger.info("DATABASE_URL unset or masked → using local SQLite")
        return DEFAULT_SQLITE

    url = str(raw).strip()

    # PostgreSQL path
    if "postgres" in url.lower():
        url = _to_async_postgres(url)

        # Check asyncpg availability
        if not _has_asyncpg():
            if _force_postgres():
                raise RuntimeError(
                    "FORCE_POSTGRES=1 but asyncpg is not installed. "
                    "Install: pip install asyncpg"
                )
            logger.info("asyncpg not installed → falling back to SQLite")
            return DEFAULT_SQLITE

        # Force Postgres → always use it
        if _force_postgres():
            logger.info(
                "FORCE_POSTGRES=1 → using PostgreSQL: %s",
                url.split("@")[-1] if "@" in url else url,
            )
            return url

        # Check environment context
        try:
            from apps.shared_core.config import settings

            if settings.ENVIRONMENT in ("production", "staging"):
                logger.info(
                    "PostgreSQL selected for %s environment", settings.ENVIRONMENT
                )
                return url

            if settings.ENVIRONMENT == "local":
                # Local: use PostgreSQL if explicitly configured with a non-localhost URL
                # (implies intent to connect to a container or remote PG)
                if "localhost" in url or "127.0.0.1" in url:
                    logger.info(
                        "Local environment with local PostgreSQL URL → using PostgreSQL"
                    )
                    return url
                logger.info(
                    "Local environment → SQLite fallback (set FORCE_POSTGRES=1 to use PG)"
                )
                return DEFAULT_SQLITE
        except Exception:
            # If settings aren't available, trust the URL if it's clearly PostgreSQL
            if "+asyncpg" in url:
                return url
            return DEFAULT_SQLITE

    # SQLite path
    if url.startswith("sqlite://") and "+aiosqlite" not in url:
        url = url.replace("sqlite://", "sqlite+aiosqlite://", 1)

    return url


# ---------------------------------------------------------------------------
# Engine creation
# ---------------------------------------------------------------------------
DATABASE_URL = _resolve_database_url()

_IS_POSTGRES = "postgresql" in DATABASE_URL
_IS_SQLITE = "sqlite" in DATABASE_URL

_engine_kwargs: dict = {
    "echo": os.getenv("DB_ECHO", "").lower() in ("1", "true", "yes"),
    "pool_pre_ping": True,
}

if _IS_POSTGRES:
    _engine_kwargs.update({
        "pool_size": _POOL_SIZE,
        "max_overflow": _MAX_OVERFLOW,
        "pool_timeout": _POOL_TIMEOUT,
        "pool_recycle": _POOL_RECYCLE,
        # PostgreSQL‑specific: wait for connections instead of failing fast
        "pool_pre_ping": True,
        # Connection arguments for production
        "connect_args": {
            "server_settings": {
                "application_name": "econojin",
                "timezone": "UTC",
            },
        },
    })
elif _IS_SQLITE:
    _engine_kwargs.update({
        "connect_args": {"check_same_thread": False},
    })

logger.info(
    "Database engine: %s (pool=%s overflow=%s timeout=%ss)",
    "PostgreSQL" if _IS_POSTGRES else "SQLite",
    _engine_kwargs.get("pool_size", "N/A"),
    _engine_kwargs.get("max_overflow", "N/A"),
    _engine_kwargs.get("pool_timeout", "N/A"),
)

engine: AsyncEngine = create_async_engine(DATABASE_URL, **_engine_kwargs)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


def get_engine() -> AsyncEngine:
    return engine


def is_postgres() -> bool:
    """Check if the current database is PostgreSQL."""
    return _IS_POSTGRES


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session with automatic commit/rollback."""
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
    logger.info("ORM models registered: %d", len(loaded))


# ---------------------------------------------------------------------------
# SQLite schema patches (zero-downtime additions for development)
# ---------------------------------------------------------------------------
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
    """Apply runtime schema patches for SQLite dev environments."""
    if not _IS_SQLITE:
        return

    users = await _table_cols(conn, "users")
    if users:
        await _add_col(conn, "users", "phone", "phone VARCHAR(40)", users)
        await _add_col(conn, "users", "organization", "organization VARCHAR(255)", users)
        await _add_col(conn, "users", "role", "role VARCHAR(40) DEFAULT 'farmer'", users)

    courses = await _table_cols(conn, "courses")
    if courses:
        await _add_col(conn, "courses", "instructor_id", "instructor_id VARCHAR(50)", courses)
        await _add_col(conn, "courses", "instructor", "instructor VARCHAR(255)", courses)
        await _add_col(conn, "courses", "is_active", "is_active BOOLEAN DEFAULT 1", courses)

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


# ---------------------------------------------------------------------------
# Database initialization
# ---------------------------------------------------------------------------
async def init_db() -> None:
    _import_models()

    # For PostgreSQL production/staging, skip auto-create (use Alembic)
    if _IS_POSTGRES:
        try:
            from apps.shared_core.config import settings
            if settings.ENVIRONMENT in ("production", "staging"):
                logger.info(
                    "Skipping create_all (ENVIRONMENT=%s on PostgreSQL) — use Alembic migrations",
                    settings.ENVIRONMENT,
                )
                return
        except Exception:
            pass

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        if _IS_SQLITE:
            await _sqlite_schema_patches(conn)


async def close_db() -> None:
    await engine.dispose()
    logger.info("Database engine disposed")


# Alias for backward compatibility
get_db = get_db_session

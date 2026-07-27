"""Alembic environment — prefers local SQLite when Postgres driver missing."""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except Exception:
    pass

DEFAULT_SQLITE = "sqlite:///./apps/econojin.db"


def _has_postgres_driver() -> bool:
    try:
        import psycopg  # noqa: F401

        return True
    except ImportError:
        pass
    try:
        import psycopg2  # noqa: F401

        return True
    except ImportError:
        return False


def to_sync_url(url: str | None) -> str:
    env = (os.getenv("ENVIRONMENT") or "local").lower()
    force_sqlite = os.getenv("ALEMBIC_FORCE_SQLITE", "").lower() in ("1", "true", "yes")

    if force_sqlite or (env == "local" and os.getenv("ALEMBIC_USE_SQLITE", "1") != "0"):
        # Local default: avoid Postgres driver requirement unless explicitly disabled
        if not url or "***" in str(url) or "postgres" in str(url).lower():
            if not _has_postgres_driver() or force_sqlite or env == "local":
                if not url or "postgres" in str(url or "").lower() or "***" in str(url or ""):
                    return DEFAULT_SQLITE

    if not url or not str(url).strip() or "***" in str(url):
        return DEFAULT_SQLITE

    u = str(url).strip()

    if u.startswith("sqlite+aiosqlite:"):
        return u.replace("sqlite+aiosqlite:", "sqlite:", 1)

    if "+asyncpg" in u:
        if _has_postgres_driver():
            try:
                import psycopg  # noqa: F401

                return u.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
            except ImportError:
                return u.replace("postgresql+asyncpg://", "postgresql+psycopg2://", 1)
        return DEFAULT_SQLITE

    if u.startswith("postgres://"):
        u = "postgresql://" + u[len("postgres://") :]

    if u.startswith("postgresql://") and not _has_postgres_driver():
        print("  [alembic] No psycopg/psycopg2 — falling back to SQLite for migrations")
        return DEFAULT_SQLITE

    return u


def get_url() -> str:
    raw = os.getenv("DATABASE_URL")
    if not raw:
        try:
            from apps.shared_core.config import settings

            raw = getattr(settings, "DATABASE_URL", None)
        except Exception:
            raw = None
    if not raw:
        raw = context.config.get_main_option("sqlalchemy.url")
    return to_sync_url(raw)


try:
    from apps.shared_core.database.session import Base
    from apps.shared_core.database.model_registry import MODEL_MODULES, import_all_models

    import_all_models(MODEL_MODULES)
    for extra in (
        "apps.api.models.education",
        "apps.api.models.community",
        "apps.shared_core.rbac.models",
    ):
        try:
            __import__(extra, fromlist=["*"])
        except ImportError:
            pass
except Exception as e:
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()  # type: ignore
    print(f"  [alembic] Warning: Could not import Base/models: {e}")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()
    print(f"  [alembic] using url dialect: {configuration['sqlalchemy.url'].split(':', 1)[0]}")

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

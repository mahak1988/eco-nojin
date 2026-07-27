"""Alembic environment — sync driver URLs (R11)."""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Load .env early so DATABASE_URL is visible
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except Exception:
    pass


def to_sync_url(url: str | None) -> str:
    """Alembic needs a sync DBAPI. Convert async SQLAlchemy URLs."""
    if not url or not str(url).strip() or "***" in str(url):
        return "sqlite:///./apps/econojin.db"

    u = str(url).strip()

    # SQLite async → sync
    if u.startswith("sqlite+aiosqlite:"):
        return u.replace("sqlite+aiosqlite:", "sqlite:", 1)

    # Postgres async → psycopg3 (package: psycopg[binary]) preferred over psycopg2
    if "+asyncpg" in u:
        u = u.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
        u = u.replace("+asyncpg", "")
        return u

    # Bare postgres:// → postgresql://
    if u.startswith("postgres://"):
        u = "postgresql://" + u[len("postgres://") :]

    return u


def get_url() -> str:
    raw = os.getenv("DATABASE_URL")
    if not raw:
        try:
            from apps.shared_core.config import settings

            raw = settings.DATABASE_URL
        except Exception:
            raw = None
    if not raw:
        raw = context.config.get_main_option("sqlalchemy.url")
    return to_sync_url(raw)


# Import metadata after path setup; tolerate missing optional drivers at import time
try:
    from apps.shared_core.database.session import Base
    from apps.shared_core.database.model_registry import MODEL_MODULES, import_all_models

    import_all_models(MODEL_MODULES)
    for extra in ("apps.api.models.education", "apps.api.models.community"):
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

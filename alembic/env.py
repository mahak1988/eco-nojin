"""Alembic environment — uses shared model registry (R11)."""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

try:
    from apps.shared_core.database.session import Base
    from apps.shared_core.database.model_registry import import_all_models, MODEL_MODULES

    import_all_models(MODEL_MODULES)
    # Ensure education is present for migrations
    for extra in ("apps.api.models.education", "apps.api.models.community"):
        try:
            __import__(extra, fromlist=["*"])
        except ImportError:
            pass
except ImportError as e:
    from sqlalchemy.orm import declarative_base

    Base = declarative_base()
    print(f"  [alembic] Warning: Could not import Base: {e}")

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    try:
        from apps.shared_core.config import settings

        url = settings.DATABASE_URL
        # Alembic sync engine: strip +aiosqlite / +asyncpg for offline tools if needed
        return url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg2") if False else url
    except Exception:
        url = os.getenv("DATABASE_URL")
        if url:
            return url
        return config.get_main_option("sqlalchemy.url")


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

    # For async URLs, use a sync variant for Alembic classic engine
    url = configuration["sqlalchemy.url"]
    if url.startswith("sqlite+aiosqlite"):
        configuration["sqlalchemy.url"] = url.replace("sqlite+aiosqlite", "sqlite")
    elif "+asyncpg" in url:
        configuration["sqlalchemy.url"] = url.replace("+asyncpg", "")

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

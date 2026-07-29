"""Alembic env — uses shared Base metadata; URL from DATABASE_URL or sqlite default."""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models so metadata is populated
from apps.shared_core.database.model_registry import import_all_models  # noqa: E402
from apps.shared_core.database.session import Base  # noqa: E402

import_all_models()
target_metadata = Base.metadata


def get_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url or "***" in url:
        return "sqlite:///./apps/econojin.db"
    # Alembic uses sync drivers
    if url.startswith("sqlite+aiosqlite://"):
        return url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""Alembic Environment Configuration"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from apps.shared_core.database.session import Base
    import apps.shared_core.models  # noqa: F401
except ImportError as e:
    print(f"Warning: Could not import Base from shared_core: {e}")
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Auto-import all domain models for Alembic autogenerate
# This ensures all SQLAlchemy models are discovered during migration generation
model_imports = [
    "apps.users.models",
    "apps.simulation.models",
    "apps.api.models",
    "apps.shared_ai.models",
    "apps.shared_knowledge.models",
    "apps.admin_panel.models",
    "apps.ai_agents.models",
    "apps.cms.models",
]

for module_path in model_imports:
    try:
        __import__(module_path)
        print(f"✓ Imported: {module_path}")
    except ImportError as e:
        print(f"⚠ Could not import {module_path}: {e}")
    except Exception as e:
        print(f"⚠ Error importing {module_path}: {e}")

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode.
    
    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.
    
    Calls to context.configure() here will update the target_metadata
    for SQL generation.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, 
        target_metadata=target_metadata, 
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode.
    
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

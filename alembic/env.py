"""
Alembic Environment Configuration
===================================
Adapted from fastapi/full-stack-fastapi-template with proper import paths
for the Econojin project structure.
"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Import Base and all models so Alembic can detect them
try:
    from apps.shared_core.database.session import Base
    
    # Auto-import all model modules to register them with SQLAlchemy metadata
    model_modules = [
        "apps.users.models",
        "apps.ai_agents.models",
        "apps.simulation.models",
        "apps.admin_panel.models",
        "apps.shared_knowledge.models",
        "apps.shared_sim.models",
        "apps.api.models.accounting",
        "apps.api.models.agriculture_school",
    ]
    for mod_name in model_modules:
        try:
            __import__(mod_name, fromlist=["*"])
        except ImportError as e:
            print(f"  [alembic] Model module not found (optional): {mod_name} - {e}")
except ImportError as e:
    from sqlalchemy.orm import declarative_base
    Base = declarative_base()
    print(f"  [alembic] Warning: Could not import Base from shared_core: {e}")

# Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target metadata
target_metadata = Base.metadata

# Database URL from environment or config
def get_url():
    """Get database URL from environment or alembic.ini."""
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
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
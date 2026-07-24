"""Alembic Environment Configuration"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from apps.shared_core.database.session import Base
    import apps.shared_core.models  # noqa: F401
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Auto-import all models from apps directory
try:
    # Core models
    import apps.users.models  # noqa: F401
    import apps.ai_agents.models  # noqa: F401
    import apps.simulation.models  # noqa: F401
    import apps.accounting.models  # noqa: F401
    import apps.education.models  # noqa: F401
    import apps.decision_support.models  # noqa: F401
    import apps.knowledge_graph.models  # noqa: F401
    
    # Shared modules
    import apps.shared_sim.models  # noqa: F401
    import apps.shared_ai.models  # noqa: F401
    import apps.shared_knowledge.models  # noqa: F401
    
    print("✅ All models imported successfully")
except ImportError as e:
    print(f"⚠️  Warning importing models: {e}")

target_metadata = Base.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_item=render_item,
            include_schemas=True
        )
        with context.begin_transaction():
            context.run_migrations()

def render_item(type_, obj, autogen_context):
    """Custom render function to handle SQLite incompatibilities"""
    # Skip all operations on existing tables - we only want to add new tables
    return False

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

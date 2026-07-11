"""Alembic Environment Configuration"""
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from apps.app.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Auto-import all db_models
try:
    from apps.app.domains.dashboard.models.db_models import *
    from apps.app.domains.hydrology.models.db_models import *
    from apps.app.domains.iot.models.db_models import *
    from apps.app.domains.logframe.models.db_models import *
    from apps.app.domains.mrv.models.db_models import *
    from apps.app.domains.pilots.models.db_models import *
    from apps.app.domains.psychology.models.db_models import *
    from apps.app.domains.remote_sensing.models.db_models import *
    from apps.app.domains.safeguards.models.db_models import *
    from apps.app.domains.training.models.db_models import *
    from apps.app.domains.lms.models.db_models import *
except ImportError as e:
    print(f"Warning: {e}")

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
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

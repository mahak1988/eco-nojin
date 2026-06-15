"""
Database Configuration for Econojin Platform
Optimized for both PostgreSQL (production) and SQLite (development/testing)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os

# Database URL - supports both PostgreSQL and SQLite
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./econojin.db"
)

# Detect database type
is_postgresql = "postgresql" in SQLALCHEMY_DATABASE_URL

# Engine configuration - optimized for database type
if is_postgresql:
    # PostgreSQL-specific optimizations
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=30,
        pool_pre_ping=True,
        pool_recycle=3600,
        pool_timeout=30,
        echo=False
    )
else:
    # SQLite configuration (for development/testing)
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {},
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for database sessions with proper cleanup"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================================================================
# Database initialization helpers
# ========================================================================
def create_tables():
    """Create all database tables"""
    # Import all models to ensure they're registered
    try:
        from api.domains.dashboard.models import db_models
        from api.domains.hydrology.models import db_models
        from api.domains.iot.models import db_models
        from api.domains.logframe.models import db_models
        from api.domains.mrv.models import db_models
        from api.domains.pilots.models import db_models
        from api.domains.psychology.models import db_models
        from api.domains.remote_sensing.models import db_models
        from api.domains.safeguards.models import db_models
        from api.domains.training.models import db_models
        from api.domains.lms.models import db_models
        from api.domains.drought.models import db_models
        from api.domains.soil_water.models import db_models
        from api.domains.financial.models import db_models
    except ImportError as e:
        print(f"Warning: Could not import some models: {e}")
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def check_connection():
    """Test database connection"""
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print(f"✅ Database connection successful: {SQLALCHEMY_DATABASE_URL}")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Quick test when run directly
    print("Testing database configuration...")
    if check_connection():
        print("Creating tables...")
        create_tables()

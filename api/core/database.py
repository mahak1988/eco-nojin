"""
Database configuration and initialization
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from api.core.config import settings


# Engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

# Session
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Base class for models
class Base(DeclarativeBase):
    pass


# Dependency for FastAPI
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Initialize database
async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        # Import all models
        from api.modules import all_models  # noqa: F401
        
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
    
    return True
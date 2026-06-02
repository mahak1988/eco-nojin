from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = None
AsyncSessionLocal = None

async def init_db():
    global engine, AsyncSessionLocal
    from api.core.config import settings

    register_models()
    connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    engine = create_async_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ Database initialized: {settings.DATABASE_URL}")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def register_models():
    """Import all ORM models so metadata.create_all sees every table."""
    from api.modules.calendar import models as calendar_models  # noqa: F401
    from api.modules.auth import models as auth_models  # noqa: F401
    from api.modules.farmer import models as farmer_models  # noqa: F401
    from api.modules.store import models as store_models  # noqa: F401

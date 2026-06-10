from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///./econojin.db")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(lambda m: None)  # placeholder

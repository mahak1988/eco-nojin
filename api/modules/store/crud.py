from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.store.models import StoreItem
from api.modules.store.schemas import StoreItemCreate, StoreItemUpdate


async def list_items(db: AsyncSession, skip: int = 0, limit: int = 50):
    total = (await db.execute(select(func.count()).select_from(StoreItem))).scalar_one()
    result = await db.execute(
        select(StoreItem).offset(skip).limit(limit).order_by(StoreItem.id.desc())
    )
    return list(result.scalars().all()), total


async def get_item(db: AsyncSession, item_id: int) -> StoreItem | None:
    r = await db.execute(select(StoreItem).where(StoreItem.id == item_id))
    return r.scalar_one_or_none()


async def create_item(db: AsyncSession, data: StoreItemCreate) -> StoreItem:
    item = StoreItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def update_item(db: AsyncSession, item_id: int, data: StoreItemUpdate) -> StoreItem | None:
    item = await get_item(db, item_id)
    if not item:
        return None
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item_id: int) -> bool:
    item = await get_item(db, item_id)
    if not item:
        return False
    await db.delete(item)
    await db.commit()
    return True

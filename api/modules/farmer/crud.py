from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.farmer.models import Farmer
from api.modules.farmer.schemas import FarmerCreate, FarmerUpdate


async def list_farmers(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> tuple[list[Farmer], int]:
    count_result = await db.execute(select(func.count()).select_from(Farmer))
    total = count_result.scalar_one()
    result = await db.execute(select(Farmer).offset(skip).limit(limit).order_by(Farmer.id.desc()))
    return list(result.scalars().all()), total


async def get_farmer(db: AsyncSession, farmer_id: int) -> Farmer | None:
    result = await db.execute(select(Farmer).where(Farmer.id == farmer_id))
    return result.scalar_one_or_none()


async def create_farmer(db: AsyncSession, data: FarmerCreate) -> Farmer:
    farmer = Farmer(**data.model_dump())
    db.add(farmer)
    await db.commit()
    await db.refresh(farmer)
    return farmer


async def update_farmer(db: AsyncSession, farmer_id: int, data: FarmerUpdate) -> Farmer | None:
    farmer = await get_farmer(db, farmer_id)
    if not farmer:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(farmer, key, value)
    await db.commit()
    await db.refresh(farmer)
    return farmer


async def delete_farmer(db: AsyncSession, farmer_id: int) -> bool:
    farmer = await get_farmer(db, farmer_id)
    if not farmer:
        return False
    await db.delete(farmer)
    await db.commit()
    return True

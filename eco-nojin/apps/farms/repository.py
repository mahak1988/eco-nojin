"""Farm data access."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.farms.models import Farm
from apps.farms.schemas import FarmCreate, FarmUpdate


class FarmRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        owner_id: int | None = None,
    ) -> tuple[Sequence[Farm], int]:
        q = select(Farm).where(Farm.is_deleted.is_(False))
        count_q = select(func.count()).select_from(Farm).where(Farm.is_deleted.is_(False))
        if search:
            like = f"%{search}%"
            q = q.where(Farm.name.ilike(like))
            count_q = count_q.where(Farm.name.ilike(like))
        if owner_id is not None:
            q = q.where(Farm.owner_id == owner_id)
            count_q = count_q.where(Farm.owner_id == owner_id)
        total = int((await self.session.execute(count_q)).scalar_one())
        result = await self.session.execute(
            q.order_by(Farm.id.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all(), total

    async def get(self, farm_id: int) -> Farm | None:
        result = await self.session.execute(
            select(Farm).where(Farm.id == farm_id, Farm.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def create(self, data: FarmCreate, owner_id: int | None = None) -> Farm:
        farm = Farm(
            name=data.name,
            description=data.description,
            region=data.region,
            area_ha=data.area_ha,
            latitude=data.latitude,
            longitude=data.longitude,
            geojson=data.geojson,
            owner_id=owner_id,
            created_by=owner_id,
        )
        self.session.add(farm)
        await self.session.flush()
        await self.session.refresh(farm)
        return farm

    async def update(self, farm: Farm, data: FarmUpdate) -> Farm:
        for k, v in data.model_dump(exclude_unset=True).items():
            setattr(farm, k, v)
        await self.session.flush()
        await self.session.refresh(farm)
        return farm

    async def soft_delete(self, farm: Farm) -> None:
        farm.is_deleted = True
        farm.is_active = False
        await self.session.flush()

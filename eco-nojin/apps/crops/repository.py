"""Crop repository."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.crops.models import Crop
from apps.crops.schemas import CropCreate


class CropRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ) -> tuple[Sequence[Crop], int]:
        q = select(Crop).where(Crop.is_deleted.is_(False), Crop.is_active.is_(True))
        cq = select(func.count()).select_from(Crop).where(
            Crop.is_deleted.is_(False), Crop.is_active.is_(True)
        )
        if search:
            like = f"%{search}%"
            q = q.where(Crop.name.ilike(like) | Crop.name_fa.ilike(like))
            cq = cq.where(Crop.name.ilike(like) | Crop.name_fa.ilike(like))
        if category:
            q = q.where(Crop.category == category)
            cq = cq.where(Crop.category == category)
        total = int((await self.session.execute(cq)).scalar_one())
        rows = await self.session.execute(q.order_by(Crop.name).offset(skip).limit(limit))
        return rows.scalars().all(), total

    async def get(self, crop_id: int) -> Optional[Crop]:
        r = await self.session.execute(
            select(Crop).where(Crop.id == crop_id, Crop.is_deleted.is_(False))
        )
        return r.scalar_one_or_none()

    async def create(self, data: CropCreate) -> Crop:
        crop = Crop(**data.model_dump())
        self.session.add(crop)
        await self.session.flush()
        await self.session.refresh(crop)
        return crop

    async def count(self) -> int:
        r = await self.session.execute(
            select(func.count()).select_from(Crop).where(Crop.is_deleted.is_(False))
        )
        return int(r.scalar_one())

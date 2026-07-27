"""Crop service."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.crops.repository import CropRepository
from apps.crops.schemas import CropCreate, CropResponse
from apps.crops.seed_data import RAW_CROPS
from apps.shared_core.schemas.pagination import build_meta, page_to_offset


def _seed_items() -> list[CropCreate]:
    return [
        CropCreate(
            name=n,
            name_fa=nf,
            scientific_name=sci,
            category=cat,
            season=season,
            water_need_mm=float(w),
            growth_days=int(d),
            description=desc,
        )
        for n, nf, sci, cat, season, w, d, desc in RAW_CROPS
    ]


class CropService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = CropRepository(session)

    async def list_crops(
        self,
        *,
        page: int = 1,
        size: int = 50,
        search: Optional[str] = None,
        category: Optional[str] = None,
    ):
        skip = page_to_offset(page, size)
        rows, total = await self.repo.list(skip=skip, limit=size, search=search, category=category)
        items = [CropResponse.model_validate(r) for r in rows]
        return items, build_meta(total, page, size)

    async def get(self, crop_id: int) -> CropResponse:
        crop = await self.repo.get(crop_id)
        if not crop:
            raise ValueError("CROP_NOT_FOUND")
        return CropResponse.model_validate(crop)

    async def seed_demo(self, force: bool = False) -> int:
        count = await self.repo.count()
        if count >= 100 and not force:
            return 0
        if force and count > 0:
            # only fill missing names
            existing_names = {r.name for r in (await self.repo.list(skip=0, limit=500))[0]}
        else:
            existing_names = set()
        n = 0
        for item in _seed_items():
            if item.name in existing_names:
                continue
            await self.repo.create(item)
            n += 1
        return n

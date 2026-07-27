"""Crop service."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.crops.repository import CropRepository
from apps.crops.schemas import CropCreate, CropResponse
from apps.shared_core.schemas.pagination import build_meta, page_to_offset

SEED_CROPS = [
    CropCreate(
        name="Wheat",
        name_fa="گندم",
        scientific_name="Triticum aestivum",
        category="cereal",
        season="winter",
        water_need_mm=450,
        growth_days=150,
        description="Staple cereal for temperate climates",
    ),
    CropCreate(
        name="Barley",
        name_fa="جو",
        scientific_name="Hordeum vulgare",
        category="cereal",
        season="winter",
        water_need_mm=380,
        growth_days=120,
    ),
    CropCreate(
        name="Corn",
        name_fa="ذرت",
        scientific_name="Zea mays",
        category="cereal",
        season="summer",
        water_need_mm=550,
        growth_days=110,
    ),
    CropCreate(
        name="Tomato",
        name_fa="گوجه‌فرنگی",
        scientific_name="Solanum lycopersicum",
        category="vegetable",
        season="summer",
        water_need_mm=600,
        growth_days=90,
    ),
    CropCreate(
        name="Alfalfa",
        name_fa="یونجه",
        scientific_name="Medicago sativa",
        category="forage",
        season="perennial",
        water_need_mm=800,
        growth_days=365,
    ),
    CropCreate(
        name="Saffron",
        name_fa="زعفران",
        scientific_name="Crocus sativus",
        category="spice",
        season="autumn",
        water_need_mm=300,
        growth_days=200,
    ),
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

    async def seed_demo(self) -> int:
        if await self.repo.count() > 0:
            return 0
        n = 0
        for item in SEED_CROPS:
            await self.repo.create(item)
            n += 1
        return n

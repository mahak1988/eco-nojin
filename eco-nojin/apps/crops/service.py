"""Crop service + irrigation calculator."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.crops.agronomy_defaults import CATEGORY_DEFAULTS
from apps.crops.repository import CropRepository
from apps.crops.schemas import CropCreate, CropResponse, IrrigationCalcRequest, IrrigationCalcResponse
from apps.crops.seed_data import RAW_CROPS
from apps.shared_core.schemas.pagination import build_meta, page_to_offset


def _seed_items() -> list[CropCreate]:
    items: list[CropCreate] = []
    for n, nf, sci, cat, season, w, d, desc in RAW_CROPS:
        defaults = CATEGORY_DEFAULTS.get(cat, CATEGORY_DEFAULTS.get("cereal", {})).copy()
        items.append(
            CropCreate(
                name=n,
                name_fa=nf,
                scientific_name=sci,
                category=cat,
                season=season,
                water_need_mm=float(w),
                growth_days=int(d),
                description=desc,
                **{k: v for k, v in defaults.items() if k in CropCreate.model_fields},
            )
        )
    return items


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
        existing_names = set()
        if count > 0:
            existing_names = {r.name for r in (await self.repo.list(skip=0, limit=500))[0]}
        n = 0
        for item in _seed_items():
            if item.name in existing_names:
                continue
            await self.repo.create(item)
            n += 1
        return n

    @staticmethod
    def calc_irrigation(req: IrrigationCalcRequest) -> IrrigationCalcResponse:
        etc = req.et0_mm_day * req.kc
        etc_period = etc * req.days
        gross = etc_period / req.efficiency
        vol_m3 = gross * req.area_ha * 10.0  # 1 mm over 1 ha = 10 m3
        interval = max(1, int(round(25 / max(etc, 0.1))))  # rough MAD-based
        return IrrigationCalcResponse(
            etc_mm_day=round(etc, 2),
            etc_mm_period=round(etc_period, 2),
            gross_mm_period=round(gross, 2),
            volume_m3=round(vol_m3, 2),
            volume_liters=round(vol_m3 * 1000, 0),
            recommended_interval_days=interval,
        )

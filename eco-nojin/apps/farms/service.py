"""Farm business logic."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.farms.repository import FarmRepository
from apps.farms.schemas import FarmCreate, FarmResponse, FarmUpdate
from apps.shared_core.schemas.pagination import build_meta, page_to_offset


class FarmService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = FarmRepository(session)

    async def list_farms(
        self,
        *,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        owner_id: Optional[int] = None,
    ) -> tuple[list[FarmResponse], dict]:
        skip = page_to_offset(page, size)
        rows, total = await self.repo.list(skip=skip, limit=size, search=search, owner_id=owner_id)
        items = [FarmResponse.model_validate(r) for r in rows]
        meta = build_meta(total, page, size)
        return items, meta.model_dump()

    async def get_farm(self, farm_id: int) -> FarmResponse:
        farm = await self.repo.get(farm_id)
        if not farm:
            raise ValueError("FARM_NOT_FOUND")
        return FarmResponse.model_validate(farm)

    async def create_farm(self, data: FarmCreate, owner_id: Optional[int] = None) -> FarmResponse:
        farm = await self.repo.create(data, owner_id=owner_id)
        return FarmResponse.model_validate(farm)

    async def update_farm(self, farm_id: int, data: FarmUpdate) -> FarmResponse:
        farm = await self.repo.get(farm_id)
        if not farm:
            raise ValueError("FARM_NOT_FOUND")
        farm = await self.repo.update(farm, data)
        return FarmResponse.model_validate(farm)

    async def delete_farm(self, farm_id: int) -> None:
        farm = await self.repo.get(farm_id)
        if not farm:
            raise ValueError("FARM_NOT_FOUND")
        await self.repo.soft_delete(farm)

    async def geojson(self, farm_id: int) -> dict:
        farm = await self.repo.get(farm_id)
        if not farm:
            raise ValueError("FARM_NOT_FOUND")
        if farm.geojson:
            import json

            try:
                return json.loads(farm.geojson)
            except Exception:
                pass
        if farm.latitude is not None and farm.longitude is not None:
            return {
                "type": "Feature",
                "properties": {"id": farm.id, "name": farm.name},
                "geometry": {
                    "type": "Point",
                    "coordinates": [farm.longitude, farm.latitude],
                },
            }
        return {"type": "FeatureCollection", "features": []}

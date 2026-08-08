"""Farms API — /api/v1/farms."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.farms.models import Farm
from apps.farms.schemas import FarmCreate, FarmListResponse, FarmResponse, FarmUpdate
from apps.farms.service import FarmService
from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.shared_core.schemas.pagination import ListMeta

router = APIRouter(prefix="/api/v1/farms", tags=["Farms"])


@router.get("", response_model=FarmListResponse)
async def list_farms(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    session: AsyncSession = Depends(get_db_session),
):
    service = FarmService(session)
    items, meta = await service.list_farms(page=page, size=size, search=search)
    if not isinstance(meta, dict):
        meta = {"total": 0, "page": page, "size": size, "pages": 0}
    return FarmListResponse(data=items, meta=ListMeta(**meta))


@router.post("/seed-demo", status_code=status.HTTP_200_OK)
async def seed_farms(
    current_user: Farm = Depends(require_permission("farm.seed")),
    session: AsyncSession = Depends(get_db_session),
):
    """Insert demo farms (local/dev only). Uses direct COUNT — no meta tuple bugs."""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Seed disabled in production")

    total = int(
        (
            await session.execute(
                select(func.count()).select_from(Farm).where(Farm.is_deleted.is_(False))
            )
        ).scalar_one()
        or 0
    )
    if total > 0:
        return {"seeded": 0, "message": "already has farms", "total": total}

    service = FarmService(session)
    demos = [
        FarmCreate(
            name="Isfahan Demo Farm",
            description="Pilot plot near Zayandeh-Rud",
            region="Isfahan",
            area_ha=12.5,
            latitude=32.65,
            longitude=51.67,
        ),
        FarmCreate(
            name="Khuzestan Water Pilot",
            description="Irrigation efficiency demo",
            region="Khuzestan",
            area_ha=40.0,
            latitude=31.32,
            longitude=48.67,
        ),
        FarmCreate(
            name="Fars Dryland Trial",
            description="Drought-resilient cereals",
            region="Fars",
            area_ha=8.0,
            latitude=29.59,
            longitude=52.58,
        ),
    ]
    n = 0
    for d in demos:
        await service.create_farm(d)
        n += 1
    return {"seeded": n, "message": "ok"}


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(
    farm_in: FarmCreate,
    current_user: Farm = Depends(require_permission("farm.create")),
    session: AsyncSession = Depends(get_db_session),
):
    service = FarmService(session)
    return await service.create_farm(farm_in)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        return await FarmService(session).get_farm(farm_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Farm not found")


@router.patch("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_in: FarmUpdate,
    current_user: Farm = Depends(require_permission("farm.update")),
    session: AsyncSession = Depends(get_db_session),
):
    service = FarmService(session)
    farm = await service.update_farm(farm_id, farm_in)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(
    farm_id: int,
    current_user: Farm = Depends(require_permission("farm.delete")),
    session: AsyncSession = Depends(get_db_session),
):
    service = FarmService(session)
    success = await service.delete_farm(farm_id)
    if not success:
        raise HTTPException(status_code=404, detail="Farm not found")


@router.get("/{farm_id}/geojson")
async def farm_geojson(farm_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        return await FarmService(session).geojson(farm_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Farm not found")

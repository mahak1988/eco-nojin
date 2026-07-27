"""Farms API — /api/v1/farms."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.farms.schemas import FarmCreate, FarmListResponse, FarmResponse, FarmUpdate
from apps.farms.service import FarmService
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.shared_core.schemas.pagination import ListMeta

router = APIRouter(prefix="/api/v1/farms", tags=["Farms"])


@router.get("", response_model=FarmListResponse)
async def list_farms(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    service = FarmService(session)
    items, meta = await service.list_farms(page=page, size=size, search=search)
    return FarmListResponse(data=items, meta=ListMeta(**meta))


@router.post("", response_model=FarmResponse, status_code=status.HTTP_201_CREATED)
async def create_farm(
    payload: FarmCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("farms:write")),
):
    service = FarmService(session)
    return await service.create_farm(payload)


@router.get("/{farm_id}", response_model=FarmResponse)
async def get_farm(farm_id: int, session: AsyncSession = Depends(get_db_session)):
    service = FarmService(session)
    try:
        return await service.get_farm(farm_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Farm not found")


@router.patch("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    payload: FarmUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("farms:write")),
):
    service = FarmService(session)
    try:
        return await service.update_farm(farm_id, payload)
    except ValueError:
        raise HTTPException(status_code=404, detail="Farm not found")


@router.delete("/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farm(
    farm_id: int,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("farms:write")),
):
    service = FarmService(session)
    try:
        await service.delete_farm(farm_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Farm not found")


@router.get("/{farm_id}/geojson")
async def farm_geojson(farm_id: int, session: AsyncSession = Depends(get_db_session)):
    service = FarmService(session)
    try:
        return await service.geojson(farm_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Farm not found")

"""Crops API."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.crops.schemas import (
    CropListResponse,
    CropResponse,
    IrrigationCalcRequest,
    IrrigationCalcResponse,
)
from apps.crops.service import CropService
from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/crops", tags=["Crops"])


@router.get("", response_model=CropListResponse)
async def list_crops(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=200),
    search: Optional[str] = None,
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db_session),
):
    items, meta = await CropService(session).list_crops(
        page=page, size=size, search=search, category=category
    )
    return CropListResponse(data=items, meta=meta)


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(crop_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        return await CropService(session).get(crop_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Crop not found")


@router.post("/seed-demo")
async def seed_crops(
    force: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
):
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Seed disabled")
    n = await CropService(session).seed_demo(force=force)
    return {"seeded": n, "message": "ok"}


@router.post("/irrigation/calculate", response_model=IrrigationCalcResponse)
async def irrigation_calculate(body: IrrigationCalcRequest):
    """ETc = ET0 × Kc; gross = ETc / efficiency; volume = gross_mm × area_ha × 10."""
    return CropService.calc_irrigation(body)

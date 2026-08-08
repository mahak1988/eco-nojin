"""Crops API + agronomy decision helpers."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.crops.agronomy_services import disease_rules, rotation_plan, yield_prediction
from apps.crops.schemas import (
    CropListResponse,
    CropResponse,
    IrrigationCalcRequest,
    IrrigationCalcResponse,
)
from apps.crops.service import CropService
from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission

router = APIRouter(prefix="/api/v1/crops", tags=["Crops"])


class RotationIn(BaseModel):
    current_crop: str = Field(..., min_length=1)
    years: int = Field(3, ge=2, le=6)


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


@router.get("/disease-rules")
async def get_disease_rules(crop: Optional[str] = None):
    return {"data": disease_rules(crop)}


@router.get("/yield-prediction")
async def get_yield_prediction(
    crop: str = Query("wheat"),
    area_ha: float = Query(1.0, gt=0),
    water_stress: float = Query(0.2, ge=0, le=1),
    fertility: float = Query(0.8, ge=0, le=1),
):
    return yield_prediction(crop, area_ha, water_stress, fertility)


from apps.shared_core.rbac import require_permission
from apps.crops.models import Crop

@router.post("/rotation-plan")
async def post_rotation_plan(
    body: RotationIn,
    current_user: Annotated[Crop, Depends(require_permission("crop.rotation_plan"))],
):
    return rotation_plan(body.current_crop, body.years)


from apps.shared_core.rbac import require_permission
from apps.crops.models import Crop

@router.post("/seed-demo")
async def seed_crops(
    current_user: Annotated[Crop, Depends(require_permission("crop.seed"))],
    force: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
):
    """Seed crop catalog. Open in local; production requires crops:write."""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Seed disabled in production")
    n = await CropService(session).seed_demo(force=force)
    return {"seeded": n, "message": "ok"}


@router.get("/{crop_id}", response_model=CropResponse)
async def get_crop(crop_id: int, session: AsyncSession = Depends(get_db_session)):
    try:
        return await CropService(session).get(crop_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Crop not found")


from apps.shared_core.rbac import require_permission
from apps.crops.models import Crop

@router.post("/irrigation/calculate", response_model=IrrigationCalcResponse)
async def irrigation_calculate(
    body: IrrigationCalcRequest,
    current_user: Annotated[Crop, Depends(require_permission("crop.irrigation_calc"))],
):
    return CropService.calc_irrigation(body)

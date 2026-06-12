"""
Admin router for Land & Soil-Water (LDN dashboards + CRUD).
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.modules.soil_water import schemas, service
from api.services.soil_water.ldn_services import (
    analyze_ldn,
    LDNInput,
    batch_analyze_ldn,
)

router = APIRouter(
    prefix="/soil-water/admin",
    tags=["soil-water-admin"],
)


# -----------------------------
# Preview / analytical endpoints
# -----------------------------


@router.get("/ldn-preview")
async def ldn_preview(
    soil_organic_carbon: float = Query(40.0, ge=0, le=100),
    vegetation_cover: float = Query(35.0, ge=0, le=100),
    erosion_risk: float = Query(30.0, ge=0, le=100),
):
    inputs: LDNInput = {
        "soil_organic_carbon": soil_organic_carbon,
        "vegetation_cover": vegetation_cover,
        "erosion_risk": erosion_risk,
    }
    analysis = analyze_ldn(inputs)
    return analysis


@router.post("/ldn-batch")
async def ldn_batch(items: List[LDNInput]):
    return batch_analyze_ldn(items)


# -----------------------------
# CRUD endpoints for SoilWaterAnalysis
# -----------------------------


@router.post(
    "/analyses",
    response_model=schemas.SoilWaterDB,
    status_code=status.HTTP_201_CREATED,
)
async def create_soil_water_analysis(
    payload: schemas.SoilWaterCreate,
    db: Session = Depends(get_db),
):
    """
    ایجاد یک تحلیل جدید LDN و ذخیره در دیتابیس.
    فرانت: فرم ثبت تحلیل / ایجاد رکورد جدید.
    """
    obj = service.create_analysis(db, payload)
    return obj


@router.get(
    "/analyses",
    response_model=schemas.SoilWaterList,
)
async def list_soil_water_analyses(
    farmer_id: Optional[int] = Query(default=None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    لیست تحلیل‌ها برای داشبورد (با فیلتر اختیاری farmer_id).
    """
    total, items = service.list_analyses(
        db=db,
        farmer_id=farmer_id,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "items": items}


@router.get(
    "/analyses/{analysis_id}",
    response_model=schemas.SoilWaterDB,
)
async def get_soil_water_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    obj = service.get_analysis(db, analysis_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return obj


@router.patch(
    "/analyses/{analysis_id}",
    response_model=schemas.SoilWaterDB,
)
async def update_soil_water_analysis(
    analysis_id: int,
    payload: schemas.SoilWaterUpdate,
    db: Session = Depends(get_db),
):
    obj = service.update_analysis(db, analysis_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return obj


@router.delete(
    "/analyses/{analysis_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_soil_water_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    ok = service.delete_analysis(db, analysis_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return None
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.core.dependencies import get_db
from api.modules.soil_water import erosion_schemas, erosion_service

admin_erosion_router = APIRouter(prefix="/soil-water/admin/erosion", tags=["Soil Erosion (Admin)"])


@admin_erosion_router.post("/analyses", response_model=erosion_schemas.SoilErosionDB)
def create_erosion(
    payload: erosion_schemas.SoilErosionCreate,
    db: Session = Depends(get_db),
):
    return erosion_service.create_erosion_analysis(db, payload)


@admin_erosion_router.get("/analyses/{analysis_id}", response_model=erosion_schemas.SoilErosionDB)
def get_erosion(
    analysis_id: int,
    db: Session = Depends(get_db),
):
    obj = erosion_service.get_erosion_analysis(db, analysis_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Erosion analysis not found")
    return obj


@admin_erosion_router.get("/analyses", response_model=erosion_schemas.SoilErosionList)
def list_erosion(
    farmer_id: int | None = Query(default=None),
    location_id: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    total, items = erosion_service.list_erosion_analyses(
        db=db,
        farmer_id=farmer_id,
        location_id=location_id,
        skip=skip,
        limit=limit,
    )
    return {"total": total, "items": items}
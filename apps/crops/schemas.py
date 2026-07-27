"""Crop schemas with agronomy."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class CropCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    name_fa: Optional[str] = None
    scientific_name: Optional[str] = None
    category: str = "cereal"
    season: Optional[str] = None
    water_need_mm: Optional[float] = Field(None, ge=0)
    growth_days: Optional[int] = Field(None, ge=1)
    description: Optional[str] = None
    planting_method: Optional[str] = None
    row_spacing_cm: Optional[float] = None
    plant_spacing_cm: Optional[float] = None
    sowing_depth_cm: Optional[float] = None
    seed_rate_kg_ha: Optional[float] = None
    irrigation_method: Optional[str] = None
    irrigation_interval_days: Optional[int] = None
    kc_mid: Optional[float] = None
    fertilizer_n_kg_ha: Optional[float] = None
    fertilizer_p_kg_ha: Optional[float] = None
    fertilizer_k_kg_ha: Optional[float] = None
    soil_ph_min: Optional[float] = None
    soil_ph_max: Optional[float] = None
    harvest_method: Optional[str] = None
    harvest_moisture_pct: Optional[float] = None
    common_pests: Optional[str] = None
    common_diseases: Optional[str] = None
    care_notes: Optional[str] = None


class CropResponse(CropCreate):
    id: int
    is_active: bool = True
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class CropListResponse(BaseModel):
    data: list[CropResponse]
    meta: ListMeta


class IrrigationCalcRequest(BaseModel):
    area_ha: float = Field(..., gt=0)
    et0_mm_day: float = Field(..., gt=0, description="Reference ET0 mm/day")
    kc: float = Field(1.0, gt=0, description="Crop coefficient")
    efficiency: float = Field(0.85, gt=0, le=1, description="Irrigation system efficiency")
    days: int = Field(7, ge=1, le=90)


class IrrigationCalcResponse(BaseModel):
    etc_mm_day: float
    etc_mm_period: float
    gross_mm_period: float
    volume_m3: float
    volume_liters: float
    recommended_interval_days: Optional[int] = None

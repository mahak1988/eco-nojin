"""Crop schemas with agronomy."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from apps.shared_core.schemas.pagination import ListMeta


class CropCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    name_fa: str | None = None
    scientific_name: str | None = None
    category: str = "cereal"
    season: str | None = None
    water_need_mm: float | None = Field(None, ge=0)
    growth_days: int | None = Field(None, ge=1)
    description: str | None = None
    planting_method: str | None = None
    row_spacing_cm: float | None = None
    plant_spacing_cm: float | None = None
    sowing_depth_cm: float | None = None
    seed_rate_kg_ha: float | None = None
    irrigation_method: str | None = None
    irrigation_interval_days: int | None = None
    kc_mid: float | None = None
    fertilizer_n_kg_ha: float | None = None
    fertilizer_p_kg_ha: float | None = None
    fertilizer_k_kg_ha: float | None = None
    soil_ph_min: float | None = None
    soil_ph_max: float | None = None
    harvest_method: str | None = None
    harvest_moisture_pct: float | None = None
    common_pests: str | None = None
    common_diseases: str | None = None
    care_notes: str | None = None


class CropResponse(CropCreate):
    id: int
    is_active: bool = True
    created_at: datetime | None = None

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
    recommended_interval_days: int | None = None

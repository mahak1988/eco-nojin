"""Phosphorus cycle, deep KGE, soil type amendments API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.simulation.kge_deep import kge_components
from apps.simulation.phosphorus_cycle import run_phosphorus_cycle
from apps.simulation.soil_amendment_types import (
    classify_soil,
    list_soil_types,
    recommend_amendments,
)

router = APIRouter(prefix="/api/v1/science", tags=["Phosphorus & Soil Types"])


class PBody(BaseModel):
    years: int = Field(10, ge=1, le=50)
    p_labile_kg_ha: float = Field(25, ge=0, le=200)
    p_active_kg_ha: float = Field(80, ge=0, le=500)
    p_stable_kg_ha: float = Field(200, ge=0, le=2000)
    p_organic_kg_ha: float = Field(60, ge=0, le=500)
    fertilizer_p_kg_ha_y: float = Field(40, ge=0, le=150)
    residue_p_kg_ha_y: float = Field(5, ge=0, le=50)
    max_uptake_kg_ha_y: float = Field(25, ge=0, le=80)
    ph: float = Field(7.0, ge=4, le=9.5)
    clay_pct: float = Field(25, ge=0, le=80)
    temp_c: float = Field(15, ge=-5, le=40)
    moisture_frac: float = Field(0.55, ge=0.1, le=1.0)
    erosion_loss_frac_y: float = Field(0.01, ge=0, le=0.2)


class KgeBody(BaseModel):
    observed: list[float] = Field(..., min_length=2)
    simulated: list[float] = Field(..., min_length=2)


class SoilTypeBody(BaseModel):
    ph: float = Field(7.0, ge=3.5, le=10)
    ec_ds_m: float = Field(1.0, ge=0, le=40)
    esp_pct: float = Field(5.0, ge=0, le=80)
    sand_pct: float = Field(40, ge=0, le=100)
    clay_pct: float = Field(25, ge=0, le=100)
    om_pct: float = Field(1.5, ge=0, le=30)
    bulk_density_mg_m3: float = Field(1.4, ge=0.8, le=2.0)
    cec_cmol_kg: float = Field(15, ge=1, le=80)
    depth_cm: float = Field(30, ge=10, le=60)
    ec_water_ds_m: float = Field(1.0, ge=0.1, le=10)
    gypsum_pct: float = Field(0.0, ge=0, le=40)


@router.post("/phosphorus/run")
async def p_run(body: PBody) -> dict[str, Any]:
    return run_phosphorus_cycle(body.model_dump())


@router.post("/metrics/kge-deep")
async def kge_deep(body: KgeBody) -> dict[str, Any]:
    return kge_components(body.observed, body.simulated)


@router.get("/soil/types")
async def soil_types() -> dict[str, Any]:
    return list_soil_types()


@router.post("/soil/classify")
async def soil_class(body: SoilTypeBody) -> dict[str, Any]:
    return classify_soil(body.model_dump())


@router.post("/soil/amendment-plan")
async def amendment_plan(body: SoilTypeBody) -> dict[str, Any]:
    return recommend_amendments(body.model_dump())

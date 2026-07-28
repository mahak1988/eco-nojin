"""Organic matter dynamics + soil carbon calibration API."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apps.simulation.organic_matter import (
    om_catalog,
    run_litter_cascade,
    run_om_cn_coupled,
    run_om_two_pool,
)
from apps.simulation.soil_carbon_calibration import calibrate_soil_carbon

router = APIRouter(prefix="/api/v1/science", tags=["Organic Matter & Calibration"])


class CalibrateBody(BaseModel):
    model: str = Field("rothc", description="rothc | icbm | century3 | yasso07_lite")
    observed_soc: list[float] = Field(
        ...,
        min_length=2,
        description="Annual SOC t C/ha starting at year 0",
    )
    base_params: Optional[dict[str, Any]] = None
    free_params: Optional[list[str]] = None
    n_samples: int = Field(80, ge=20, le=400)
    metric: str = Field("rmse", pattern="^(rmse|nse)$")
    seed: int = 42


class OmTwoBody(BaseModel):
    years: int = Field(20, ge=1, le=100)
    om_t_ha: float = Field(80.0, ge=1, le=400)
    om_input_t_ha_y: float = Field(3.0, ge=0, le=30)
    labile_frac: float = Field(0.2, ge=0.05, le=0.6)
    k_labile: float = Field(1.2, ge=0.1, le=5)
    k_stable: float = Field(0.05, ge=0.005, le=0.5)
    stabilization_frac: float = Field(0.25, ge=0, le=0.8)
    temp_c: float = Field(15.0, ge=-5, le=40)
    moisture_frac: float = Field(0.55, ge=0.05, le=1.0)
    carbon_fraction: float = Field(0.58, ge=0.4, le=0.6)


class OmCnBody(BaseModel):
    years: int = Field(15, ge=1, le=80)
    soc_t_ha: float = Field(40.0, ge=5, le=200)
    cn_ratio: float = Field(12.0, ge=5, le=40)
    n_mineral_t_ha: float = Field(0.08, ge=0, le=2)
    c_input_t_ha_y: float = Field(1.5, ge=0, le=15)
    cn_input: float = Field(25.0, ge=8, le=80)
    k_decomp: float = Field(0.15, ge=0.02, le=1.0)
    temp_c: float = Field(15.0, ge=-5, le=40)
    moisture_frac: float = Field(0.55, ge=0.05, le=1.0)


class LitterBody(BaseModel):
    years: int = Field(15, ge=1, le=80)
    litter_t_ha: float = Field(2.0, ge=0, le=50)
    om_t_ha: float = Field(70.0, ge=1, le=300)
    passive_t_ha: float = Field(30.0, ge=0, le=200)
    litter_input_t_ha_y: float = Field(2.5, ge=0, le=20)
    k_litter: float = Field(1.5, ge=0.2, le=5)
    k_om: float = Field(0.08, ge=0.01, le=0.5)
    temp_c: float = Field(15.0, ge=-5, le=40)
    moisture_frac: float = Field(0.55, ge=0.05, le=1.0)


@router.get("/organic-matter/catalog")
async def organic_matter_catalog() -> dict[str, Any]:
    return om_catalog()


@router.post("/soil-carbon/calibrate")
async def calibrate(body: CalibrateBody) -> dict[str, Any]:
    try:
        return calibrate_soil_carbon(
            model=body.model,
            observed_soc=body.observed_soc,
            base_params=body.base_params,
            free_params=body.free_params,
            n_samples=body.n_samples,
            metric=body.metric,
            seed=body.seed,
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/organic-matter/two-pool")
async def om_two(body: OmTwoBody) -> dict[str, Any]:
    return run_om_two_pool(body.model_dump())


@router.post("/organic-matter/cn")
async def om_cn(body: OmCnBody) -> dict[str, Any]:
    return run_om_cn_coupled(body.model_dump())


@router.post("/organic-matter/litter")
async def om_litter(body: LitterBody) -> dict[str, Any]:
    return run_litter_cascade(body.model_dump())

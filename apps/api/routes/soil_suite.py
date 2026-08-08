"""Soil profile, nitrate leaching, amendments, KGE/PBIAS API."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from apps.simulation.soil_suite import (
    amendment_carbon,
    cec_estimate,
    compaction_index,
    evaluate_soil_series,
    infiltration_green_ampt,
    liming_requirement,
    n_leaching_index,
    profile_available_n,
    run_nitrate_leaching,
    rusle_lite,
    salinity_leaching,
    soc_stock,
    sodicity_gypsum,
    soil_catalog,
    soil_health_score,
    soil_temperature_profile,
    texture_hydrology,
)

router = APIRouter(prefix="/api/v1/science/soil", tags=["Soil Suite"])


class LeachBody(BaseModel):
    days: int = Field(120, ge=7, le=366)
    n_layers: int = Field(3, ge=1, le=6)
    layer_thickness_mm: float = Field(300, ge=50, le=600)
    theta_fc: float = Field(0.32, ge=0.1, le=0.55)
    theta_wp: float = Field(0.14, ge=0.05, le=0.4)
    rain_mm_day: float = Field(1.5, ge=0, le=50)
    et_mm_day: float = Field(2.0, ge=0, le=15)
    irrigation_mm_day: float = Field(0.5, ge=0, le=30)
    no3_kg_ha_layer: float = Field(25.0, ge=0, le=200)
    no3_profile: list[float] | None = None
    fertilizer_events: list[dict[str, Any]] | None = None


class TextureBody(BaseModel):
    sand_pct: float = Field(40, ge=0, le=100)
    clay_pct: float = Field(25, ge=0, le=100)
    depth_cm: float = Field(30, ge=5, le=200)


class SocBody(BaseModel):
    soc_pct: float = Field(1.2, ge=0.05, le=15)
    bulk_density_mg_m3: float = Field(1.35, ge=0.8, le=1.9)
    depth_cm: float = Field(30, ge=5, le=100)
    stone_frac: float = Field(0.0, ge=0, le=0.5)


class LimeBody(BaseModel):
    ph: float = Field(5.5, ge=3.5, le=9)
    target_ph: float = Field(6.5, ge=5, le=8)
    cec_cmol_kg: float = Field(15, ge=1, le=80)
    depth_cm: float = Field(20, ge=5, le=40)


class CecBody(BaseModel):
    clay_pct: float = Field(25, ge=0, le=100)
    om_pct: float = Field(2.0, ge=0, le=20)


class SalBody(BaseModel):
    ec_extract_ds_m: float = Field(4.0, ge=0.2, le=30)
    ec_water_ds_m: float = Field(1.0, ge=0.1, le=10)
    et_mm_season: float = Field(600, ge=50, le=2000)


class GypBody(BaseModel):
    esp_pct: float = Field(18, ge=0, le=60)
    target_esp_pct: float = Field(10, ge=0, le=30)
    cec_cmol_kg: float = Field(20, ge=1, le=80)
    depth_cm: float = Field(30, ge=10, le=60)
    bulk_density_mg_m3: float = Field(1.4, ge=1.0, le=1.8)


class CompBody(BaseModel):
    bulk_density_mg_m3: float = Field(1.55, ge=1.0, le=2.0)
    clay_pct: float = Field(25, ge=0, le=100)


class RusleBody(BaseModel):
    R: float = 100
    K: float = 0.3
    LS: float = 1.0
    C: float = 0.2
    P: float = 1.0


class AmendBody(BaseModel):
    rate_t_ha: float = Field(10, ge=0, le=100)
    kind: str = Field("compost")


class NLIBody(BaseModel):
    precip_mm_y: float = Field(400, ge=50, le=3000)
    et_mm_y: float = Field(1200, ge=100, le=3000)
    n_fert_kg_ha: float = Field(120, ge=0, le=400)


class ProfileNBody(BaseModel):
    layers: list[dict[str, Any]] | None = None


class InfilBody(BaseModel):
    ks_mm_h: float = Field(10, ge=0.1, le=200)
    suction_mm: float = Field(100, ge=10, le=500)
    delta_theta: float = Field(0.2, ge=0.05, le=0.4)
    hours: float = Field(2, ge=0.2, le=24)


class TempBody(BaseModel):
    t_air_c: float = 25
    t_annual_mean_c: float = 15
    depths_cm: list[float] | None = None


class HealthBody(BaseModel):
    soc_pct: float = 1.2
    ph: float = 7.0
    bulk_density_mg_m3: float = 1.35
    ec_ds_m: float = 1.0


class EvalBody(BaseModel):
    observed: list[float] = Field(..., min_length=2)
    simulated: list[float] = Field(..., min_length=2)
    variable: str = "soil"


@router.get("/catalog")
async def catalog() -> dict[str, Any]:
    return soil_catalog()


@router.post("/nitrate-leaching")
async def nitrate_leaching(body: LeachBody) -> dict[str, Any]:
    return run_nitrate_leaching(body.model_dump(exclude_none=True))


@router.post("/texture-hydrology")
async def texture(body: TextureBody) -> dict[str, Any]:
    return texture_hydrology(body.model_dump())


@router.post("/soc-stock")
async def soc(body: SocBody) -> dict[str, Any]:
    return soc_stock(body.model_dump())


@router.post("/liming")
async def liming(body: LimeBody) -> dict[str, Any]:
    return liming_requirement(body.model_dump())


@router.post("/cec")
async def cec(body: CecBody) -> dict[str, Any]:
    return cec_estimate(body.model_dump())


@router.post("/salinity-leaching")
async def salinity(body: SalBody) -> dict[str, Any]:
    return salinity_leaching(body.model_dump())


@router.post("/gypsum")
async def gypsum(body: GypBody) -> dict[str, Any]:
    return sodicity_gypsum(body.model_dump())


@router.post("/compaction")
async def compaction(body: CompBody) -> dict[str, Any]:
    return compaction_index(body.model_dump())


@router.post("/rusle")
async def rusle(body: RusleBody) -> dict[str, Any]:
    return rusle_lite(body.model_dump())


@router.post("/amendment-carbon")
async def amend(body: AmendBody) -> dict[str, Any]:
    return amendment_carbon(body.model_dump())


@router.post("/n-leaching-index")
async def nli(body: NLIBody) -> dict[str, Any]:
    return n_leaching_index(body.model_dump())


@router.post("/profile-n")
async def profile_n(body: ProfileNBody) -> dict[str, Any]:
    return profile_available_n(body.model_dump(exclude_none=True))


@router.post("/infiltration")
async def infil(body: InfilBody) -> dict[str, Any]:
    return infiltration_green_ampt(body.model_dump())


@router.post("/temperature")
async def temp(body: TempBody) -> dict[str, Any]:
    return soil_temperature_profile(body.model_dump(exclude_none=True))


@router.post("/health-score")
async def health(body: HealthBody) -> dict[str, Any]:
    return soil_health_score(body.model_dump())


@router.post("/evaluate")
async def evaluate(body: EvalBody) -> dict[str, Any]:
    return evaluate_soil_series(body.observed, body.simulated, body.variable)

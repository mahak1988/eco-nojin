"""Phase 3 scientific APIs — SWAT+, advanced AquaCrop, climate ETL, scenarios."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from apps.shared_core.rbac import require_permission
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.climate_etl import fetch_climate_series
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.scenario_engine import run_scenarios

router = APIRouter(prefix="/api/v1/science", tags=["Phase3 Science"])


class SwatBody(BaseModel):
    area_km2: float = 25.0
    days: int = Field(365, ge=30, le=3660)
    precip_mm_year: float = 320.0
    et0_mm_year: float = 1400.0
    curve_number: float = Field(75.0, ge=30, le=98)
    soil_awc_mm: float = 120.0
    slope_pct: float = 3.0
    land_cover: str = "cropland"


class AquaAdvBody(BaseModel):
    area_ha: float = 1.0
    days: int = Field(90, ge=7, le=365)
    et0_mm_day: float = 4.5
    kc: float = 1.1
    rain_mm_day: float = 0.5
    taw_mm: float = 100.0
    ky: float = 1.15
    y_potential_t_ha: float = 6.0
    irrig_threshold_frac: float = 0.6
    canopy_cover: Optional[list[float]] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    use_live_climate: bool = False


class ScenarioBody(BaseModel):
    scenarios: Optional[list[dict[str, Any]]] = None


@router.get("/status")
async def science_status() -> dict[str, Any]:
    gee_ok = False
    gee_detail = "not_configured"
    try:
        from apps.satellite.providers.gee_provider import GEEProvider

        p = GEEProvider()
        gee_ok = p.is_available
        gee_detail = "initialized" if gee_ok else "credentials_or_ee_missing"
    except Exception as e:
        gee_detail = str(e)[:100]

    db_kind = "unknown"
    try:
        from apps.shared_core.database.session import DATABASE_URL

        if "postgres" in DATABASE_URL:
            db_kind = "postgres"
        elif "sqlite" in DATABASE_URL:
            db_kind = "sqlite"
    except Exception:
        pass

    return {
        "phase": 3,
        "database": db_kind,
        "gee": {"available": gee_ok, "detail": gee_detail},
        "models": ["aquacrop_advanced", "rothc_stub", "swat_plus_proxy", "coupling", "scenario"],
        "note": "SWAT+ is process proxy until official binary is installed",
    }


@router.post("/swat")
async def swat_run(
    body: SwatBody,
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    return run_swat_plus(body.model_dump())


@router.post("/aquacrop-advanced")
async def aquacrop_adv(
    body: AquaAdvBody,
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    params = body.model_dump()
    if body.use_live_climate and body.lat is not None and body.lon is not None:
        clim = fetch_climate_series(body.lat, body.lon, days=min(body.days, 90))
        drivers = clim.get("drivers") or {}
        params["et0_mm_day"] = drivers.get("et0_mm_day", body.et0_mm_day)
        params["rain_mm_day"] = drivers.get("rain_mm_day", body.rain_mm_day)
        params["climate_source"] = clim.get("source")
    # strip non-model keys
    for k in ("lat", "lon", "use_live_climate", "climate_source"):
        params.pop(k, None)
    result = run_aquacrop_advanced(params)
    if body.use_live_climate:
        result["climate_attached"] = True
    return result


@router.get("/climate-drivers")
async def climate_drivers(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=366),
) -> dict[str, Any]:
    return fetch_climate_series(lat, lon, days)


@router.post("/scenarios")
async def scenarios(
    body: ScenarioBody | None = None,
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    return run_scenarios(body.scenarios if body else None)


@router.post("/pipeline/farm-run")
async def farm_pipeline(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    area_ha: float = Query(2.0),
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    """End-to-end: climate → AquaCrop advanced → SWAT proxy → ranking context."""
    clim = fetch_climate_series(lat, lon, days=60)
    d = clim.get("drivers") or {}
    aq = run_aquacrop_advanced(
        {
            "area_ha": area_ha,
            "days": 60,
            "et0_mm_day": d.get("et0_mm_day", 4.5),
            "rain_mm_day": d.get("rain_mm_day", 0.5),
        }
    )
    sw = run_swat_plus(
        {
            "area_km2": max(area_ha / 100.0, 0.01),
            "precip_mm_year": d.get("precip_mm_year_proxy", 300),
            "et0_mm_year": d.get("et0_mm_year_proxy", 1400),
        }
    )
    return {
        "pipeline": "farm-run-v1",
        "climate": {"source": clim.get("source"), "drivers": d},
        "aquacrop": aq,
        "swat": sw,
    }

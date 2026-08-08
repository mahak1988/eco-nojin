"""Phase 3 scientific APIs — no Celery import at module load.

AquaCrop advanced lives in apps.api.routes.science (loose schema, public).
This router keeps SWAT / scenarios / pipeline / climate helpers.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.climate_etl import fetch_climate_series
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async
from apps.simulation.run_store import get_run, list_runs, run_to_dict, save_run_async
from apps.simulation.runners import run_swat_local
from apps.simulation.scenario_engine import run_scenarios

router = APIRouter(prefix="/api/v1/science", tags=["Phase3 Science"])


class SwatBody(BaseModel):
    model_config = ConfigDict(extra="ignore")
    area_km2: float = 25.0
    days: int = Field(365, ge=30, le=3660)
    precip_mm_year: float = 320.0
    et0_mm_year: float = 1400.0
    curve_number: float = Field(75.0, ge=30, le=98)
    soil_awc_mm: float = 120.0
    slope_pct: float = 3.0
    land_cover: str = "cropland"
    farm_id: int | None = None
    async_mode: bool = False
    persist: bool = True


class ScenarioBody(BaseModel):
    scenarios: list[dict[str, Any]] | None = None


@router.get("/status", operation_id="phase3_science_status")
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
        "wave": 2,
        "database": db_kind,
        "gee": {"available": gee_ok, "detail": gee_detail},
        "models": ["aquacrop_advanced", "rothc", "swat_plus_proxy", "coupling", "scenario"],
        "auth": "aquacrop-advanced is public (see apps.api.routes.science)",
        "crop_library": "/api/v1/science/crop-library",
        "note": "SWAT+ is process proxy until official binary is installed",
    }


@router.post("/swat", operation_id="phase3_swat_run")
async def swat_run(
    body: SwatBody,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    params = body.model_dump()
    async_mode = params.pop("async_mode", False)
    persist = params.pop("persist", True)
    farm_id = params.pop("farm_id", None)
    if async_mode:
        try:
            from apps.simulation.tasks_phase3 import task_swat

            task = task_swat.delay({**params, "farm_id": farm_id})
            return {"status": "queued", "task_id": task.id, "model": "swat_plus_proxy"}
        except Exception as e:
            result = run_swat_local(params, farm_id=farm_id, persist=persist)
            result["celery_error"] = str(e)[:120]
            return result
    result = run_swat_local(params, farm_id=farm_id, persist=False)
    if persist:
        try:
            row = await save_run_async(session, "swat_plus_proxy", params, result, farm_id=farm_id)
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:120]
    return result


@router.get("/ndvi-canopy", operation_id="phase3_ndvi_canopy")
async def ndvi_canopy(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=7, le=365),
) -> dict[str, Any]:
    return await fetch_ndvi_canopy_async(lat, lon, days)


@router.get("/runs", operation_id="phase3_runs_list")
async def runs_list(
    model: str | None = None,
    farm_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    rows = await list_runs(session, model=model, farm_id=farm_id, limit=limit)
    return {"data": [run_to_dict(r) for r in rows], "count": len(rows)}


@router.get("/runs/{run_id}", operation_id="phase3_runs_get")
async def runs_get(
    run_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    row = await get_run(session, run_id)
    if not row:
        raise HTTPException(404, "Run not found")
    return run_to_dict(row)


@router.get("/climate-drivers", operation_id="phase3_climate_drivers")
async def climate_drivers(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=366),
) -> dict[str, Any]:
    return fetch_climate_series(lat, lon, days)


@router.post("/scenarios", operation_id="phase3_scenarios")
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
    use_ndvi: bool = Query(True),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    clim = fetch_climate_series(lat, lon, days=60)
    d = clim.get("drivers") or {}
    canopy = None
    ndvi_meta = None
    if use_ndvi:
        bridge = await fetch_ndvi_canopy_async(lat, lon, days=60)
        canopy = bridge["canopy_cover"]
        ndvi_meta = {"provider": bridge["provider"], "count": bridge["count"]}
    aq_params: dict[str, Any] = {
        "area_ha": area_ha,
        "days": 60,
        "et0_mm_day": d.get("et0_mm_day", 4.5),
        "rain_mm_day": d.get("rain_mm_day", 0.5),
    }
    if canopy:
        aq_params["canopy_cover"] = canopy
    aq = run_aquacrop_advanced(aq_params)
    if ndvi_meta:
        aq["ndvi_meta"] = ndvi_meta
    sw = run_swat_plus(
        {
            "area_km2": max(area_ha / 100.0, 0.01),
            "precip_mm_year": d.get("precip_mm_year_proxy", 300),
            "et0_mm_year": d.get("et0_mm_year_proxy", 1400),
        }
    )
    out: dict[str, Any] = {
        "pipeline": "farm-run-v2",
        "climate": {"source": clim.get("source"), "drivers": d},
        "aquacrop": aq,
        "swat": sw,
        "ndvi_meta": ndvi_meta,
    }
    try:
        row = await save_run_async(
            session, "farm_pipeline", {"lat": lat, "lon": lon, "area_ha": area_ha}, out
        )
        out["run_id"] = row.id
    except Exception as e:
        out["persist_error"] = str(e)[:120]
    return out

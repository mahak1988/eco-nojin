"""Phase 3 scientific APIs — no Celery import at module load."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.climate_etl import fetch_climate_series
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async
from apps.simulation.run_store import get_run, list_runs, run_to_dict, save_run_async
from apps.simulation.runners import run_aquacrop_advanced_local, run_swat_local
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
    farm_id: Optional[int] = None
    async_mode: bool = False
    persist: bool = True


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
    use_ndvi_canopy: bool = False
    farm_id: Optional[int] = None
    async_mode: bool = False
    persist: bool = True


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
        "wave": 2,
        "database": db_kind,
        "gee": {"available": gee_ok, "detail": gee_detail},
        "models": [
            "aquacrop_advanced",
            "rothc_stub",
            "swat_plus_proxy",
            "coupling",
            "scenario",
        ],
        "features": {
            "simulation_runs_persist": True,
            "celery_aquacrop_swat": True,
            "ndvi_canopy_bridge": True,
            "postgis_farm_index": True,
        },
        "note": "SWAT+ is process proxy until official binary is installed",
    }


@router.post("/swat")
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


@router.post("/aquacrop-advanced")
async def aquacrop_adv(
    body: AquaAdvBody,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("simulation:write")),
) -> dict[str, Any]:
    params = body.model_dump()
    async_mode = params.pop("async_mode", False)
    persist = params.pop("persist", True)
    farm_id = params.pop("farm_id", None)
    use_live = params.pop("use_live_climate", False)
    use_ndvi = params.pop("use_ndvi_canopy", False)
    lat, lon = params.get("lat"), params.get("lon")

    if use_live and lat is not None and lon is not None:
        clim = fetch_climate_series(float(lat), float(lon), days=min(int(params.get("days", 90)), 90))
        drivers = clim.get("drivers") or {}
        params["et0_mm_day"] = drivers.get("et0_mm_day", params["et0_mm_day"])
        params["rain_mm_day"] = drivers.get("rain_mm_day", params["rain_mm_day"])

    ndvi_meta = None
    if use_ndvi and lat is not None and lon is not None and not params.get("canopy_cover"):
        bridge = await fetch_ndvi_canopy_async(
            float(lat), float(lon), days=int(params.get("days", 90))
        )
        params["canopy_cover"] = bridge["canopy_cover"]
        ndvi_meta = {"provider": bridge["provider"], "count": bridge["count"]}

    if async_mode:
        try:
            from apps.simulation.tasks_phase3 import task_aquacrop_advanced

            celery_params = dict(params)
            celery_params["farm_id"] = farm_id
            celery_params["use_ndvi_canopy"] = False  # already resolved above
            task = task_aquacrop_advanced.delay(celery_params)
            return {"status": "queued", "task_id": task.id, "model": "aquacrop_advanced"}
        except Exception as e:
            result = run_aquacrop_advanced_local(
                {**params, "use_ndvi_canopy": False},
                farm_id=farm_id,
                persist=persist,
            )
            result["celery_error"] = str(e)[:120]
            if ndvi_meta:
                result["ndvi_meta"] = ndvi_meta
            return result

    model_params = {
        k: v
        for k, v in params.items()
        if k
        not in (
            "lat",
            "lon",
            "use_live_climate",
            "use_ndvi_canopy",
            "async_mode",
            "persist",
            "farm_id",
        )
    }
    result = run_aquacrop_advanced(model_params)
    result["mode"] = "sync_local"
    if ndvi_meta:
        result["ndvi_meta"] = ndvi_meta
        result["ndvi_calibrated"] = True
    if use_live:
        result["climate_attached"] = True
    if persist:
        try:
            row = await save_run_async(
                session, "aquacrop_advanced", model_params, result, farm_id=farm_id
            )
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:120]
    return result


@router.get("/ndvi-canopy")
async def ndvi_canopy(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=7, le=365),
) -> dict[str, Any]:
    return await fetch_ndvi_canopy_async(lat, lon, days)


@router.get("/runs")
async def runs_list(
    model: Optional[str] = None,
    farm_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    rows = await list_runs(session, model=model, farm_id=farm_id, limit=limit)
    return {"data": [run_to_dict(r) for r in rows], "count": len(rows)}


@router.get("/runs/{run_id}")
async def runs_get(
    run_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    row = await get_run(session, run_id)
    if not row:
        raise HTTPException(404, "Run not found")
    return run_to_dict(row)


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

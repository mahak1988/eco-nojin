"""Science API — registered like education so it always loads with api.routes."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/science", tags=["Phase3 Science"])


def _perm(code: str):
    try:
        from apps.shared_core.rbac import require_permission

        return require_permission(code)
    except Exception:

        async def _noop() -> None:
            return None

        return _noop


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
    persist: bool = True


class AquaBody(BaseModel):
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
    use_ndvi_canopy: bool = False
    farm_id: Optional[int] = None
    persist: bool = True


@router.get("/status")
async def science_status() -> dict[str, Any]:
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
        "router": "apps.api.routes.science",
        "database": db_kind,
        "models": ["aquacrop_advanced", "swat_plus_proxy", "scenario"],
        "ok": True,
    }


@router.post("/swat")
async def swat_run(
    body: SwatBody,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.models_swat import run_swat_plus

    params = body.model_dump()
    persist = params.pop("persist", True)
    farm_id = params.pop("farm_id", None)
    result = run_swat_plus(params)
    result["mode"] = "sync"
    if persist:
        try:
            from apps.simulation.run_store import save_run_async

            row = await save_run_async(session, "swat_plus_proxy", params, result, farm_id=farm_id)
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:120]
    return result


@router.post("/aquacrop-advanced")
async def aquacrop_run(
    body: AquaBody,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.aquacrop_advanced import run_aquacrop_advanced

    params = body.model_dump()
    persist = params.pop("persist", True)
    farm_id = params.pop("farm_id", None)
    use_ndvi = params.pop("use_ndvi_canopy", False)
    lat, lon = params.pop("lat", None), params.pop("lon", None)
    ndvi_meta = None
    if use_ndvi and lat is not None and lon is not None and not params.get("canopy_cover"):
        try:
            from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

            bridge = await fetch_ndvi_canopy_async(float(lat), float(lon), days=int(params.get("days", 90)))
            params["canopy_cover"] = bridge["canopy_cover"]
            ndvi_meta = {"provider": bridge["provider"], "count": bridge["count"]}
        except Exception as e:
            ndvi_meta = {"error": str(e)[:120]}
    result = run_aquacrop_advanced(params)
    result["mode"] = "sync"
    if ndvi_meta:
        result["ndvi_meta"] = ndvi_meta
    if persist:
        try:
            from apps.simulation.run_store import save_run_async

            row = await save_run_async(session, "aquacrop_advanced", params, result, farm_id=farm_id)
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
    from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

    return await fetch_ndvi_canopy_async(lat, lon, days)


@router.get("/runs")
async def runs_list(
    model: Optional[str] = None,
    farm_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    from apps.simulation.run_store import list_runs, run_to_dict

    rows = await list_runs(session, model=model, farm_id=farm_id, limit=limit)
    return {"data": [run_to_dict(r) for r in rows], "count": len(rows)}


@router.get("/runs/{run_id}")
async def runs_get(run_id: int, session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    from apps.simulation.run_store import get_run, run_to_dict

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
    from apps.simulation.climate_etl import fetch_climate_series

    return fetch_climate_series(lat, lon, days)


@router.post("/scenarios")
async def scenarios(
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.scenario_engine import run_scenarios

    return run_scenarios()


@router.post("/pipeline/farm-run")
async def farm_pipeline(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    area_ha: float = Query(2.0),
    use_ndvi: bool = Query(True),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
    from apps.simulation.climate_etl import fetch_climate_series
    from apps.simulation.models_swat import run_swat_plus

    clim = fetch_climate_series(lat, lon, days=60)
    d = clim.get("drivers") or {}
    aq_params: dict[str, Any] = {
        "area_ha": area_ha,
        "days": 60,
        "et0_mm_day": d.get("et0_mm_day", 4.5),
        "rain_mm_day": d.get("rain_mm_day", 0.5),
    }
    ndvi_meta = None
    if use_ndvi:
        try:
            from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

            bridge = await fetch_ndvi_canopy_async(lat, lon, days=60)
            aq_params["canopy_cover"] = bridge["canopy_cover"]
            ndvi_meta = {"provider": bridge["provider"], "count": bridge["count"]}
        except Exception as e:
            ndvi_meta = {"error": str(e)[:120]}
    aq = run_aquacrop_advanced(aq_params)
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
        from apps.simulation.run_store import save_run_async

        row = await save_run_async(session, "farm_pipeline", {"lat": lat, "lon": lon}, out)
        out["run_id"] = row.id
    except Exception as e:
        out["persist_error"] = str(e)[:120]
    return out

"""Science API — process models + user-facing analysis."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.simulation.science_analysis import attach_analysis

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
    crop: str = "wheat"


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
        "models": ["aquacrop_advanced", "swat_plus_proxy", "rothc", "ndvi_canopy"],
        "ok": True,
        "notes_fa": "خروجی هر مدل شامل analysis (خلاصه فارسی/انگلیسی + فرمول + توصیه) است.",
        "notes_en": "Each model response includes analysis (fa/en summary, formulas, advice).",
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
    result = attach_analysis("scs", run_swat_plus(params))
    result["mode"] = "sync"
    if persist:
        try:
            from apps.simulation.run_store import save_run_async

            row = await save_run_async(session, "scs_cn_basin_balance", params, result, farm_id=farm_id)
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:200]
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
            ndvi_meta = {
                "provider": bridge["provider"],
                "count": bridge["count"],
                "analysis": bridge.get("analysis"),
            }
        except Exception as e:
            ndvi_meta = {"error": str(e)[:120], "provider": "none"}
    try:
        raw = run_aquacrop_advanced(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"aquacrop failed: {e}") from e
    result = attach_analysis("aquacrop", raw)
    result["mode"] = "sync"
    if ndvi_meta:
        result["ndvi_meta"] = ndvi_meta
    if persist:
        try:
            from apps.simulation.run_store import save_run_async

            row = await save_run_async(session, "aquacrop_advanced", params, result, farm_id=farm_id)
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:200]
    return result


@router.get("/ndvi-canopy")
async def ndvi_canopy(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=7, le=365),
) -> dict[str, Any]:
    try:
        from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

        raw = await fetch_ndvi_canopy_async(lat, lon, days)
    except Exception as e:
        from apps.simulation.ndvi_canopy import _synthetic_ndvi, ndvi_to_canopy

        ndvi = _synthetic_ndvi(days)
        raw = {
            "ndvi": ndvi,
            "canopy_cover": ndvi_to_canopy(ndvi),
            "dates": [],
            "provider": "synthetic-fallback",
            "count": len(ndvi),
            "error": str(e)[:120],
        }
    return attach_analysis("ndvi", raw)


@router.get("/runs")
async def runs_list(
    model: Optional[str] = None,
    farm_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    try:
        from apps.simulation.run_store import list_runs, run_to_dict

        rows = await list_runs(session, model=model, farm_id=farm_id, limit=limit)
        return {"data": [run_to_dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"data": [], "count": 0, "error": str(e)[:160]}


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


@router.post("/rothc")
async def rothc_run(
    years: int = Query(10, ge=1, le=100),
    soc_t_ha: float = Query(40.0),
    c_input_t_ha_y: float = Query(1.5),
    clay_pct: float = Query(25.0),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.rothc_model import run_rothc

    params = {
        "years": years,
        "soc_t_ha": soc_t_ha,
        "c_input_t_ha_y": c_input_t_ha_y,
        "clay_pct": clay_pct,
    }
    result = attach_analysis("rothc", run_rothc(params))
    try:
        from apps.simulation.run_store import save_run_async

        row = await save_run_async(session, "rothc_26_3", params, result)
        result["run_id"] = row.id
    except Exception as e:
        result["persist_error"] = str(e)[:200]
    return result


@router.post("/scenarios")
async def scenarios(
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.scenario_engine import run_scenarios

    return run_scenarios()


@router.get("/formulas")
async def formulas_catalog() -> dict[str, Any]:
    """Catalog of formulas for UI."""
    return {
        "items": [
            {
                "id": "scs_cn",
                "title_fa": "رواناب SCS-CN",
                "title_en": "SCS Curve Number runoff",
                "formulas": [
                    "S = 25.4 × (1000/CN − 10)",
                    "Q = (P − 0.2S)² / (P + 0.8S)  if P > 0.2S",
                ],
                "why_fa": "برآورد سهم بارش که به رواناب سطحی تبدیل می‌شود؛ پایه مدیریت فرسایش و سیل.",
                "why_en": "Estimates how much rainfall becomes surface runoff; erosion/flood planning.",
            },
            {
                "id": "aquacrop_ky",
                "title_fa": "بیلان آب و عملکرد (FAO Ky)",
                "title_en": "Water balance & yield (FAO Ky)",
                "formulas": [
                    "ETc = Kc × ET0",
                    "Y/Yx = 1 − Ky × (1 − Ta/Tc)",
                ],
                "why_fa": "ربط تنش آبی ریشه به کاهش عملکرد؛ کمک به زمان‌بندی آبیاری.",
                "why_en": "Links root-zone water stress to yield loss; irrigation timing.",
            },
            {
                "id": "rothc",
                "title_fa": "کربن آلی خاک RothC",
                "title_en": "Soil organic carbon RothC",
                "formulas": ["pool decay with a(T)·b(θ)·c(cover)", "DPM/RPM/BIO/HUM/IOM"],
                "why_fa": "مسیر کربن خاک تحت مدیریت بقایا و اقلیم.",
                "why_en": "Soil C trajectory under residue and climate management.",
            },
            {
                "id": "ndvi",
                "title_fa": "NDVI و پوشش تاج",
                "title_en": "NDVI and canopy cover",
                "formulas": [
                    "NDVI = (NIR − Red)/(NIR + Red)",
                    "CC = clamp((NDVI − 0.15)/0.70)",
                ],
                "why_fa": "پایش سبزینگی و کالیبره Kc در بیلان آب.",
                "why_en": "Greenness monitoring and Kc scaling for water balance.",
            },
        ]
    }

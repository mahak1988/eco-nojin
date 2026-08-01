"""Science API — process models + soil + global SA + final reports.

Public compute: aquacrop-advanced, rothc, coupled-run, maturity, crop-library.
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field, field_validator
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


def _safe_float(v: Any, default: float) -> float:
    try:
        x = float(v)
        if x != x:
            return default
        return x
    except (TypeError, ValueError):
        return default


def _safe_int(v: Any, default: int, lo: int, hi: int) -> int:
    try:
        x = int(round(float(v)))
    except (TypeError, ValueError):
        x = default
    return max(lo, min(hi, x))


class AquaBody(BaseModel):
    model_config = ConfigDict(extra="ignore")

    area_ha: float = 1.0
    days: int = 90
    et0_mm_day: float = 4.5
    kc: float = 1.1
    rain_mm_day: float = 0.5
    taw_mm: float = 100.0
    ky: float = 1.15
    y_potential_t_ha: float = 6.0
    irrig_threshold_frac: float = 0.55
    canopy_cover: Optional[list[float]] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    use_ndvi_canopy: bool = False
    farm_id: Optional[int] = None
    persist: bool = False
    crop: str = "wheat"
    soc_t_ha: float = 40.0
    c_input_t_ha_y: float = 1.5
    clay_pct: float = 25.0
    rothc_years: int = 10

    @field_validator("days", "rothc_years", mode="before")
    @classmethod
    def _days(cls, v: Any) -> int:
        return _safe_int(v, 90, 1, 365)

    @field_validator(
        "area_ha",
        "et0_mm_day",
        "kc",
        "rain_mm_day",
        "taw_mm",
        "ky",
        "y_potential_t_ha",
        "irrig_threshold_frac",
        "soc_t_ha",
        "c_input_t_ha_y",
        "clay_pct",
        mode="before",
    )
    @classmethod
    def _floats(cls, v: Any) -> float:
        return _safe_float(v, 0.0)

    @field_validator("crop", mode="before")
    @classmethod
    def _crop(cls, v: Any) -> str:
        s = str(v or "wheat").lower().strip() or "wheat"
        return s.split()[0][:32]


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
    farm_id: Optional[int] = None
    persist: bool = True


class RusleBody(BaseModel):
    R: float = 150.0
    K: float = 0.32
    slope_length_m: float = 50.0
    slope_pct: float = 5.0
    C: float = 0.2
    P: float = 0.8


class SoilProfileBody(BaseModel):
    sand_pct: float = 40.0
    silt_pct: float = 35.0
    clay_pct: float = 25.0
    soc_surface_pct: float = 1.2
    moisture_frac: float = 0.55
    layers_cm: Optional[list[float]] = None


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
    from apps.simulation.science_maturity import science_maturity_report

    mat = science_maturity_report()
    return {
        "phase": 3,
        "wave": 3,
        "router": "apps.api.routes.science",
        "database": db_kind,
        "models": [
            "aquacrop_advanced",
            "rothc",
            "coupled_science",
            "ndvi_canopy",
            "swat_plus_proxy",
            "rusle2_proxy",
            "soil_profile",
            "ml",
        ],
        "ok": True,
        "auth": "public: aquacrop-advanced, rothc, coupled-run, maturity, crop-library",
        "crop_library": "/api/v1/science/crop-library",
        "coupled_run": "/api/v1/science/coupled-run",
        "maturity": "/api/v1/science/maturity",
        "overall_score_pct": mat.get("overall_score_pct"),
    }


@router.get("/maturity")
async def science_maturity() -> dict[str, Any]:
    from apps.simulation.science_maturity import science_maturity_report

    return science_maturity_report()


@router.get("/crop-library")
async def crop_library() -> dict[str, Any]:
    from apps.simulation.fao_crop_params import list_crops

    return {
        "source": "FAO56 Kc · FAO33 Ky (embedded indicative tables)",
        "note_en": "Offline defaults for DSS; calibrate with local agronomy.",
        "note_fa": "مقادیر پیش‌فرض آفلاین برای پشتیبانی تصمیم؛ با داده محلی کالیبره کنید.",
        "crops": list_crops(),
    }


@router.post("/coupled-run")
async def coupled_run(request: Request) -> dict[str, Any]:
    """AquaCrop + RothC + WUE/risks advisory in one payload (public)."""
    from apps.simulation.science_coupling import run_coupled_science

    try:
        raw_body = await request.json()
    except Exception:
        raw_body = {}
    if not isinstance(raw_body, dict):
        raw_body = {}
    try:
        body = AquaBody.model_validate(raw_body)
        params = body.model_dump()
    except Exception:
        params = dict(raw_body)
    params["days"] = _safe_int(params.get("days"), 90, 7, 365)
    return run_coupled_science(params)


@router.post("/swat")
async def swat_run(
    body: SwatBody,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.models_swat import run_swat_plus
    from apps.simulation.report_builder import report_scs

    params = body.model_dump()
    persist = params.pop("persist", True)
    farm_id = params.pop("farm_id", None)
    result = attach_analysis("scs", run_swat_plus(params))
    result["mode"] = "sync"
    result["report"] = report_scs(result)
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
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
    from apps.simulation.report_builder import report_aquacrop

    try:
        raw_body = await request.json()
    except Exception:
        raw_body = {}
    if not isinstance(raw_body, dict):
        raw_body = {}

    try:
        body = AquaBody.model_validate(raw_body)
    except Exception:
        body = AquaBody()

    params = body.model_dump()
    params["days"] = _safe_int(params.get("days"), 90, 7, 365)
    params["area_ha"] = max(0.01, _safe_float(params.get("area_ha"), 1.0))
    params["et0_mm_day"] = max(0.1, _safe_float(params.get("et0_mm_day"), 4.5))
    params["kc"] = max(0.1, min(2.5, _safe_float(params.get("kc"), 1.1)))
    params["rain_mm_day"] = max(0.0, _safe_float(params.get("rain_mm_day"), 0.5))
    params["taw_mm"] = max(10.0, _safe_float(params.get("taw_mm"), 100.0))
    params["ky"] = max(0.1, min(2.5, _safe_float(params.get("ky"), 1.15)))
    params["y_potential_t_ha"] = max(0.1, _safe_float(params.get("y_potential_t_ha"), 6.0))

    persist = bool(params.pop("persist", False))
    farm_id = params.pop("farm_id", None)
    use_ndvi = bool(params.pop("use_ndvi_canopy", False))
    lat, lon = params.pop("lat", None), params.pop("lon", None)
    for k in ("soc_t_ha", "c_input_t_ha_y", "clay_pct", "rothc_years"):
        params.pop(k, None)
    ndvi_meta = None
    if use_ndvi and lat is not None and lon is not None and not params.get("canopy_cover"):
        try:
            from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

            bridge = await fetch_ndvi_canopy_async(float(lat), float(lon), days=int(params.get("days", 90)))
            params["canopy_cover"] = bridge["canopy_cover"]
            ndvi_meta = {"provider": bridge["provider"], "count": bridge["count"]}
        except Exception as e:
            ndvi_meta = {"error": str(e)[:120], "provider": "none"}
    try:
        raw = run_aquacrop_advanced(params)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"aquacrop failed: {e}") from e
    result = attach_analysis("aquacrop", raw)
    result["mode"] = "sync"
    result["report"] = report_aquacrop(result)
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
    with_sa: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    from apps.simulation.report_builder import report_rothc
    from apps.simulation.rothc_model import run_rothc

    params = {
        "years": years,
        "soc_t_ha": soc_t_ha,
        "c_input_t_ha_y": c_input_t_ha_y,
        "clay_pct": clay_pct,
    }
    result = attach_analysis("rothc", run_rothc(params))
    sa = None
    if with_sa:
        from apps.simulation.soil_sensitivity import global_sa_rothc

        sa = global_sa_rothc(n_src=80, n_morris=8, n_sobol=24)
        result["global_sensitivity"] = sa
    result["report"] = report_rothc(result, sensitivity=sa)
    try:
        from apps.simulation.run_store import save_run_async

        row = await save_run_async(session, "rothc_26_3", params, result)
        result["run_id"] = row.id
    except Exception as e:
        result["persist_error"] = str(e)[:200]
    return result


@router.post("/soil/rusle")
async def soil_rusle(
    body: RusleBody,
    with_sa: bool = Query(False),
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.report_builder import report_rusle
    from apps.simulation.soil_models import run_rusle2

    raw = run_rusle2(body.model_dump())
    result = attach_analysis("rusle", raw)
    sa = None
    if with_sa:
        from apps.simulation.soil_sensitivity import global_sa_rusle

        sa = global_sa_rusle(n_src=80, n_morris=8, n_sobol=24)
        result["global_sensitivity"] = sa
    result["report"] = report_rusle(result, sensitivity=sa)
    return result


@router.post("/soil/profile")
async def soil_profile(body: SoilProfileBody) -> dict[str, Any]:
    from apps.simulation.soil_models import run_soil_profile

    params = body.model_dump()
    if not params.get("layers_cm"):
        params.pop("layers_cm", None)
    return run_soil_profile(params)


@router.get("/sensitivity/rothc")
async def sa_rothc(
    n_sobol: int = Query(32, ge=16, le=96),
    n_morris: int = Query(10, ge=4, le=30),
    n_src: int = Query(100, ge=40, le=400),
) -> dict[str, Any]:
    from apps.simulation.soil_sensitivity import global_sa_rothc

    return global_sa_rothc(n_src=n_src, n_morris=n_morris, n_sobol=n_sobol)


@router.get("/sensitivity/rusle")
async def sa_rusle(
    n_sobol: int = Query(32, ge=16, le=96),
    n_morris: int = Query(10, ge=4, le=30),
    n_src: int = Query(100, ge=40, le=400),
) -> dict[str, Any]:
    from apps.simulation.soil_sensitivity import global_sa_rusle

    return global_sa_rusle(n_src=n_src, n_morris=n_morris, n_sobol=n_sobol)


@router.post("/scenarios")
async def scenarios(
    _: object = Depends(_perm("simulation:write")),
) -> dict[str, Any]:
    from apps.simulation.scenario_engine import run_scenarios

    return run_scenarios()


@router.get("/formulas")
async def formulas_catalog() -> dict[str, Any]:
    return {
        "items": [
            {
                "id": "scs_cn",
                "title_fa": "رواناب SCS-CN",
                "formulas": ["S = 25.4 × (1000/CN − 10)", "Q = (P − 0.2S)² / (P + 0.8S)"],
            },
            {
                "id": "aquacrop_ky",
                "title_fa": "بیلان آب و عملکرد (FAO Ky)",
                "formulas": ["ETc = Kc × ET0", "Y/Yx = 1 − Ky × (1 − Ta/Tc)"],
                "library": "/api/v1/science/crop-library",
            },
            {
                "id": "rothc",
                "title_fa": "کربن آلی خاک RothC",
                "formulas": ["a(T)·b(θ)·c(cover)", "DPM/RPM/BIO/HUM/IOM"],
            },
            {
                "id": "coupled",
                "title_fa": "اجرای جفت‌شده آب-محصول + کربن خاک",
                "endpoint": "/api/v1/science/coupled-run",
            },
            {
                "id": "ndvi",
                "title_fa": "NDVI و پوشش تاج",
                "formulas": ["NDVI = (NIR − Red)/(NIR + Red)", "CC = clamp((NDVI − 0.15)/0.70)"],
            },
        ]
    }

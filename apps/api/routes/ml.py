"""Machine learning API — yield / risk / anomaly / local+global sensitivity."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/ml", tags=["Machine Learning"])


class PredictBody(BaseModel):
    et0_mm_day: float = 4.5
    rain_mm_day: float = 0.5
    mean_ndvi: float = 0.45
    mean_canopy: float = 0.5
    soil_moisture: float = 30.0
    air_temp_c: float = 28.0
    irrigation_need_mm: float = 120.0
    yield_relative_proxy: float = 0.75
    runoff_mm_year: float = 40.0
    soc_delta: float = 0.0


class SensitivityBody(BaseModel):
    baseline: dict[str, float] | None = None
    rel_step: float = Field(0.10, ge=0.01, le=0.5)
    pd_features: list[str] | None = None
    pd_points: int = Field(12, ge=5, le=40)


@router.get("/status")
async def ml_status() -> dict[str, Any]:
    from apps.ml.service import get_bundle

    try:
        b = get_bundle()
        return {
            "ok": True,
            "engine": "econojin-pure-python",
            "models": ["linear_yield", "logistic_risk", "zscore_anomaly"],
            "metrics": b.metrics,
            "sklearn": False,
            "sensitivity_local": ["coefficient", "oat", "partial_dependence", "tornado"],
            "sensitivity_global": ["SRC", "Morris", "Saltelli-Sobol"],
            "notes_fa": "بدون وابستگی sklearn/SALib — pure Python.",
        }
    except Exception as e:
        return {"ok": False, "error": str(e)[:160]}


@router.post("/train")
async def ml_train(n_samples: int = Query(1000, ge=200, le=5000)) -> dict[str, Any]:
    from apps.ml.service import train_default_models

    return train_default_models(n_samples=n_samples)


@router.post("/predict")
async def ml_predict(body: PredictBody) -> dict[str, Any]:
    from apps.ml.service import predict_bundle

    return predict_bundle(body.model_dump())


@router.post("/predict-from-watch")
async def ml_from_watch(lat: float = 32.65, lon: float = 51.67, days: int = 40) -> dict[str, Any]:
    from apps.ml.service import predict_from_watch
    from apps.simulation.model_monitors import run_full_watch

    watch = run_full_watch(
        lat=lat,
        lon=lon,
        include_sensors=True,
        aquacrop_params={"days": days, "lat": lat, "lon": lon},
    )
    pred = predict_from_watch(watch)
    pred["watch_counts"] = watch.get("counts")
    pred["watch_metrics"] = watch.get("metrics")
    return pred


@router.get("/features")
async def ml_features() -> dict[str, Any]:
    from apps.ml.features import FEATURE_NAMES

    return {
        "features": FEATURE_NAMES,
        "description_fa": {
            "et0_mm_day": "تبخیر-تعرق مرجع روزانه",
            "rain_mm_day": "بارش روزانه",
            "mean_ndvi": "میانگین NDVI",
            "mean_canopy": "پوشش تاج",
            "soil_moisture": "رطوبت خاک %",
            "air_temp_c": "دمای هوا",
            "irrigation_need_mm": "نیاز آبیاری فصل",
            "yield_relative_proxy": "عملکرد نسبی (پروکسی)",
            "runoff_mm_year": "رواناب سالانه",
            "soc_delta": "تغییر کربن آلی خاک",
        },
    }


@router.get("/sensitivity")
async def ml_sensitivity_get(
    rel_step: float = Query(0.10, ge=0.01, le=0.5),
) -> dict[str, Any]:
    from apps.ml.sensitivity import full_sensitivity_report

    return full_sensitivity_report(rel_step=rel_step)


@router.post("/sensitivity")
async def ml_sensitivity_post(body: SensitivityBody) -> dict[str, Any]:
    from apps.ml.sensitivity import full_sensitivity_report

    return full_sensitivity_report(
        body.baseline,
        rel_step=body.rel_step,
        pd_features=body.pd_features,
        pd_points=body.pd_points,
    )


@router.get("/sensitivity/oat")
async def ml_sensitivity_oat(rel_step: float = Query(0.10, ge=0.01, le=0.5)) -> dict[str, Any]:
    from apps.ml.sensitivity import oat_sensitivity

    return oat_sensitivity(rel_step=rel_step)


@router.get("/sensitivity/coefficients")
async def ml_sensitivity_coef() -> dict[str, Any]:
    from apps.ml.sensitivity import coefficient_importance

    return coefficient_importance()


@router.get("/sensitivity/partial")
async def ml_sensitivity_pd(
    feature: str = Query("mean_ndvi"),
    points: int = Query(12, ge=5, le=40),
) -> dict[str, Any]:
    from apps.ml.sensitivity import partial_dependence

    try:
        return partial_dependence(feature, points=points)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.get("/sensitivity/global")
async def ml_sensitivity_global(
    n_src: int = Query(120, ge=40, le=800),
    n_morris: int = Query(12, ge=4, le=40),
    n_sobol: int = Query(32, ge=16, le=128),
    target: str = Query("yield", pattern="^(yield|risk)$"),
    seed: int = Query(42),
) -> dict[str, Any]:
    """SRC + Morris + Saltelli–Sobol combined report."""
    from apps.ml.global_sensitivity import full_global_sensitivity

    return full_global_sensitivity(
        n_src=n_src, n_morris=n_morris, n_sobol=n_sobol, seed=seed, target=target
    )


@router.get("/sensitivity/sobol")
async def ml_sensitivity_sobol(
    n_base: int = Query(48, ge=16, le=128),
    target: str = Query("yield", pattern="^(yield|risk)$"),
    seed: int = Query(42),
) -> dict[str, Any]:
    from apps.ml.global_sensitivity import saltelli_sobol
    from apps.ml.service import get_bundle

    get_bundle()
    return saltelli_sobol(n_base=n_base, seed=seed, target=target)


@router.get("/sensitivity/morris")
async def ml_sensitivity_morris(
    n_trajectories: int = Query(16, ge=4, le=40),
    levels: int = Query(6, ge=4, le=12),
    target: str = Query("yield", pattern="^(yield|risk)$"),
    seed: int = Query(42),
) -> dict[str, Any]:
    from apps.ml.global_sensitivity import morris_elementary_effects
    from apps.ml.service import get_bundle

    get_bundle()
    return morris_elementary_effects(
        n_trajectories=n_trajectories, levels=levels, seed=seed, target=target
    )


@router.get("/sensitivity/src")
async def ml_sensitivity_src(
    n_samples: int = Query(180, ge=40, le=1000),
    target: str = Query("yield", pattern="^(yield|risk)$"),
    seed: int = Query(42),
) -> dict[str, Any]:
    from apps.ml.global_sensitivity import standardized_regression_coefficients
    from apps.ml.service import get_bundle

    get_bundle()
    return standardized_regression_coefficients(n_samples=n_samples, seed=seed, target=target)

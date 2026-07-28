"""Machine learning API — yield / risk / anomaly."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Query
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
            "notes_fa": "بدون وابستگی sklearn — قابل اجرا روی هر محیط.",
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
    """Run full science watch then ML on resulting metrics."""
    from apps.ml.service import predict_from_watch
    from apps.simulation.model_monitors import run_full_watch

    watch = run_full_watch(lat=lat, lon=lon, include_sensors=True, aquacrop_params={"days": days, "lat": lat, "lon": lon})
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

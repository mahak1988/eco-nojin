"""Train / load / predict facade for agricultural ML."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from apps.ml.classical import (
    ModelBundle,
    fit_linear,
    fit_logistic,
    fit_zscore,
    load_bundle,
    save_bundle,
)
from apps.ml.features import FEATURE_NAMES, vector_from_dict
from apps.ml.synthetic_data import generate_dataset

_ROOT = Path(__file__).resolve().parents[2]
_MODEL_PATH = _ROOT / "data" / "ml_models.json"
_BUNDLE: Optional[ModelBundle] = None


def train_default_models(n_samples: int = 1000, seed: int = 42) -> dict[str, Any]:
    global _BUNDLE
    X, y_reg, y_cls = generate_dataset(n_samples, seed=seed)
    # hold-out last 20%
    cut = int(len(X) * 0.8)
    Xtr, Xte = X[:cut], X[cut:]
    ytr, yte = y_reg[:cut], y_reg[cut:]
    ctr, cte = y_cls[:cut], y_cls[cut:]

    reg = fit_linear(Xtr, ytr)
    clf = fit_logistic(Xtr, ctr, classes=["low", "medium", "high"])
    anom = fit_zscore(Xtr, threshold=2.8)

    # metrics
    mae = sum(abs(reg.predict(x) - yt) for x, yt in zip(Xte, yte)) / max(len(Xte), 1)
    acc = sum(1 for x, yt in zip(Xte, cte) if clf.predict(x) == yt) / max(len(Xte), 1)

    bundle = ModelBundle(
        yield_regressor=reg,
        risk_classifier=clf,
        anomaly=anom,
        metrics={
            "n_train": len(Xtr),
            "n_test": len(Xte),
            "yield_mae": round(mae, 4),
            "risk_accuracy": round(acc, 4),
            "features": FEATURE_NAMES,
            "engine": "econojin-pure-python",
            "notes_fa": "مدل‌ها روی داده مصنوعی فیزیک‌مبنا آموزش دیده‌اند؛ برای production با داده واقعی بازآموزش دهید.",
            "notes_en": "Trained on physics-inspired synthetic data; retrain with real farm data for production.",
        },
    )
    save_bundle(bundle, _MODEL_PATH)
    _BUNDLE = bundle
    return {"ok": True, "path": str(_MODEL_PATH), "metrics": bundle.metrics}


def get_bundle(force_train: bool = False) -> ModelBundle:
    global _BUNDLE
    if force_train or _BUNDLE is None:
        loaded = None if force_train else load_bundle(_MODEL_PATH)
        if loaded is None:
            train_default_models()
            loaded = _BUNDLE
        _BUNDLE = loaded
    assert _BUNDLE is not None
    return _BUNDLE


def predict_bundle(features: dict[str, Any]) -> dict[str, Any]:
    bundle = get_bundle()
    x = vector_from_dict(features)
    y_hat = bundle.yield_regressor.predict(x)
    y_hat = max(0.0, min(1.0, y_hat))
    proba = bundle.risk_classifier.predict_proba(x)
    label = bundle.risk_classifier.predict(x)
    anom = bundle.anomaly.score(x)

    advice_fa = {
        "low": "ریسک پایین — برنامه آبیاری و تغذیه را حفظ کنید.",
        "medium": "ریسک متوسط — پایش NDVI و رطوبت خاک را افزایش دهید.",
        "high": "ریسک بالا — آبیاری تکمیلی، سایه‌اندازی یا تغییر تاریخ کاشت را بررسی کنید.",
    }.get(label, "")

    return {
        "engine": "econojin-ml-v1",
        "features_used": FEATURE_NAMES,
        "input": {k: features.get(k) for k in FEATURE_NAMES},
        "yield_relative_pred": round(y_hat, 4),
        "yield_t_ha_proxy": round(y_hat * 6.0, 3),  # scale to wheat-like potential
        "risk_label": label,
        "risk_proba": {k: round(v, 4) for k, v in proba.items()},
        "anomaly": anom,
        "advice_fa": advice_fa,
        "model_metrics": bundle.metrics,
    }


def predict_from_watch(watch: dict[str, Any]) -> dict[str, Any]:
    """Map monitor/watch metrics into ML features."""
    m = watch.get("metrics") or {}
    sensors = watch.get("sensors") or {}
    features = {
        "et0_mm_day": 5.0,
        "rain_mm_day": sensors.get("rainfall_24h_mm", 0.5),
        "mean_ndvi": m.get("mean_ndvi", 0.45),
        "mean_canopy": m.get("mean_canopy", 0.5),
        "soil_moisture": sensors.get("soil_moisture", m.get("soil_moisture", 30)),
        "air_temp_c": sensors.get("air_temp_c", 28),
        "irrigation_need_mm": m.get("irrigation_need_mm", 120),
        "yield_relative_proxy": m.get("yield_relative", 0.7),
        "runoff_mm_year": m.get("runoff_mm_year", 40),
        "soc_delta": m.get("delta", 0.0),
    }
    pred = predict_bundle(features)
    pred["source"] = "watch_metrics"
    return pred

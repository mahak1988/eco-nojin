"""
Sensitivity analysis for Econojin ML models.

Methods:
1. Coefficient importance (standardized weights for linear / logistic)
2. One-at-a-time (OAT) local elasticity around a baseline feature vector
3. Partial dependence-style sweeps (1D) for top features
4. Tornado ranking by |Δ output|
"""

from __future__ import annotations

from typing import Any

from apps.ml.features import FEATURE_NAMES
from apps.ml.service import get_bundle, predict_bundle

# Typical operational ranges for sweeps (min, max)
FEATURE_RANGES: dict[str, tuple[float, float]] = {
    "et0_mm_day": (2.0, 8.0),
    "rain_mm_day": (0.0, 3.5),
    "mean_ndvi": (0.1, 0.85),
    "mean_canopy": (0.1, 0.9),
    "soil_moisture": (10.0, 55.0),
    "air_temp_c": (15.0, 45.0),
    "irrigation_need_mm": (20.0, 450.0),
    "yield_relative_proxy": (0.2, 0.95),
    "runoff_mm_year": (0.0, 200.0),
    "soc_delta": (-3.0, 2.0),
}

DEFAULT_BASELINE: dict[str, float] = {
    "et0_mm_day": 4.5,
    "rain_mm_day": 0.5,
    "mean_ndvi": 0.45,
    "mean_canopy": 0.5,
    "soil_moisture": 30.0,
    "air_temp_c": 28.0,
    "irrigation_need_mm": 120.0,
    "yield_relative_proxy": 0.75,
    "runoff_mm_year": 40.0,
    "soc_delta": 0.0,
}


def coefficient_importance() -> dict[str, Any]:
    """Importance from model coefficients (absolute standardized weights)."""
    bundle = get_bundle()
    reg = bundle.yield_regressor
    # weights last element is bias
    w = reg.weights[:-1]
    yield_imp = []
    for name, coef, std in zip(FEATURE_NAMES, w, reg.feature_stds):
        # effect of +1 raw unit ≈ coef / std on normalized scale, but coef already on norm space
        # sensitivity of output to +1 std of feature ≈ |coef| * target_std
        effect = abs(coef) * (reg.target_std or 1.0)
        yield_imp.append(
            {"feature": name, "abs_coef": round(abs(coef), 6), "effect_per_std": round(effect, 6)}
        )
    yield_imp.sort(key=lambda r: r["effect_per_std"], reverse=True)

    clf = bundle.risk_classifier
    risk_imp: list[dict[str, Any]] = []
    # average |coef| across classes for each feature
    d = len(FEATURE_NAMES)
    for j, name in enumerate(FEATURE_NAMES):
        vals = [abs(row[j]) for row in clf.weights]
        avg = sum(vals) / max(len(vals), 1)
        risk_imp.append({"feature": name, "mean_abs_coef": round(avg, 6)})
    risk_imp.sort(key=lambda r: r["mean_abs_coef"], reverse=True)

    return {
        "method": "coefficient_importance",
        "yield": yield_imp,
        "risk": risk_imp,
        "notes_fa": "اهمیت بر اساس قدر مطلق ضرایب استانداردشده؛ برای مدل خطی/لجستیک معتبر است.",
        "notes_en": "Importance from absolute standardized coefficients.",
    }


def oat_sensitivity(
    baseline: dict[str, float] | None = None,
    *,
    rel_step: float = 0.10,
    abs_floor: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    One-at-a-time: perturb each feature ±rel_step (or abs_floor) and measure Δ yield and risk proba.
    Elasticity ≈ (Δy / y) / (Δx / x) when x ≠ 0.
    """
    base = dict(DEFAULT_BASELINE)
    if baseline:
        base.update({k: float(v) for k, v in baseline.items() if k in FEATURE_NAMES})
    floors = abs_floor or {
        "et0_mm_day": 0.3,
        "rain_mm_day": 0.1,
        "mean_ndvi": 0.03,
        "mean_canopy": 0.03,
        "soil_moisture": 2.0,
        "air_temp_c": 1.0,
        "irrigation_need_mm": 15.0,
        "yield_relative_proxy": 0.05,
        "runoff_mm_year": 5.0,
        "soc_delta": 0.2,
    }

    y0 = predict_bundle(base)
    y0_val = float(y0["yield_relative_pred"])
    p0 = y0["risk_proba"]

    rows: list[dict[str, Any]] = []
    for name in FEATURE_NAMES:
        x0 = float(base[name])
        step = max(abs(x0) * rel_step, float(floors.get(name, 0.05)))
        low = dict(base)
        high = dict(base)
        low[name] = x0 - step
        high[name] = x0 + step
        # clamp to range if known
        lo_r, hi_r = FEATURE_RANGES.get(name, (None, None))
        if lo_r is not None:
            low[name] = max(lo_r, low[name])
            high[name] = min(hi_r, high[name])  # type: ignore[arg-type]

        yl = predict_bundle(low)
        yh = predict_bundle(high)
        y_lo = float(yl["yield_relative_pred"])
        y_hi = float(yh["yield_relative_pred"])
        dy = y_hi - y_lo
        dx = high[name] - low[name]
        elasticity = None
        if abs(x0) > 1e-9 and abs(y0_val) > 1e-9 and abs(dx) > 1e-12:
            elasticity = (dy / (2 * step if abs(dx) < 1e-12 else dx)) * (x0 / y0_val)
            # simpler central difference elasticity
            elasticity = (dy / dx) * (x0 / y0_val)

        # risk: change in P(high)
        ph_lo = float(yl["risk_proba"].get("high", 0))
        ph_hi = float(yh["risk_proba"].get("high", 0))
        d_phigh = ph_hi - ph_lo

        rows.append(
            {
                "feature": name,
                "baseline": round(x0, 4),
                "step": round(step, 4),
                "yield_low": round(y_lo, 4),
                "yield_high": round(y_hi, 4),
                "delta_yield": round(dy, 4),
                "abs_delta_yield": round(abs(dy), 4),
                "elasticity": round(elasticity, 4) if elasticity is not None else None,
                "delta_p_high": round(d_phigh, 4),
                "abs_delta_p_high": round(abs(d_phigh), 4),
                "risk_low": yl["risk_label"],
                "risk_high": yh["risk_label"],
            }
        )

    tornado_yield = sorted(rows, key=lambda r: r["abs_delta_yield"], reverse=True)
    tornado_risk = sorted(rows, key=lambda r: r["abs_delta_p_high"], reverse=True)

    return {
        "method": "oat",
        "rel_step": rel_step,
        "baseline": base,
        "baseline_prediction": {
            "yield_relative_pred": y0_val,
            "risk_label": y0["risk_label"],
            "risk_proba": y0["risk_proba"],
        },
        "features": rows,
        "tornado_yield": [
            {
                "feature": r["feature"],
                "abs_delta_yield": r["abs_delta_yield"],
                "delta_yield": r["delta_yield"],
            }
            for r in tornado_yield
        ],
        "tornado_risk": [
            {
                "feature": r["feature"],
                "abs_delta_p_high": r["abs_delta_p_high"],
                "delta_p_high": r["delta_p_high"],
            }
            for r in tornado_risk
        ],
        "notes_fa": "هر ویژگی جداگانه ±گام جابه‌جا می‌شود؛ بقیه ثابت. نمودار گردباد رتبه اثر را نشان می‌دهد.",
        "notes_en": "One-at-a-time ±step; tornado ranks absolute effect on yield and P(high).",
    }


def partial_dependence(
    feature: str,
    baseline: dict[str, float] | None = None,
    *,
    points: int = 15,
) -> dict[str, Any]:
    """1D partial dependence: sweep feature across range, fix others at baseline."""
    if feature not in FEATURE_NAMES:
        raise ValueError(f"unknown feature: {feature}")
    base = dict(DEFAULT_BASELINE)
    if baseline:
        base.update({k: float(v) for k, v in baseline.items() if k in FEATURE_NAMES})
    lo, hi = FEATURE_RANGES.get(feature, (0.0, 1.0))
    points = max(points, 3)
    grid = [lo + (hi - lo) * i / (points - 1) for i in range(points)]
    series = []
    for v in grid:
        f = dict(base)
        f[feature] = v
        pred = predict_bundle(f)
        series.append(
            {
                "x": round(v, 4),
                "yield_relative_pred": pred["yield_relative_pred"],
                "risk_label": pred["risk_label"],
                "p_high": round(float(pred["risk_proba"].get("high", 0)), 4),
                "p_medium": round(float(pred["risk_proba"].get("medium", 0)), 4),
                "p_low": round(float(pred["risk_proba"].get("low", 0)), 4),
            }
        )
    return {
        "method": "partial_dependence",
        "feature": feature,
        "range": [lo, hi],
        "baseline": base,
        "series": series,
        "notes_fa": "وابستگی جزئی تک‌متغیره: فقط این ویژگی روی بازه جاروب می‌شود.",
        "notes_en": "1D partial dependence sweep for one feature.",
    }


def full_sensitivity_report(
    baseline: dict[str, float] | None = None,
    *,
    rel_step: float = 0.10,
    pd_features: list[str] | None = None,
    pd_points: int = 12,
) -> dict[str, Any]:
    """Combined report for API / UI."""
    coef = coefficient_importance()
    oat = oat_sensitivity(baseline, rel_step=rel_step)
    # PD for top-3 yield-sensitive features
    top = [r["feature"] for r in oat["tornado_yield"][:3]]
    if pd_features:
        top = [f for f in pd_features if f in FEATURE_NAMES][:5]
    pds = [partial_dependence(f, baseline or oat["baseline"], points=pd_points) for f in top]
    return {
        "engine": "econojin-ml-sensitivity-v1",
        "coefficient_importance": coef,
        "oat": oat,
        "partial_dependence": pds,
        "summary_fa": _summary_fa(oat),
        "summary_en": _summary_en(oat),
    }


def _summary_fa(oat: dict[str, Any]) -> str:
    top = oat["tornado_yield"][:3]
    names = "، ".join(t["feature"] for t in top)
    return (
        f"حساس‌ترین ویژگی‌ها برای عملکرد نسبی: {names}. "
        f"پیش‌بینی پایه={oat['baseline_prediction']['yield_relative_pred']:.2f} "
        f"با ریسک {oat['baseline_prediction']['risk_label']}."
    )


def _summary_en(oat: dict[str, Any]) -> str:
    top = oat["tornado_yield"][:3]
    names = ", ".join(t["feature"] for t in top)
    return (
        f"Top yield-sensitive features: {names}. "
        f"Baseline yield={oat['baseline_prediction']['yield_relative_pred']:.2f}, "
        f"risk={oat['baseline_prediction']['risk_label']}."
    )

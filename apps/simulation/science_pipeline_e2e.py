"""
Phase 5 — End-to-end free science + MRV pipeline.

Chain (all optional engines fall back safely):
  NDVI (Planetary/synthetic) → canopy → AquaCrop (conceptual|OSPy)
  → RothC (in-repo|pyRothC) → MRV L1/L2/L3 → EcoCoin issuable preview

Designed for zero-cost operation; no paid API keys required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from apps.api.services.mrv_standards import compute_issuable, quality_from_mrv_v2
from apps.satellite.processors.indices import canopy_cover_from_ndvi
from apps.simulation.aquacrop_ospy_engine import run_aquacrop_with_optional_ospy
from apps.simulation.rothc_pyrothc_engine import run_rothc_with_optional_pyrothc

# Preset: wheat near Isfahan (approx.)
ISFAHAN_WHEAT: dict[str, Any] = {
    "scenario_id": "isfahan-wheat",
    "label_en": "Wheat near Isfahan (demo)",
    "label_fa": "گندم حوالی اصفهان (دمو)",
    "lat": 32.65,
    "lon": 51.67,
    "crop": "wheat",
    "days": 90,
    "area_ha": 1.0,
    "et0_mm_day": 5.2,
    "rain_mm_day": 0.3,
    "soc_t_ha": 38.0,
    "c_input_t_ha_y": 1.8,
    "clay_pct": 28.0,
    "rothc_years": 10,
    "credit_type_factor": 25.0,
    "measured_value": 40.0,
}


def _ndvi_series_offline(days: int = 90) -> dict[str, Any]:
    """Deterministic synthetic NDVI curve (offline / test-safe)."""
    from apps.simulation.ndvi_canopy import _synthetic_ndvi, ndvi_to_canopy

    ndvi = _synthetic_ndvi(days)
    canopy = ndvi_to_canopy(ndvi)
    mean_ndvi = sum(ndvi) / len(ndvi) if ndvi else 0.55
    return {
        "ndvi": ndvi,
        "canopy_cover": canopy,
        "mean_ndvi": round(mean_ndvi, 4),
        "provider": "synthetic-offline",
        "count": len(ndvi),
    }


async def _ndvi_series_live(lat: float, lon: float, days: int) -> dict[str, Any]:
    try:
        from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async

        raw = await fetch_ndvi_canopy_async(lat, lon, days)
        ndvi = raw.get("ndvi") or []
        mean_ndvi = sum(ndvi) / len(ndvi) if ndvi else float(raw.get("mean_ndvi") or 0.55)
        return {
            "ndvi": ndvi,
            "canopy_cover": raw.get("canopy_cover") or ndvi_to_canopy_safe(ndvi),
            "mean_ndvi": round(float(mean_ndvi), 4),
            "provider": raw.get("provider", "satellite-chain"),
            "count": int(raw.get("count") or len(ndvi)),
            "dates": raw.get("dates") or [],
        }
    except Exception as e:
        out = _ndvi_series_offline(days)
        out["fallback_error"] = str(e)[:120]
        return out


def ndvi_to_canopy_safe(ndvi: list[float]) -> list[float]:
    try:
        from apps.simulation.ndvi_canopy import ndvi_to_canopy

        return ndvi_to_canopy(ndvi)
    except Exception:
        return [canopy_cover_from_ndvi(v) for v in ndvi]


def run_pipeline_sync(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fully offline E2E (no network). Suitable for unit tests."""
    p = {**ISFAHAN_WHEAT, **(params or {})}
    days = int(p.get("days", 90))
    engine = str(p.get("engine", "conceptual")).lower()

    ndvi_block = _ndvi_series_offline(days)
    canopy = ndvi_block["canopy_cover"]
    mean_ndvi = float(ndvi_block["mean_ndvi"])

    aq_params = {
        "crop": p.get("crop", "wheat"),
        "days": days,
        "area_ha": float(p.get("area_ha", 1.0)),
        "et0_mm_day": float(p.get("et0_mm_day", 5.2)),
        "rain_mm_day": float(p.get("rain_mm_day", 0.3)),
        "canopy_cover": canopy,
        "engine": engine,
    }
    aq = run_aquacrop_with_optional_ospy(aq_params)

    rc_params = {
        "years": int(p.get("rothc_years", 10)),
        "soc_t_ha": float(p.get("soc_t_ha", 38.0)),
        "c_input_t_ha_y": float(p.get("c_input_t_ha_y", 1.8)),
        "clay_pct": float(p.get("clay_pct", 28.0)),
        "engine": engine,
    }
    rc = run_rothc_with_optional_pyrothc(rc_params)

    yield_t = float(aq.get("yield_t_ha") or 0.0)
    soc_final = float(rc.get("soc_final") or rc.get("soc_final_t_ha") or p.get("soc_t_ha") or 0)
    soc0 = float(p.get("soc_t_ha", 38.0))
    delta_soc = soc_final - soc0

    mrv = quality_from_mrv_v2(
        ndvi_observed=mean_ndvi,
        ndvi_expected=max(0.2, mean_ndvi * 0.95),
        model_yield_t_ha=yield_t,
        field_yield_t_ha=p.get("field_yield_t_ha"),
        model_soc_t_ha=soc_final,
        lab_soc_t_ha=p.get("lab_soc_t_ha"),
        field_data_present=p.get("field_yield_t_ha") is not None or p.get("lab_soc_t_ha") is not None,
        satellite_available=True,
        model_present=True,
        additionality_score=float(p.get("additionality_score", 1.0)),
        leakage_risk=float(p.get("leakage_risk", 0.0)),
    )

    measured = float(p.get("measured_value", max(abs(delta_soc), 1.0)))
    issuance = compute_issuable(
        measured_value=measured,
        credit_factor=float(p.get("credit_type_factor", 25.0)),
        mrv=mrv,
        region_multiplier=float(p.get("region_multiplier", 1.0)),
        scarcity=float(p.get("scarcity", 1.0)),
    )

    return {
        "pipeline": "e2e_free_science_mrv_v1",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "scenario": {
            "id": p.get("scenario_id", "custom"),
            "lat": p.get("lat"),
            "lon": p.get("lon"),
            "crop": p.get("crop"),
            "label_en": p.get("label_en"),
            "label_fa": p.get("label_fa"),
        },
        "ndvi": ndvi_block,
        "aquacrop": {
            "engine": aq.get("engine") or aq.get("model") or "aquacrop_advanced",
            "yield_t_ha": yield_t,
            "yield_relative": aq.get("yield_relative"),
            "disclaimer": aq.get("disclaimer"),
            "raw_keys": list(aq.keys())[:20],
        },
        "rothc": {
            "engine": rc.get("engine") or rc.get("model") or "rothc_26_3",
            "soc_initial": soc0,
            "soc_final": soc_final,
            "delta_soc": round(delta_soc, 4),
        },
        "mrv": mrv,
        "issuance": issuance,
        "kpis": {
            "mean_ndvi": mean_ndvi,
            "canopy_mean": round(sum(canopy) / len(canopy), 4) if canopy else None,
            "yield_t_ha": round(yield_t, 3),
            "delta_soc_t_ha": round(delta_soc, 3),
            "assurance_level": mrv.get("assurance_level"),
            "issuable": issuance.get("issuable"),
        },
        "cost": "zero",
        "notes_en": [
            "Default path is conceptual AquaCrop + in-repo RothC (offline).",
            "Set engine=ospy|pyrothc|free when packages are installed.",
            "NDVI uses synthetic offline series in sync mode; live mode uses Planetary-first chain.",
        ],
        "notes_fa": [
            "مسیر پیش‌فرض: AquaCrop مفهومی + RothC داخلی (آفلاین).",
            "با engine=ospy|pyrothc|free موتورهای pure-Python فعال می‌شوند.",
            "در حالت sync، NDVI مصنوعی است؛ در live از زنجیره Planetary اولویت دارد.",
        ],
    }


async def run_pipeline_async(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Live NDVI when network available; otherwise same as sync."""
    p = {**ISFAHAN_WHEAT, **(params or {})}
    days = int(p.get("days", 90))
    lat = float(p.get("lat", 32.65))
    lon = float(p.get("lon", 51.67))
    use_live = bool(p.get("use_live_ndvi", True))

    if use_live:
        ndvi_block = await _ndvi_series_live(lat, lon, days)
    else:
        ndvi_block = _ndvi_series_offline(days)

    # Reuse sync body with precomputed NDVI injected
    p2 = dict(p)
    p2["_ndvi_override"] = ndvi_block
    out = run_pipeline_sync(p2)
    # If override present, rebuild NDVI-dependent parts
    if p2.get("_ndvi_override"):
        canopy = ndvi_block.get("canopy_cover") or []
        mean_ndvi = float(ndvi_block.get("mean_ndvi") or 0.55)
        engine = str(p.get("engine", "conceptual")).lower()
        aq = run_aquacrop_with_optional_ospy(
            {
                "crop": p.get("crop", "wheat"),
                "days": days,
                "area_ha": float(p.get("area_ha", 1.0)),
                "et0_mm_day": float(p.get("et0_mm_day", 5.2)),
                "rain_mm_day": float(p.get("rain_mm_day", 0.3)),
                "canopy_cover": canopy,
                "engine": engine,
            }
        )
        rc = run_rothc_with_optional_pyrothc(
            {
                "years": int(p.get("rothc_years", 10)),
                "soc_t_ha": float(p.get("soc_t_ha", 38.0)),
                "c_input_t_ha_y": float(p.get("c_input_t_ha_y", 1.8)),
                "clay_pct": float(p.get("clay_pct", 28.0)),
                "engine": engine,
            }
        )
        yield_t = float(aq.get("yield_t_ha") or 0.0)
        soc0 = float(p.get("soc_t_ha", 38.0))
        soc_final = float(rc.get("soc_final") or rc.get("soc_final_t_ha") or soc0)
        delta_soc = soc_final - soc0
        mrv = quality_from_mrv_v2(
            ndvi_observed=mean_ndvi,
            ndvi_expected=max(0.2, mean_ndvi * 0.95),
            model_yield_t_ha=yield_t,
            field_yield_t_ha=p.get("field_yield_t_ha"),
            model_soc_t_ha=soc_final,
            lab_soc_t_ha=p.get("lab_soc_t_ha"),
            field_data_present=p.get("field_yield_t_ha") is not None
            or p.get("lab_soc_t_ha") is not None,
            satellite_available=True,
            model_present=True,
        )
        issuance = compute_issuable(
            measured_value=float(p.get("measured_value", max(abs(delta_soc), 1.0))),
            credit_factor=float(p.get("credit_type_factor", 25.0)),
            mrv=mrv,
        )
        out["ndvi"] = ndvi_block
        out["aquacrop"] = {
            "engine": aq.get("engine") or aq.get("model") or "aquacrop_advanced",
            "yield_t_ha": yield_t,
            "yield_relative": aq.get("yield_relative"),
        }
        out["rothc"] = {
            "engine": rc.get("engine") or rc.get("model") or "rothc_26_3",
            "soc_initial": soc0,
            "soc_final": soc_final,
            "delta_soc": round(delta_soc, 4),
        }
        out["mrv"] = mrv
        out["issuance"] = issuance
        out["kpis"] = {
            "mean_ndvi": mean_ndvi,
            "yield_t_ha": round(yield_t, 3),
            "delta_soc_t_ha": round(delta_soc, 3),
            "assurance_level": mrv.get("assurance_level"),
            "issuable": issuance.get("issuable"),
        }
    return out

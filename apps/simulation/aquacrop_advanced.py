"""
AquaCrop-style daily soil water balance + FAO yield response to water.

Equations (decision-support, open process):
  ETc = Kc · ET0
  Ks when depletion > RAW
  Y/Yx = 1 - Ky · (1 - Ta/Tc)   (FAO 33)

Crop defaults from ``apps.simulation.fao_crop_params`` (FAO56 / FAO33 tables).
Not the official FAO AquaCrop binary.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from apps.simulation.et0 import resolve_et0_mm_day
from apps.simulation.fao_crop_params import get_crop_params

ENGINE = "conceptual"
ENGINE_VERSION = "2.3.0"
DISCLAIMER_EN = (
    "Open process model aligned with FAO AquaCrop / FAO-33 concepts. "
    "Crop defaults from embedded FAO56/FAO33 tables. "
    "Not the official FAO AquaCrop binary. For decision support only."
)
DISCLAIMER_FA = (
    "مدل فرآیندی باز هم‌راستا با مفاهیم FAO AquaCrop / FAO-33. "
    "پارامترهای محصول از جداول داخلی FAO56/FAO33. "
    "باینری رسمی FAO نیست. فقط برای پشتیبانی تصمیم."
)


def _f(v: Any, default: float) -> float:
    try:
        x = float(v)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except (TypeError, ValueError):
        return default


def _i(v: Any, default: int, lo: int, hi: int) -> int:
    try:
        x = int(round(float(v)))
    except (TypeError, ValueError):
        x = default
    return max(lo, min(hi, x))


def run_aquacrop_advanced(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = dict(params or {})
    crop_meta = get_crop_params(str(p.get("crop", "wheat")))
    crop = crop_meta["crop_key"]

    days = _i(p.get("days", crop_meta.get("cycle_days", 90)), 90, 7, 365)
    area_ha = max(0.01, _f(p.get("area_ha", 1.0), 1.0))

    # Prefer explicit request values; else FAO library
    if "et0_mm_day" in p:
        et0_base = max(0.1, _f(p.get("et0_mm_day"), 4.5))
    else:
        et0_base = resolve_et0_mm_day(p)

    kc = _f(p.get("kc"), float(crop_meta["kc_mid"]))
    rain_base = max(0.0, _f(p.get("rain_mm_day"), 0.5))
    taw_mm = max(10.0, _f(p.get("taw_mm"), float(crop_meta["taw_mm_typical"])))
    raw_frac = _f(p.get("raw_fraction"), float(crop_meta["raw_fraction"]))
    raw_frac = max(0.1, min(0.95, raw_frac))
    ky = _f(p.get("ky"), float(crop_meta["ky"]))
    yx = max(0.1, _f(p.get("y_potential_t_ha"), float(crop_meta["yx_t_ha"])))
    irrig_threshold = max(0.2, min(0.95, _f(p.get("irrig_threshold_frac"), 0.55)))
    canopy = p.get("canopy_cover")
    climate_amp = max(0.0, min(0.8, _f(p.get("climate_amplitude"), 0.35)))

    raw_mm = taw_mm * raw_frac
    depletion = max(0.0, min(taw_mm, _f(p.get("initial_depletion_mm"), taw_mm * 0.35)))
    irrig_total = 0.0
    etc_total = 0.0
    rain_total = 0.0
    tc_total = 0.0
    ta_sum = 0.0
    series: list[dict[str, Any]] = []
    sample_every = 1 if days <= 120 else max(1, days // 100)

    for d in range(days):
        phase = math.sin(math.pi * d / max(days - 1, 1))
        et0 = max(0.2, et0_base * (1.0 + climate_amp * (phase - 0.15)))
        rain = max(0.0, rain_base * (1.0 + climate_amp * (0.5 - phase)))
        rain_total += rain

        if isinstance(canopy, list) and canopy:
            cc = float(canopy[min(d, len(canopy) - 1)])
            cc = max(0.05, min(1.0, cc))
        else:
            x = d / max(days - 1, 1)
            if x < 0.2:
                cc = 0.15 + 0.85 * (x / 0.2)
            elif x < 0.7:
                cc = 1.0
            else:
                cc = max(0.2, 1.0 - 0.8 * ((x - 0.7) / 0.3))

        kc_act = kc * (0.15 + 0.85 * cc)
        etc = et0 * kc_act
        etc_total += etc
        tc = etc
        tc_total += tc

        if depletion <= raw_mm:
            ks = 1.0
        else:
            ks = max(0.0, (taw_mm - depletion) / max(taw_mm - raw_mm, 1e-6))
        ta = tc * ks
        ta_sum += ta

        irr = 0.0
        if depletion / max(taw_mm, 1e-6) >= irrig_threshold:
            irr = min(depletion, max(raw_mm * 0.85, taw_mm * 0.25))
            irrig_total += irr

        fillable = max(0.0, taw_mm - depletion)
        infiltrated = min(rain + irr, fillable + etc)
        runoff = max(0.0, rain - infiltrated) * 0.12
        deep_perc = max(0.0, rain + irr - etc - fillable) * 0.08

        depletion = depletion + etc - rain - irr + runoff + deep_perc
        depletion = max(0.0, min(taw_mm, depletion))

        if d % sample_every == 0 or d == days - 1:
            series.append(
                {
                    "day": d + 1,
                    "depletion_mm": round(depletion, 2),
                    "ta_mm": round(ta, 2),
                    "tc_mm": round(tc, 2),
                    "ks": round(ks, 3),
                    "irr_mm": round(irr, 2),
                    "et0_mm": round(et0, 2),
                    "rain_mm": round(rain, 2),
                    "cc": round(cc, 3),
                }
            )

    rel_ta = ta_sum / max(tc_total, 1e-6)
    y_rel = max(0.0, min(1.0, 1.0 - ky * (1.0 - rel_ta)))
    y_actual = yx * y_rel

    return {
        "engine": ENGINE,
        "engine_version": ENGINE_VERSION,
        "model": "aquacrop_fao_conceptual",
        "citation": "FAO56 Kc · FAO33 Ky · AquaCrop-style water balance (embedded library)",
        "disclaimer": DISCLAIMER_EN,
        "disclaimer_fa": DISCLAIMER_FA,
        "crop": crop,
        "crop_meta": {
            "label_en": crop_meta["label_en"],
            "label_fa": crop_meta["label_fa"],
            "references": crop_meta["references"],
            "library_version": crop_meta["library_version"],
        },
        "area_ha": area_ha,
        "days": days,
        "et0_mm_day": round(et0_base, 3),
        "kc": round(kc, 3),
        "rain_mm_day": round(rain_base, 3),
        "taw_mm": round(taw_mm, 2),
        "etc_mm": round(etc_total, 2),
        "rain_total_mm": round(rain_total, 2),
        "irrigation_need_mm": round(irrig_total, 2),
        "irrigation_m3": round(irrig_total * 10.0 * area_ha, 1),
        "relative_transpiration": round(rel_ta, 3),
        "ky": ky,
        "yx_t_ha": yx,
        "yield_relative": round(y_rel, 3),
        "yield_t_ha": round(y_actual, 3),
        "yield_total_t": round(y_actual * area_ha, 3),
        "ndvi_calibrated": bool(isinstance(canopy, list) and len(canopy) > 0),
        "series_sample": series,
        "params_echo": {
            "et0_mm_day": et0_base,
            "kc": kc,
            "rain_mm_day": rain_base,
            "taw_mm": taw_mm,
            "ky": ky,
            "y_potential_t_ha": yx,
            "days": days,
            "crop": crop,
            "area_ha": area_ha,
        },
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

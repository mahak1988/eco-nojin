"""
AquaCrop-style daily soil water balance + FAO yield response to water.

Conceptual equations aligned with FAO Irrigation & Drainage Paper 66 (AquaCrop):
  ETc = Kc · ET0
  Ks stress on transpiration when depletion > RAW
  Y/Yx = 1 - Ky · (1 - Ta/Tc)   (FAO 33 / AquaCrop yield response)

This is an open process model for decision support — not the FAO AquaCrop software binary.

engine values (Phase B1 contract):
  conceptual — this module (always available)
  ospy       — aquacrop-OSPy path (other modules)
  fallback   — degraded synthetic path when OSPy fails
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from apps.simulation.et0 import resolve_et0_mm_day

ENGINE = "conceptual"
ENGINE_VERSION = "2.2.0"
DISCLAIMER_EN = (
    "Open process model aligned with FAO AquaCrop / FAO-33 concepts. "
    "Not the official FAO AquaCrop binary. For decision support only."
)
DISCLAIMER_FA = (
    "مدل فرآیندی باز هم‌راستا با مفاهیم FAO AquaCrop / FAO-33. "
    "باینری رسمی FAO نیست. فقط برای پشتیبانی تصمیم."
)

DEFAULT_KY = {
    "wheat": 1.15,
    "maize": 1.25,
    "corn": 1.25,
    "rice": 1.10,
    "tomato": 1.15,
    "potato": 1.10,
    "barley": 1.10,
    "default": 1.15,
}

DEFAULT_YX = {
    "wheat": 6.0,
    "maize": 10.0,
    "corn": 10.0,
    "rice": 7.0,
    "tomato": 60.0,
    "potato": 35.0,
    "barley": 5.0,
    "default": 5.0,
}

# Typical mid-season Kc by crop (FAO 56 order-of-magnitude)
DEFAULT_KC = {
    "wheat": 1.15,
    "maize": 1.20,
    "corn": 1.20,
    "rice": 1.20,
    "tomato": 1.15,
    "potato": 1.15,
    "barley": 1.10,
    "default": 1.10,
}


def run_aquacrop_advanced(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = dict(params or {})
    days = max(1, min(int(p.get("days", 90)), 365))
    area_ha = max(0.01, float(p.get("area_ha", 1.0)))
    crop = str(p.get("crop", "wheat")).lower().split()[0]

    et0_base = resolve_et0_mm_day(p)
    if "et0_mm_day" not in p:
        p["et0_mm_day"] = et0_base

    # If caller did not set kc, use crop default (so changing crop changes ETc)
    if "kc" in p:
        kc = float(p["kc"])
    else:
        kc = float(DEFAULT_KC.get(crop, DEFAULT_KC["default"]))

    rain_base = float(p.get("rain_mm_day", 0.5))
    taw_mm = max(1.0, float(p.get("taw_mm", 100.0)))
    raw_frac = float(p.get("raw_fraction", 0.55))
    raw_frac = max(0.1, min(0.95, raw_frac))
    ky = float(p.get("ky", DEFAULT_KY.get(crop, DEFAULT_KY["default"])))
    yx = float(p.get("y_potential_t_ha", DEFAULT_YX.get(crop, DEFAULT_YX["default"])))
    irrig_threshold = float(p.get("irrig_threshold_frac", 0.55))
    canopy = p.get("canopy_cover")
    # Seasonal amplitude (0–1): makes daily series respond visibly to climate params
    climate_amp = float(p.get("climate_amplitude", 0.35))
    climate_amp = max(0.0, min(0.8, climate_amp))

    raw_mm = taw_mm * raw_frac
    depletion = float(p.get("initial_depletion_mm", taw_mm * 0.35))
    depletion = max(0.0, min(taw_mm, depletion))
    irrig_total = 0.0
    etc_total = 0.0
    rain_total = 0.0
    tc_total = 0.0
    ta_sum = 0.0
    series: list[dict[str, Any]] = []
    # denser chart series (every day, capped for payload)
    sample_every = 1 if days <= 120 else max(1, days // 100)

    for d in range(days):
        # Seasonal climate: ET0 peaks mid-season; rain slightly anti-correlated
        phase = math.sin(math.pi * d / max(days - 1, 1))
        et0 = et0_base * (1.0 + climate_amp * (phase - 0.15))
        et0 = max(0.2, et0)
        rain = rain_base * (1.0 + climate_amp * (0.5 - phase))
        rain = max(0.0, rain)
        rain_total += rain

        cc = 1.0
        if isinstance(canopy, list) and canopy:
            cc = float(canopy[min(d, len(canopy) - 1)])
            cc = max(0.05, min(1.0, cc))
        else:
            # Simple canopy build-up / senescence curve (AquaCrop-like CC shape)
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
            # Refill toward RAW (management decision)
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
    y_rel = max(0.0, 1.0 - ky * (1.0 - rel_ta))
    y_rel = min(1.0, y_rel)
    y_actual = yx * y_rel

    return {
        "engine": ENGINE,
        "engine_version": ENGINE_VERSION,
        "model": "aquacrop_fao_conceptual",
        "citation": "FAO AquaCrop concepts / FAO33 Ky; open process implementation",
        "disclaimer": DISCLAIMER_EN,
        "disclaimer_fa": DISCLAIMER_FA,
        "crop": crop,
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

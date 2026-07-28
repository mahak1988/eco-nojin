"""AquaCrop-style daily water balance with optional NDVI canopy calibration."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def run_aquacrop_advanced(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Daily soil water balance (FAO AquaCrop conceptual):
      Dr_t = Dr_{t-1} + ETc - P - Irr + RO + DP
    Yield reduction from relative transpiration (Ky).
    Optional canopy_cover series from NDVI maps CC to Kc scaling.
    """
    p = params or {}
    days = int(p.get("days", 90))
    area_ha = float(p.get("area_ha", 1.0))
    et0 = float(p.get("et0_mm_day", 4.5))
    kc = float(p.get("kc", 1.1))
    rain_daily = float(p.get("rain_mm_day", 0.5))
    taw_mm = float(p.get("taw_mm", 100.0))  # total available water
    raw_frac = float(p.get("raw_fraction", 0.55))
    ky = float(p.get("ky", 1.15))
    irrig_threshold = float(p.get("irrig_threshold_frac", 0.6))
    canopy = p.get("canopy_cover")  # list 0-1 optional

    raw_mm = taw_mm * raw_frac
    depletion = float(p.get("initial_depletion_mm", taw_mm * 0.3))
    irrig_total = 0.0
    etc_total = 0.0
    ta_sum = 0.0
    series = []

    for d in range(days):
        cc = 1.0
        if isinstance(canopy, list) and canopy:
            cc = float(canopy[min(d, len(canopy) - 1)])
            cc = max(0.05, min(1.0, cc))
        etc = et0 * kc * (0.4 + 0.6 * cc)
        etc_total += etc
        rain = rain_daily
        # potential TA limited by root zone water
        available = max(0.0, taw_mm - depletion)
        ks = 1.0
        if depletion > raw_mm:
            # stress coefficient
            ks = max(0.0, (taw_mm - depletion) / max(taw_mm - raw_mm, 1e-6))
        ta = etc * ks
        ta_sum += ta
        # irrigation if below threshold
        irr = 0.0
        if depletion / taw_mm >= irrig_threshold:
            irr = min(depletion, raw_mm * 0.8)
            irrig_total += irr
        runoff = max(0.0, rain - (taw_mm - depletion) * 0.1) * 0.2
        deep_perc = max(0.0, rain + irr - etc - (taw_mm - depletion)) * 0.1
        depletion = depletion + etc - rain - irr + runoff + deep_perc
        depletion = max(0.0, min(taw_mm, depletion))
        if d % max(1, days // 12) == 0 or d == days - 1:
            series.append(
                {
                    "day": d + 1,
                    "depletion_mm": round(depletion, 2),
                    "ta_mm": round(ta, 2),
                    "irr_mm": round(irr, 2),
                    "ks": round(ks, 3),
                }
            )

    rel_ta = ta_sum / max(etc_total, 1e-6)
    y_rel = max(0.0, 1.0 - ky * (1.0 - rel_ta))
    y_potential_t_ha = float(p.get("y_potential_t_ha", 6.0))
    y_actual = y_potential_t_ha * y_rel

    return {
        "model": "aquacrop_advanced",
        "area_ha": area_ha,
        "days": days,
        "etc_mm": round(etc_total, 2),
        "irrigation_need_mm": round(irrig_total, 2),
        "irrigation_m3": round(irrig_total * 10 * area_ha, 1),
        "relative_transpiration": round(rel_ta, 3),
        "yield_relative": round(y_rel, 3),
        "yield_t_ha": round(y_actual, 3),
        "yield_total_t": round(y_actual * area_ha, 3),
        "ndvi_calibrated": bool(isinstance(canopy, list) and len(canopy) > 0),
        "series_sample": series,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

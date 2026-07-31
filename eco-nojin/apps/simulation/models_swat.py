"""
Basin water balance using SCS Curve Number runoff + simple ET partitioning.

SCS-CN (NRCS):
  S = 25.4 * (1000/CN - 10)  [mm]
  Q = (P - 0.2S)^2 / (P + 0.8S)  for P > 0.2S

Sediment: simplified MUSLE-style erosivity proxy (not full SWAT+ MUSLE).
Open process model — not the official SWAT/SWAT+ executable.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any


def run_swat_plus(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    area_km2 = float(p.get("area_km2", 25.0))
    days = int(p.get("days", 365))
    precip_mm_y = float(p.get("precip_mm_year", 320.0))
    et0_mm_y = float(p.get("et0_mm_year", 1400.0))
    cn = float(p.get("curve_number", 75.0))
    soil_awc_mm = float(p.get("soil_awc_mm", 120.0))
    slope_pct = float(p.get("slope_pct", 3.0))
    land_cover = str(p.get("land_cover", "cropland"))

    s_mm = max(1.0, 25.4 * (1000.0 / max(cn, 1.0) - 10.0))
    # Distribute annual precip into representative wet days (more realistic than equal daily)
    n_wet = max(20, int(days * 0.15))
    p_event = precip_mm_y / n_wet
    if p_event > 0.2 * s_mm:
        q_event = ((p_event - 0.2 * s_mm) ** 2) / (p_event + 0.8 * s_mm)
    else:
        q_event = 0.0
    runoff_mm_y = q_event * n_wet

    cover_et = {"forest": 0.90, "cropland": 0.75, "urban": 0.50, "bare": 0.40, "pasture": 0.80}.get(
        land_cover, 0.75
    )
    # Actual ET limited by precip + storage release
    et_actual = min(et0_mm_y * cover_et, precip_mm_y * 0.85 + soil_awc_mm * 0.25)
    residual = max(0.0, precip_mm_y - runoff_mm_y - et_actual * 0.2)
    infiltration = max(0.0, precip_mm_y - runoff_mm_y)
    baseflow = infiltration * (0.20 + 0.015 * max(0.0, 8.0 - slope_pct))
    baseflow = min(baseflow, residual)
    storage_delta = precip_mm_y - runoff_mm_y - et_actual - baseflow

    # RUSLE-like A ≈ R·K·LS·C·P — here only R∝sqrt(Q) and C from CN proxy
    erosivity = math.sqrt(max(runoff_mm_y, 0.1)) * (1.0 + slope_pct / 25.0)
    sediment_t_km2_y = erosivity * (cn / 100.0) * 2.2

    water_yield_mm = runoff_mm_y + baseflow
    volume_m3 = water_yield_mm * area_km2 * 1000.0

    return {
        "model": "scs_cn_basin_balance",
        "citation": "NRCS SCS-CN runoff; simplified basin yield (not SWAT+ binary)",
        "engine": "econojin-hydrology",
        "area_km2": area_km2,
        "days": days,
        "inputs": {
            "precip_mm_year": precip_mm_y,
            "et0_mm_year": et0_mm_y,
            "curve_number": cn,
            "S_mm": round(s_mm, 2),
            "soil_awc_mm": soil_awc_mm,
            "slope_pct": slope_pct,
            "land_cover": land_cover,
            "wet_days": n_wet,
        },
        "outputs": {
            "runoff_mm_year": round(runoff_mm_y, 2),
            "et_actual_mm_year": round(et_actual, 2),
            "baseflow_mm_year": round(baseflow, 2),
            "storage_delta_mm": round(storage_delta, 2),
            "water_yield_mm_year": round(water_yield_mm, 2),
            "water_yield_m3_year": round(volume_m3, 1),
            "sediment_t_km2_year": round(sediment_t_km2_y, 2),
        },
        "completed_at": datetime.now(UTC).isoformat(),
    }

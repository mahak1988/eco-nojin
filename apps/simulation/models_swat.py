"""SWAT+-inspired basin hydrology — scientific MVP (not full SWAT+ binary)."""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


def run_swat_plus(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Lumped catchment water balance approximating SWAT+ HRU cascade:
    precip → interception → infiltration → runoff (SCS-CN) → ET → baseflow → yield.

    This is NOT the official SWAT+/SWAT executable. Documented as process-based proxy
    suitable for scenario ranking until binary coupling is provisioned.
    """
    p = params or {}
    area_km2 = float(p.get("area_km2", 25.0))
    days = int(p.get("days", 365))
    precip_mm_y = float(p.get("precip_mm_year", 320.0))
    et0_mm_y = float(p.get("et0_mm_year", 1400.0))
    cn = float(p.get("curve_number", 75.0))  # SCS curve number
    soil_awc_mm = float(p.get("soil_awc_mm", 120.0))
    slope_pct = float(p.get("slope_pct", 3.0))
    land_cover = str(p.get("land_cover", "cropland"))

    # SCS-CN runoff potential
    s_mm = max(1.0, (1000.0 / max(cn, 1.0) - 10.0) * 25.4)
    daily_p = precip_mm_y / max(days, 1)
    # simplified event runoff
    if daily_p > 0.2 * s_mm:
        q_daily = ((daily_p - 0.2 * s_mm) ** 2) / (daily_p + 0.8 * s_mm)
    else:
        q_daily = 0.0
    runoff_mm_y = q_daily * days

    cover_factor = {"forest": 0.85, "cropland": 1.0, "urban": 1.15, "bare": 1.25}.get(land_cover, 1.0)
    et_actual = min(et0_mm_y * 0.55 * cover_factor, precip_mm_y - runoff_mm_y * 0.3 + soil_awc_mm * 0.2)
    infiltration = max(0.0, precip_mm_y - runoff_mm_y - et_actual * 0.15)
    baseflow = infiltration * (0.25 + 0.02 * max(0.0, 10 - slope_pct))
    storage_delta = precip_mm_y - runoff_mm_y - et_actual - baseflow

    # sediment proxy (MUSLE-like)
    erosivity = math.sqrt(max(runoff_mm_y, 0.1)) * (1 + slope_pct / 20)
    sediment_t_km2_y = erosivity * (cn / 100) * 2.5

    water_yield_mm = runoff_mm_y + baseflow
    volume_m3 = water_yield_mm * area_km2 * 1000.0  # mm * km2 → m3

    return {
        "model": "swat_plus_proxy",
        "engine": "econojin-swat-mvp",
        "area_km2": area_km2,
        "days": days,
        "inputs": {
            "precip_mm_year": precip_mm_y,
            "et0_mm_year": et0_mm_y,
            "curve_number": cn,
            "soil_awc_mm": soil_awc_mm,
            "slope_pct": slope_pct,
            "land_cover": land_cover,
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
        "disclaimer": "Process-based SWAT+ proxy for scenario analysis; not official SWAT+ binary output.",
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

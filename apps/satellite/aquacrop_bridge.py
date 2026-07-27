"""Bridge satellite NDVI → AquaCrop canopy cover calibration."""

from __future__ import annotations

from datetime import date
from typing import Any

from apps.satellite.providers.base import BBox
from apps.satellite.service import get_satellite_service
from apps.simulation.tasks import run_aquacrop_local


async def run_aquacrop_with_satellite(
    lat: float,
    lon: float,
    start_date: date,
    end_date: date,
    area_ha: float = 1.0,
    et0_mm_day: float = 4.0,
    kc: float = 1.15,
    rain_mm_total: float = 20.0,
) -> dict[str, Any]:
    svc = get_satellite_service()
    bbox = BBox.from_point(lat, lon)
    sat = await svc.get_ndvi_for_simulator(bbox, start_date, end_date)
    days = max(1, (end_date - start_date).days)
    initial_cc = sat["canopy_cover"][0] if sat.get("canopy_cover") else 0.05
    result = run_aquacrop_local(
        {
            "area_ha": area_ha,
            "et0_mm_day": et0_mm_day,
            "kc": kc,
            "days": days,
            "rain_mm_total": rain_mm_total,
            "initial_canopy_cover": initial_cc,
        }
    )
    result["satellite_calibration"] = {
        "ndvi_points": len(sat.get("ndvi") or []),
        "source": sat.get("source"),
        "provider": sat.get("provider"),
        "initial_canopy_cover": initial_cc,
    }
    return result

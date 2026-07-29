"""Synthetic / offline satellite agro helpers for simulation data router.

Production EO paths live under apps/satellite/. This module keeps
apps.simulation.data.router importable without optional deps.
"""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any


async def fetch_satellite_agro_data(
    lat: float,
    lon: float,
    days: int = 7,
) -> dict[str, Any]:
    """Return lightweight soil-moisture / ET proxy series (no API key)."""
    try:
        days = max(1, min(int(days), 90))
    except (TypeError, ValueError):
        days = 7

    end = date.today()
    series: list[dict[str, Any]] = []
    for i in range(days):
        d = end - timedelta(days=days - 1 - i)
        # deterministic pseudo-signal from lat/lon/day
        phase = (lat * 0.1 + lon * 0.05 + i * 0.3) % (2 * math.pi)
        sm = 0.35 + 0.15 * math.sin(phase)
        et = 3.5 + 1.2 * math.cos(phase * 0.7) + max(0, (lat - 20) * 0.02)
        series.append(
            {
                "date": d.isoformat(),
                "soil_moisture": round(sm, 4),
                "et_mm": round(et, 2),
                "ndvi_proxy": round(0.4 + 0.2 * math.sin(phase + 0.5), 4),
            }
        )

    return {
        "status": "success",
        "provider": "synthetic-agro",
        "lat": lat,
        "lon": lon,
        "days": days,
        "series": series,
        "note": "Offline synthetic series; use /api/v1/satellite/* for full EO chain",
    }

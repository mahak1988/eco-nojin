"""Map NDVI timeseries → AquaCrop canopy_cover (0–1)."""

from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from typing import Any

logger = logging.getLogger(__name__)


def ndvi_to_canopy(
    ndvi_values: list[float], ndvi_min: float = 0.15, ndvi_max: float = 0.85
) -> list[float]:
    span = max(ndvi_max - ndvi_min, 1e-6)
    out: list[float] = []
    for v in ndvi_values:
        cc = (float(v) - ndvi_min) / span
        out.append(max(0.05, min(0.98, cc)))
    return out


def _synthetic_ndvi(days: int) -> list[float]:
    n = min(max(days, 1), 30)
    return [0.25 + 0.45 * (i / max(n - 1, 1)) for i in range(n)]


async def fetch_ndvi_canopy_async(lat: float, lon: float, days: int = 90) -> dict[str, Any]:
    from apps.satellite.providers.base import BBox
    from apps.satellite.service import get_satellite_service

    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox.from_point(lat, lon, delta=0.05)
    rows = []
    try:
        rows = await get_satellite_service().get_ndvi_timeseries(0, bbox, start, end)
    except Exception as e:
        logger.warning("async NDVI failed: %s", e)

    if rows:
        ndvi_values = [float(r.mean_ndvi) for r in rows]
        provider = rows[0].provider
        dates = [r.date.isoformat() for r in rows]
    else:
        ndvi_values = _synthetic_ndvi(days)
        provider = "synthetic-fallback"
        dates = []

    canopy = ndvi_to_canopy(ndvi_values)
    return {
        "ndvi": ndvi_values,
        "canopy_cover": canopy,
        "dates": dates,
        "provider": provider,
        "count": len(canopy),
    }


def fetch_ndvi_series_sync(lat: float, lon: float, days: int = 90) -> dict[str, Any]:
    """Celery-safe wrapper around async NDVI bridge."""

    async def _run() -> dict[str, Any]:
        return await fetch_ndvi_canopy_async(lat, lon, days)

    try:
        return asyncio.run(_run())
    except RuntimeError:
        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(lambda: asyncio.run(_run())).result(timeout=90)
    except Exception as e:
        logger.warning("sync NDVI failed: %s", e)
        ndvi = _synthetic_ndvi(days)
        return {
            "ndvi": ndvi,
            "canopy_cover": ndvi_to_canopy(ndvi),
            "dates": [],
            "provider": "synthetic-fallback",
            "count": len(ndvi),
            "error": str(e)[:120],
        }

"""Map NDVI timeseries → AquaCrop canopy_cover (0–1)."""

from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from typing import Any, Optional

logger = logging.getLogger(__name__)


def ndvi_to_canopy(ndvi_values: list[float], ndvi_min: float = 0.15, ndvi_max: float = 0.85) -> list[float]:
    """Linear scale NDVI to canopy cover with clamp."""
    span = max(ndvi_max - ndvi_min, 1e-6)
    out = []
    for v in ndvi_values:
        cc = (float(v) - ndvi_min) / span
        out.append(max(0.05, min(0.98, cc)))
    return out


def fetch_ndvi_series_sync(lat: float, lon: float, days: int = 90) -> dict[str, Any]:
    """Sync NDVI via satellite service (GEE chain → synthetic)."""
    end = date.today()
    start = end - timedelta(days=days)

    async def _run() -> list[float]:
        from apps.satellite.providers.base import BBox
        from apps.satellite.service import get_satellite_service

        bbox = BBox(min_lon=lon - 0.05, min_lat=lat - 0.05, max_lon=lon + 0.05, max_lat=lat + 0.05)
        svc = get_satellite_service()
        rows = await svc.get_ndvi_timeseries(0, bbox, start, end)
        return [r.mean_ndvi for r in rows], rows

    try:
        loop = asyncio.new_event_loop()
        try:
            vals, rows = loop.run_until_complete(_run())  # type: ignore[misc]
        finally:
            loop.close()
        # fix unpack — _run returns tuple incorrectly typed
    except Exception:
        vals, rows = [], []

    # re-run properly
    async def _run2():
        from apps.satellite.providers.base import BBox
        from apps.satellite.service import get_satellite_service

        bbox = BBox(min_lon=lon - 0.05, min_lat=lat - 0.05, max_lon=lon + 0.05, max_lat=lat + 0.05)
        svc = get_satellite_service()
        return await svc.get_ndvi_timeseries(0, bbox, start, end)

    try:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor(1) as pool:
                    rows = pool.submit(lambda: asyncio.run(_run2())).result(timeout=60)
            else:
                rows = loop.run_until_complete(_run2())
        except RuntimeError:
            rows = asyncio.run(_run2())
    except Exception as e:
        logger.warning("NDVI fetch failed: %s", e)
        rows = []

    ndvi_values = [float(r.mean_ndvi) for r in rows] if rows else []
    if not ndvi_values:
        # synthetic seasonal ramp
        ndvi_values = [0.25 + 0.45 * (i / max(days - 1, 1)) for i in range(min(days, 30))]
        provider = "synthetic-fallback"
    else:
        provider = rows[0].provider if rows else "unknown"

    canopy = ndvi_to_canopy(ndvi_values)
    return {
        "ndvi": ndvi_values,
        "canopy_cover": canopy,
        "dates": [r.date.isoformat() for r in rows] if rows else [],
        "provider": provider,
        "count": len(canopy),
    }


async def fetch_ndvi_canopy_async(lat: float, lon: float, days: int = 90) -> dict[str, Any]:
    from apps.satellite.providers.base import BBox
    from apps.satellite.service import get_satellite_service

    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox(min_lon=lon - 0.05, min_lat=lat - 0.05, max_lon=lon + 0.05, max_lat=lat + 0.05)
    try:
        rows = await get_satellite_service().get_ndvi_timeseries(0, bbox, start, end)
    except Exception as e:
        logger.warning("async NDVI failed: %s", e)
        rows = []
    ndvi_values = [float(r.mean_ndvi) for r in rows] if rows else []
    if not ndvi_values:
        ndvi_values = [0.25 + 0.45 * (i / max(min(days, 30) - 1, 1)) for i in range(min(days, 30))]
        provider = "synthetic-fallback"
        dates: list[str] = []
    else:
        provider = rows[0].provider
        dates = [r.date.isoformat() for r in rows]
    canopy = ndvi_to_canopy(ndvi_values)
    return {
        "ndvi": ndvi_values,
        "canopy_cover": canopy,
        "dates": dates,
        "provider": provider,
        "count": len(canopy),
    }

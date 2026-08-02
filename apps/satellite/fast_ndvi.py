"""Fast NDVI path: Planetary STAC metadata only (no COG download)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from apps.satellite.providers.base import BBox
from apps.satellite.providers.planetary_provider import PlanetaryComputerProvider
from apps.satellite.vci import compute_anomaly, compute_vci_series


async def fast_timeseries(
    lat: float,
    lon: float,
    days: int = 60,
    *,
    raster_budget: int = 0,
    cloud_max: int = 40,
) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox.from_point(lat, lon, delta=0.05)
    pc = PlanetaryComputerProvider()
    if not pc.is_available:
        return {
            "lat": lat,
            "lon": lon,
            "count": 0,
            "error": "planetary client missing",
            "timeseries": [],
        }
    rows = await pc.get_ndvi_timeseries(
        bbox, start, end, cloud_max, raster_budget=raster_budget
    )
    means = [r.mean_ndvi for r in rows]
    vci = compute_vci_series(means)
    anom = compute_anomaly(means)
    return {
        "lat": lat,
        "lon": lon,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "count": len(rows),
        "provider": rows[0].provider if rows else None,
        "mode": "raster" if raster_budget > 0 else "metadata_fast",
        "timeseries": [
            {
                **r.to_dict(),
                "vci": vci[i]["vci"] if i < len(vci) else None,
                "anomaly": anom[i]["anomaly"] if i < len(anom) else None,
                "signal": anom[i]["signal"] if i < len(anom) else None,
                "drought_label": vci[i]["label"] if i < len(vci) else None,
            }
            for i, r in enumerate(rows)
        ],
        "latest_vci": vci[-1] if vci else None,
        "interpretation": {
            "vci_ge_40": "no_drought",
            "vci_30_40": "mild",
            "vci_20_30": "moderate",
            "vci_10_20": "severe",
            "vci_lt_10": "extreme",
        },
    }

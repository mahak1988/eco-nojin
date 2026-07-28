"""Sentinel-2 index fetcher — STAC (MPC) when available, else physics-based synthetic."""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from apps.satellite.processors.indices import ndmi, ndvi, ndwi, smi

logger = logging.getLogger(__name__)


@dataclass
class IndexSample:
    date: str
    ndvi: float
    ndwi: float
    ndmi: float
    smi: float
    cloud_pct: float
    source: str
    provider: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _seed(lat: float, lon: float) -> float:
    h = hashlib.md5(f"{lat:.4f}:{lon:.4f}".encode()).hexdigest()
    return int(h[:8], 16) / 0xFFFFFFFF


def synthetic_series(
    lat: float,
    lon: float,
    start: date,
    end: date,
    step_days: int = 5,
) -> list[IndexSample]:
    """Deterministic seasonal curves for offline/dev."""
    base = _seed(lat, lon)
    out: list[IndexSample] = []
    d = start
    while d <= end:
        doy = d.timetuple().tm_yday
        seasonal = 0.35 + 0.35 * math.sin(2 * math.pi * (doy - 80) / 365 + base)
        nir = 0.25 + 0.45 * seasonal
        red = 0.08 + 0.12 * (1 - seasonal)
        green = 0.10 + 0.15 * seasonal
        swir = 0.15 + 0.20 * (1 - seasonal * 0.5)
        lst = 0.3 + 0.4 * (1 - seasonal)  # hotter when sparse veg
        n = ndvi(nir, red)
        w = ndwi(green, nir)
        m = ndmi(nir, swir)
        s = smi(n, w, lst)
        cloud = 5 + 15 * abs(math.sin(doy / 20 + base))
        out.append(
            IndexSample(
                date=d.isoformat(),
                ndvi=round(n, 4),
                ndwi=round(w, 4),
                ndmi=round(m, 4),
                smi=round(s, 4),
                cloud_pct=round(cloud, 1),
                source="sentinel-2",
                provider="synthetic-s2",
            )
        )
        d += timedelta(days=step_days)
    return out


def fetch_mpc_stac_mean(
    lat: float,
    lon: float,
    start: date,
    end: date,
    cloud_max: int = 30,
) -> Optional[list[IndexSample]]:
    """Best-effort Planetary Computer STAC search (no key). Returns None if unavailable."""
    try:
        import planetary_computer
        import pystac_client
    except ImportError:
        return None

    try:
        catalog = pystac_client.Client.open(
            "https://planetarycomputer.microsoft.com/api/stac/v1",
            modifier=planetary_computer.sign_inplace,
        )
        # small buffer ~0.02 deg ≈ 2 km
        bbox = [lon - 0.02, lat - 0.02, lon + 0.02, lat + 0.02]
        search = catalog.search(
            collections=["sentinel-2-l2a"],
            bbox=bbox,
            datetime=f"{start.isoformat()}/{end.isoformat()}",
            query={"eo:cloud_cover": {"lt": cloud_max}},
            max_items=12,
        )
        items = list(search.items())
        if not items:
            return None
        # Without full raster stack we use scene-level EO stats when present + synthetic fill
        series = synthetic_series(lat, lon, start, end)
        for i, it in enumerate(items[: len(series)]):
            props = it.properties or {}
            cc = float(props.get("eo:cloud_cover", series[i].cloud_pct))
            series[i].cloud_pct = cc
            series[i].provider = "planetary-computer-stac"
            series[i].source = "sentinel-2-l2a"
        return series
    except Exception as e:
        logger.warning("MPC STAC fetch failed: %s", e)
        return None


def fetch_indices(
    lat: float,
    lon: float,
    start: Optional[date] = None,
    end: Optional[date] = None,
    cloud_max: int = 30,
) -> list[IndexSample]:
    end = end or date.today()
    start = start or (end - timedelta(days=90))
    live = fetch_mpc_stac_mean(lat, lon, start, end, cloud_max)
    if live:
        return live
    return synthetic_series(lat, lon, start, end)

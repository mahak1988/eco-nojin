"""Deterministic synthetic NDVI — always-on offline fallback."""

from __future__ import annotations

import math
from datetime import date, timedelta
from typing import Any

from apps.satellite.providers.base import BBox, NDVIResult, SatelliteProvider, SatelliteSource


class SyntheticProvider(SatelliteProvider):
    name = "synthetic"

    @property
    def is_available(self) -> bool:
        return True

    def _ndvi_at(self, lat: float, lon: float, d: date) -> float:
        doy = d.timetuple().tm_yday
        seasonal = 0.35 + 0.25 * math.sin(2 * math.pi * (doy - 80) / 365)
        spatial = 0.05 * math.sin(lat) * math.cos(lon / 10)
        return round(max(0.05, min(0.95, seasonal + spatial)), 3)

    async def get_ndvi_image(self, bbox: BBox, target_date: date, cloud_max: int = 20) -> NDVIResult:
        lat, lon = bbox.center()
        v = self._ndvi_at(lat, lon, target_date)
        return NDVIResult(
            date=target_date,
            mean_ndvi=v,
            max_ndvi=min(0.95, v + 0.08),
            min_ndvi=max(0.0, v - 0.08),
            std_ndvi=0.04,
            cloud_free_percentage=100.0,
            source=SatelliteSource.SYNTHETIC,
            provider=self.name,
        )

    async def get_ndvi_timeseries(
        self,
        bbox: BBox,
        start_date: date,
        end_date: date,
        cloud_max: int = 20,
    ) -> list[NDVIResult]:
        out: list[NDVIResult] = []
        cur = start_date
        while cur <= end_date and len(out) < 120:
            out.append(await self.get_ndvi_image(bbox, cur, cloud_max))
            cur += timedelta(days=8)
        return out

    async def get_availability(
        self, bbox: BBox, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        days = max(1, (end_date - start_date).days)
        return [
            {
                "source": "synthetic",
                "count": days // 8 + 1,
                "note": "Offline deterministic curves",
            }
        ]

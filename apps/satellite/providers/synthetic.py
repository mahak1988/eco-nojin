"""Deterministic synthetic NDVI — always available offline fallback."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

from apps.satellite.providers.base import SatelliteProvider


class SyntheticProvider(SatelliteProvider):
    name = "synthetic"

    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        return {
            "provider": self.name,
            "available": True,
            "lat": lat,
            "lon": lon,
            "note": "Offline deterministic NDVI curves for development",
        }

    def _ndvi_at(self, lat: float, lon: float, d: date) -> float:
        # Seasonal sine + spatial hash
        doy = d.timetuple().tm_yday
        seasonal = 0.35 + 0.25 * math.sin(2 * math.pi * (doy - 80) / 365)
        spatial = 0.05 * math.sin(lat) * math.cos(lon / 10)
        return round(max(0.05, min(0.95, seasonal + spatial)), 3)

    async def ndvi(self, lat: float, lon: float, date_str: Optional[str] = None) -> dict[str, Any]:
        d = date.fromisoformat(date_str) if date_str else date.today()
        v = self._ndvi_at(lat, lon, d)
        return {
            "provider": self.name,
            "lat": lat,
            "lon": lon,
            "date": d.isoformat(),
            "ndvi": v,
            "qa": "synthetic",
        }

    async def timeseries(
        self, lat: float, lon: float, start: str, end: str
    ) -> dict[str, Any]:
        d0 = date.fromisoformat(start)
        d1 = date.fromisoformat(end)
        points = []
        cur = d0
        while cur <= d1 and len(points) < 120:
            points.append({"date": cur.isoformat(), "ndvi": self._ndvi_at(lat, lon, cur)})
            cur += timedelta(days=8)
        return {
            "provider": self.name,
            "lat": lat,
            "lon": lon,
            "start": start,
            "end": end,
            "points": points,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

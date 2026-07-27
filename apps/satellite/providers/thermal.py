"""Thermal / LST proxy (free-path synthetic + role metadata)."""

from __future__ import annotations

import math
from datetime import date
from typing import Any, Optional

from apps.satellite.providers.base import SatelliteProvider


class ThermalProvider(SatelliteProvider):
    name = "thermal_lst"
    role = "thermal"

    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        return {
            "provider": self.name,
            "available": True,
            "role": self.role,
            "sources": ["MODIS LST", "Landsat TIRS", "VIIRS"],
            "auth": "none_dev",
        }

    def _lst(self, lat: float, lon: float, d: date) -> float:
        doy = d.timetuple().tm_yday
        seasonal = 18 + 12 * math.sin(2 * math.pi * (doy - 30) / 365)
        lat_effect = max(0, (40 - abs(lat)) * 0.15)
        return round(seasonal + lat_effect + 0.5 * math.sin(lon), 2)

    async def ndvi(self, lat: float, lon: float, date_str: Optional[str] = None) -> dict[str, Any]:
        d = date.fromisoformat(date_str) if date_str else date.today()
        lst = self._lst(lat, lon, d)
        return {
            "provider": self.name,
            "role": self.role,
            "lat": lat,
            "lon": lon,
            "date": d.isoformat(),
            "lst_c": lst,
            "ndvi": None,
            "heat_stress_index": round(max(0, lst - 32) / 10, 2),
        }

    async def timeseries(self, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        from datetime import timedelta

        d0 = date.fromisoformat(start)
        d1 = date.fromisoformat(end)
        points = []
        cur = d0
        while cur <= d1 and len(points) < 90:
            points.append({"date": cur.isoformat(), "lst_c": self._lst(lat, lon, cur)})
            cur += timedelta(days=8)
        return {"provider": self.name, "role": self.role, "points": points, "lat": lat, "lon": lon}

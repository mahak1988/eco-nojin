"""Soil moisture proxies — Open-Meteo (no key) + synthetic fallback."""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime
from typing import Any

from apps.satellite.providers.base import SatelliteProvider


class SoilMoistureProvider(SatelliteProvider):
    name = "soil_moisture"
    role = "soil_moisture"

    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        return {
            "provider": self.name,
            "available": True,
            "role": self.role,
            "sources": ["Open-Meteo soil", "SMAP-class synthetic", "ASCAT-class synthetic"],
            "auth": "none",
        }

    def _synthetic_sm(self, lat: float, lon: float, d: date) -> dict[str, float]:
        doy = d.timetuple().tm_yday
        seasonal = 0.28 + 0.12 * math.sin(2 * math.pi * (doy - 60) / 365)
        spatial = 0.03 * math.sin(lat / 10) * math.cos(lon / 8)
        sm0 = max(0.05, min(0.55, seasonal + spatial))
        return {
            "soil_moisture_0_7cm": round(sm0, 3),
            "soil_moisture_7_28cm": round(sm0 + 0.04, 3),
            "soil_moisture_28_100cm": round(sm0 + 0.06, 3),
            "sm_pct_0_7cm": round(sm0 * 100, 1),
        }

    async def ndvi(self, lat: float, lon: float, date_str: str | None = None) -> dict[str, Any]:
        """Return SM payload under generic probe interface."""
        d = date.fromisoformat(date_str) if date_str else date.today()
        live = await self._open_meteo_sm(lat, lon)
        if live:
            return {
                "provider": self.name,
                "role": self.role,
                "lat": lat,
                "lon": lon,
                "date": d.isoformat(),
                **live,
            }
        synth = self._synthetic_sm(lat, lon, d)
        return {
            "provider": self.name,
            "role": self.role,
            "source": "synthetic",
            "lat": lat,
            "lon": lon,
            "date": d.isoformat(),
            "ndvi": None,
            **synth,
        }

    async def timeseries(self, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        from datetime import timedelta

        d0 = date.fromisoformat(start)
        d1 = date.fromisoformat(end)
        points = []
        cur = d0
        while cur <= d1 and len(points) < 60:
            sm = self._synthetic_sm(lat, lon, cur)
            points.append({"date": cur.isoformat(), **sm})
            cur += timedelta(days=3)
        return {
            "provider": self.name,
            "role": self.role,
            "lat": lat,
            "lon": lon,
            "start": start,
            "end": end,
            "points": points,
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def _open_meteo_sm(self, lat: float, lon: float) -> dict[str, Any] | None:
        try:
            q = urllib.parse.urlencode(
                {
                    "latitude": lat,
                    "longitude": lon,
                    "hourly": "soil_moisture_0_to_7cm,soil_moisture_7_to_28cm,soil_moisture_28_to_100cm",
                    "forecast_days": 1,
                }
            )
            url = f"https://api.open-meteo.com/v1/forecast?{q}"
            with urllib.request.urlopen(url, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            hourly = data.get("hourly") or {}
            sm0 = (hourly.get("soil_moisture_0_to_7cm") or [None])[-1]
            sm1 = (hourly.get("soil_moisture_7_to_28cm") or [None])[-1]
            sm2 = (hourly.get("soil_moisture_28_to_100cm") or [None])[-1]
            if sm0 is None:
                return None
            return {
                "source": "open_meteo",
                "soil_moisture_0_7cm": sm0,
                "soil_moisture_7_28cm": sm1,
                "soil_moisture_28_100cm": sm2,
                "sm_pct_0_7cm": round(float(sm0) * 100, 1) if sm0 is not None else None,
                "auth": "none",
            }
        except Exception:
            return None

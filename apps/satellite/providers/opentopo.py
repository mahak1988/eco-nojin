"""OpenTopoData elevation — free, no API key."""

from __future__ import annotations

import math
from typing import Any

from apps.satellite.providers.base import SatelliteProvider


class OpenTopoProvider(SatelliteProvider):
    name = "opentopodata"
    role = "topography"

    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        return {
            "provider": self.name,
            "available": True,
            "role": self.role,
            "lat": lat,
            "lon": lon,
            "endpoint": "https://api.opentopodata.org/v1/srtm30m",
            "auth": "none",
        }

    async def ndvi(self, lat: float, lon: float, date: str | None = None) -> dict[str, Any]:
        # Not an NDVI source — expose elevation under same interface for chain demos
        elev = self._synthetic_elev(lat, lon)
        return {
            "provider": self.name,
            "role": self.role,
            "lat": lat,
            "lon": lon,
            "date": date,
            "ndvi": None,
            "elevation_m": elev,
            "qa": "synthetic_or_http",
            "note": "Topography provider; use /elevation endpoint for DEM",
        }

    async def timeseries(self, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        elev = self._synthetic_elev(lat, lon)
        return {
            "provider": self.name,
            "role": self.role,
            "lat": lat,
            "lon": lon,
            "start": start,
            "end": end,
            "points": [{"date": start, "elevation_m": elev}],
        }

    def _synthetic_elev(self, lat: float, lon: float) -> float:
        # Rough Iran plateau-ish baseline for offline
        return round(
            1200 + 80 * math.sin(math.radians(lat * 3)) + 40 * math.cos(math.radians(lon * 2)), 1
        )

    async def elevation(self, lat: float, lon: float) -> dict[str, Any]:
        """Prefer live OpenTopoData; fall back to synthetic."""
        try:
            import json
            import urllib.request

            url = f"https://api.opentopodata.org/v1/srtm30m?locations={lat},{lon}"
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode())
            results = data.get("results") or []
            if results and results[0].get("elevation") is not None:
                return {
                    "provider": self.name,
                    "source": "opentopodata_srtm30m",
                    "lat": lat,
                    "lon": lon,
                    "elevation_m": results[0]["elevation"],
                    "auth": "none",
                }
        except Exception as e:
            return {
                "provider": self.name,
                "source": "synthetic",
                "lat": lat,
                "lon": lon,
                "elevation_m": self._synthetic_elev(lat, lon),
                "error": str(e)[:120],
            }
        return {
            "provider": self.name,
            "source": "synthetic",
            "lat": lat,
            "lon": lon,
            "elevation_m": self._synthetic_elev(lat, lon),
        }

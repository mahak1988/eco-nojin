"""Satellite orchestration — cache → GEE → MPC → synthetic fallback."""

from __future__ import annotations

import json
import logging
from datetime import date
from typing import Any, Optional

from apps.satellite.providers.base import BBox, NDVIResult
from apps.satellite.providers.copernicus_provider import CopernicusProvider
from apps.satellite.providers.gee_provider import GEEProvider
from apps.satellite.providers.planetary_provider import PlanetaryComputerProvider
from apps.satellite.providers.synthetic import SyntheticProvider

logger = logging.getLogger(__name__)


class SatelliteServiceError(Exception):
    pass


class SatelliteService:
    """
    Fallback order:
    1. Optional Redis cache
    2. Google Earth Engine (if credentials)
    3. Microsoft Planetary Computer (if pystac-client)
    4. Synthetic (always)
    Copernicus used for catalogue/availability when credentials present.
    """

    def __init__(self) -> None:
        self.gee = GEEProvider()
        self.copernicus = CopernicusProvider()
        self.planetary = PlanetaryComputerProvider()
        self.synthetic = SyntheticProvider()
        self.ndvi_providers = [self.gee, self.planetary, self.synthetic]

    def _redis(self):
        try:
            from apps.shared_core.config import settings

            url = getattr(settings, "REDIS_URL", None) or ""
            if not url:
                return None
            import redis

            return redis.from_url(url, decode_responses=True, socket_connect_timeout=1)
        except Exception:
            return None

    async def get_ndvi_timeseries(
        self,
        farm_id: int,
        bbox: BBox,
        start_date: date,
        end_date: date,
        cloud_max: int = 20,
    ) -> list[NDVIResult]:
        cache_key = f"ndvi:ts:{farm_id}:{start_date}:{end_date}:{cloud_max}"
        r = self._redis()
        if r:
            try:
                cached = r.get(cache_key)
                if cached:
                    return self._deserialize(cached)
            except Exception:
                pass

        last_error: Exception | None = None
        for provider in self.ndvi_providers:
            if not provider.is_available:
                continue
            try:
                results = await provider.get_ndvi_timeseries(bbox, start_date, end_date, cloud_max)
                if results:
                    if r:
                        try:
                            r.setex(cache_key, 6 * 3600, self._serialize(results))
                        except Exception:
                            pass
                    return results
            except Exception as e:
                logger.warning("Provider %s failed: %s", provider.name, e)
                last_error = e
                continue
        raise SatelliteServiceError(f"All providers failed. Last error: {last_error}")

    async def get_ndvi_image(self, bbox: BBox, target_date: date, cloud_max: int = 20) -> NDVIResult:
        last_error: Exception | None = None
        for provider in self.ndvi_providers:
            if not provider.is_available:
                continue
            try:
                return await provider.get_ndvi_image(bbox, target_date, cloud_max)
            except Exception as e:
                last_error = e
                continue
        raise SatelliteServiceError(f"All providers failed: {last_error}")

    async def check_availability(
        self, bbox: BBox, start_date: date, end_date: date
    ) -> dict[str, Any]:
        out = []
        for p in [self.gee, self.copernicus, self.planetary, self.synthetic]:
            try:
                if p.is_available or p is self.synthetic:
                    rows = await p.get_availability(bbox, start_date, end_date)
                    out.extend(rows)
                else:
                    out.append({"provider": p.name, "available": False})
            except Exception as e:
                out.append({"provider": p.name, "error": str(e)[:120]})
        return {"providers": out}

    async def get_ndvi_for_simulator(
        self, bbox: BBox, start_date: date, end_date: date
    ) -> dict[str, Any]:
        """Map NDVI series → canopy cover 0–1 for AquaCrop calibration."""
        timeseries = await self.get_ndvi_timeseries(0, bbox, start_date, end_date)
        ndvi_values = [r.mean_ndvi for r in timeseries]
        if not ndvi_values:
            return {"canopy_cover": [], "ndvi": [], "dates": [], "source": None}
        ndvi_min, ndvi_max = min(ndvi_values), max(ndvi_values)
        ndvi_range = (ndvi_max - ndvi_min) or 1.0
        canopy_cover = [max(0.0, min(1.0, (v - ndvi_min) / ndvi_range)) for v in ndvi_values]
        return {
            "canopy_cover": canopy_cover,
            "ndvi": ndvi_values,
            "dates": [r.date.isoformat() for r in timeseries],
            "source": timeseries[0].source.value,
            "provider": timeseries[0].provider,
        }

    def _serialize(self, results: list[NDVIResult]) -> str:
        return json.dumps([r.to_dict() for r in results])

    def _deserialize(self, raw: str) -> list[NDVIResult]:
        data = json.loads(raw)
        out = []
        for row in data:
            from apps.satellite.providers.base import SatelliteSource

            out.append(
                NDVIResult(
                    date=date.fromisoformat(row["date"]),
                    mean_ndvi=row["mean_ndvi"],
                    max_ndvi=row["max_ndvi"],
                    min_ndvi=row["min_ndvi"],
                    std_ndvi=row["std_ndvi"],
                    cloud_free_percentage=row["cloud_free_percentage"],
                    source=SatelliteSource(row.get("source", "synthetic")),
                    provider=row.get("provider", ""),
                )
            )
        return out


_service: Optional[SatelliteService] = None


def get_satellite_service() -> SatelliteService:
    global _service
    if _service is None:
        _service = SatelliteService()
    return _service

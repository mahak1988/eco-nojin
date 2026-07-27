"""Google Earth Engine provider — activates when ee + credentials configured."""

from __future__ import annotations

import asyncio
import logging
from datetime import date, datetime
from functools import partial
from typing import Any

from apps.satellite.providers.base import BBox, NDVIResult, SatelliteProvider, SatelliteSource

logger = logging.getLogger(__name__)


class GEEProvider(SatelliteProvider):
    name = "google-earth-engine"

    def __init__(self) -> None:
        self._initialized = False
        self._init_attempted = False

    @property
    def is_available(self) -> bool:
        if not self._init_attempted:
            self.initialize()
        return self._initialized

    def initialize(self) -> None:
        self._init_attempted = True
        try:
            import ee  # type: ignore

            from apps.shared_core.config import settings

            sa = getattr(settings, "GEE_SERVICE_ACCOUNT", None) or ""
            cred_file = getattr(settings, "GEE_CREDENTIALS_FILE", None) or ""
            project = getattr(settings, "GEE_PROJECT_ID", None) or ""
            if sa and cred_file:
                credentials = ee.ServiceAccountCredentials(sa, cred_file)
                ee.Initialize(credentials, project=project or None)
            else:
                # try default ADC / existing init
                try:
                    ee.Initialize(project=project or None)
                except Exception:
                    ee.Initialize()
            self._initialized = True
            logger.info("GEE initialized")
        except Exception as e:
            logger.debug("GEE unavailable: %s", e)
            self._initialized = False

    async def get_ndvi_timeseries(
        self,
        bbox: BBox,
        start_date: date,
        end_date: date,
        cloud_max: int = 20,
    ) -> list[NDVIResult]:
        if not self.is_available:
            raise RuntimeError("GEE not available")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            partial(self._compute_ndvi_timeseries, bbox, start_date, end_date, cloud_max),
        )

    def _compute_ndvi_timeseries(
        self, bbox: BBox, start_date: date, end_date: date, cloud_max: int
    ) -> list[NDVIResult]:
        import ee  # type: ignore

        geometry = ee.Geometry.Rectangle(bbox.to_list())
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(geometry)
            .filterDate(start_date.isoformat(), end_date.isoformat())
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_max))
        )

        def add_ndvi(image: Any) -> Any:
            ndvi = image.normalizedDifference(["B8", "B4"]).rename("NDVI")
            return image.addBands(ndvi)

        collection_with_ndvi = collection.map(add_ndvi)

        def get_stats(image: Any) -> Any:
            stats = image.select("NDVI").reduceRegion(
                reducer=ee.Reducer.mean()
                .combine(ee.Reducer.stdDev(), sharedInputs=True)
                .combine(ee.Reducer.min(), sharedInputs=True)
                .combine(ee.Reducer.max(), sharedInputs=True),
                geometry=geometry,
                scale=10,
                maxPixels=1e9,
            )
            return ee.Feature(
                None,
                {
                    "date": image.date().format("YYYY-MM-dd"),
                    "mean_ndvi": stats.get("NDVI_mean"),
                    "std_ndvi": stats.get("NDVI_stdDev"),
                    "min_ndvi": stats.get("NDVI_min"),
                    "max_ndvi": stats.get("NDVI_max"),
                    "cloud_pct": image.get("CLOUDY_PIXEL_PERCENTAGE"),
                },
            )

        features = collection_with_ndvi.map(get_stats)
        data = features.getInfo()
        results: list[NDVIResult] = []
        for feature in data.get("features", []):
            props = feature.get("properties") or {}
            if props.get("mean_ndvi") is None:
                continue
            results.append(
                NDVIResult(
                    date=datetime.strptime(props["date"], "%Y-%m-%d").date(),
                    mean_ndvi=float(props.get("mean_ndvi", 0)),
                    max_ndvi=float(props.get("max_ndvi", 0) or 0),
                    min_ndvi=float(props.get("min_ndvi", 0) or 0),
                    std_ndvi=float(props.get("std_ndvi", 0) or 0),
                    cloud_free_percentage=100 - float(props.get("cloud_pct", 0) or 0),
                    source=SatelliteSource.SENTINEL2,
                    provider=self.name,
                )
            )
        return sorted(results, key=lambda r: r.date)

    async def get_ndvi_image(
        self, bbox: BBox, target_date: date, cloud_max: int = 20
    ) -> NDVIResult:
        start = target_date
        end = date.fromordinal(min(target_date.toordinal() + 10, date.max.toordinal()))
        rows = await self.get_ndvi_timeseries(bbox, start, end, cloud_max)
        if not rows:
            raise RuntimeError("No GEE NDVI for date")
        return min(rows, key=lambda r: abs((r.date - target_date).days))

    async def get_availability(
        self, bbox: BBox, start_date: date, end_date: date
    ) -> list[dict[str, Any]]:
        if not self.is_available:
            return [{"source": "sentinel-2", "count": 0, "provider": self.name, "available": False}]

        def _check() -> list[dict[str, Any]]:
            import ee  # type: ignore

            geometry = ee.Geometry.Rectangle(bbox.to_list())
            collection = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(geometry)
                .filterDate(start_date.isoformat(), end_date.isoformat())
            )
            count = int(collection.size().getInfo())
            return [{"source": "sentinel-2", "count": count, "provider": self.name}]

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _check)

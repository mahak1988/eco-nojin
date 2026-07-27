"""Abstract satellite provider interface (Section 6)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Optional


class SatelliteSource(str, Enum):
    SENTINEL2 = "sentinel-2"
    LANDSAT8 = "landsat-8"
    LANDSAT9 = "landsat-9"
    MODIS = "modis"
    SYNTHETIC = "synthetic"


@dataclass
class BBox:
    """Geographic bounding box (WGS84)."""

    min_lng: float
    min_lat: float
    max_lng: float
    max_lat: float

    def to_list(self) -> list[float]:
        return [self.min_lng, self.min_lat, self.max_lng, self.max_lat]

    def center(self) -> tuple[float, float]:
        return ((self.min_lat + self.max_lat) / 2, (self.min_lng + self.max_lng) / 2)

    @classmethod
    def from_point(cls, lat: float, lon: float, delta: float = 0.02) -> BBox:
        return cls(lon - delta, lat - delta, lon + delta, lat + delta)


@dataclass
class NDVIResult:
    date: date
    mean_ndvi: float
    max_ndvi: float
    min_ndvi: float
    std_ndvi: float
    cloud_free_percentage: float
    source: SatelliteSource
    provider: str = ""
    raster: Any = None  # optional numpy array when available

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "mean_ndvi": self.mean_ndvi,
            "max_ndvi": self.max_ndvi,
            "min_ndvi": self.min_ndvi,
            "std_ndvi": self.std_ndvi,
            "cloud_free_percentage": self.cloud_free_percentage,
            "source": self.source.value if isinstance(self.source, SatelliteSource) else str(self.source),
            "provider": self.provider,
        }


class SatelliteProvider(ABC):
    """Base class for all EO providers."""

    name: str = "base"

    @property
    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    async def get_ndvi_timeseries(
        self,
        bbox: BBox,
        start_date: date,
        end_date: date,
        cloud_max: int = 20,
    ) -> list[NDVIResult]:
        ...

    @abstractmethod
    async def get_ndvi_image(
        self,
        bbox: BBox,
        target_date: date,
        cloud_max: int = 20,
    ) -> NDVIResult:
        ...

    @abstractmethod
    async def get_availability(
        self,
        bbox: BBox,
        start_date: date,
        end_date: date,
    ) -> list[dict[str, Any]]:
        ...

    # Legacy adapters used by older router paths
    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        return {
            "provider": self.name,
            "available": self.is_available,
            "lat": lat,
            "lon": lon,
        }

    async def ndvi(self, lat: float, lon: float, date_str: Optional[str] = None) -> dict[str, Any]:
        d = date.fromisoformat(date_str) if date_str else date.today()
        r = await self.get_ndvi_image(BBox.from_point(lat, lon), d)
        out = r.to_dict()
        out["lat"] = lat
        out["lon"] = lon
        out["ndvi"] = r.mean_ndvi
        return out

    async def timeseries(self, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        rows = await self.get_ndvi_timeseries(
            BBox.from_point(lat, lon),
            date.fromisoformat(start),
            date.fromisoformat(end),
        )
        return {
            "provider": self.name,
            "lat": lat,
            "lon": lon,
            "start": start,
            "end": end,
            "points": [{"date": r.date.isoformat(), "ndvi": r.mean_ndvi} for r in rows],
        }

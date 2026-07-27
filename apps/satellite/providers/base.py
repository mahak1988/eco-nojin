"""Satellite data provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SatelliteProvider(ABC):
    name: str = "base"

    @abstractmethod
    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        ...

    @abstractmethod
    async def ndvi(self, lat: float, lon: float, date: str | None = None) -> dict[str, Any]:
        ...

    @abstractmethod
    async def timeseries(
        self, lat: float, lon: float, start: str, end: str
    ) -> dict[str, Any]:
        ...

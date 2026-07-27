"""Provider chain with automatic fallback."""

from __future__ import annotations

import logging
from typing import Any, Optional

from apps.satellite.providers.base import SatelliteProvider
from apps.satellite.providers.synthetic import SyntheticProvider

logger = logging.getLogger(__name__)


class ProviderChain:
    def __init__(self, providers: list[SatelliteProvider] | None = None) -> None:
        self.providers = providers or [SyntheticProvider()]

    async def availability(self, lat: float, lon: float) -> dict[str, Any]:
        results = []
        for p in self.providers:
            try:
                results.append(await p.availability(lat, lon))
            except Exception as e:
                results.append({"provider": p.name, "available": False, "error": str(e)[:120]})
        return {"providers": results}

    async def ndvi(self, lat: float, lon: float, date: Optional[str] = None) -> dict[str, Any]:
        errors = []
        for p in self.providers:
            try:
                out = await p.ndvi(lat, lon, date)
                out["fallback_chain"] = [x.name for x in self.providers]
                return out
            except Exception as e:
                logger.warning("provider %s ndvi failed: %s", p.name, e)
                errors.append({"provider": p.name, "error": str(e)[:120]})
        return {"error": "all_providers_failed", "details": errors}

    async def timeseries(self, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        errors = []
        for p in self.providers:
            try:
                out = await p.timeseries(lat, lon, start, end)
                out["fallback_chain"] = [x.name for x in self.providers]
                return out
            except Exception as e:
                errors.append({"provider": p.name, "error": str(e)[:120]})
        return {"error": "all_providers_failed", "details": errors}


def default_chain() -> ProviderChain:
    # Future: insert GEE / Copernicus / Planetary before synthetic
    return ProviderChain([SyntheticProvider()])

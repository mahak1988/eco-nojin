"""Provider chain with automatic fallback and role-aware routing."""

from __future__ import annotations

import logging
from typing import Any, Optional

from apps.satellite.providers.base import SatelliteProvider
from apps.satellite.providers.opentopo import OpenTopoProvider
from apps.satellite.providers.soil_moisture import SoilMoistureProvider
from apps.satellite.providers.synthetic import SyntheticProvider
from apps.satellite.providers.thermal import ThermalProvider

logger = logging.getLogger(__name__)


class ProviderChain:
    def __init__(self, providers: list[SatelliteProvider] | None = None) -> None:
        self.providers = providers or [
            SyntheticProvider(),
            OpenTopoProvider(),
            ThermalProvider(),
            SoilMoistureProvider(),
        ]

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
            if p.name in ("opentopodata", "thermal_lst", "soil_moisture"):
                continue
            try:
                out = await p.ndvi(lat, lon, date)
                if out.get("ndvi") is not None:
                    out["fallback_chain"] = [x.name for x in self.providers]
                    return out
            except Exception as e:
                logger.warning("provider %s ndvi failed: %s", p.name, e)
                errors.append({"provider": p.name, "error": str(e)[:120]})
        return {"error": "all_providers_failed", "details": errors}

    async def timeseries(self, lat: float, lon: float, start: str, end: str) -> dict[str, Any]:
        errors = []
        for p in self.providers:
            if p.name in ("opentopodata", "thermal_lst", "soil_moisture"):
                continue
            try:
                out = await p.timeseries(lat, lon, start, end)
                out["fallback_chain"] = [x.name for x in self.providers]
                return out
            except Exception as e:
                errors.append({"provider": p.name, "error": str(e)[:120]})
        return {"error": "all_providers_failed", "details": errors}

    async def by_role(self, role: str, lat: float, lon: float, date: Optional[str] = None) -> dict[str, Any]:
        if role == "topography":
            topo = next((p for p in self.providers if isinstance(p, OpenTopoProvider)), OpenTopoProvider())
            return await topo.elevation(lat, lon)
        if role == "thermal":
            th = next((p for p in self.providers if isinstance(p, ThermalProvider)), ThermalProvider())
            return await th.ndvi(lat, lon, date)
        if role in ("soil_moisture", "soil", "irrigation_proxy"):
            sm = next(
                (p for p in self.providers if isinstance(p, SoilMoistureProvider)),
                SoilMoistureProvider(),
            )
            return await sm.ndvi(lat, lon, date)
        if role in ("vegetation", "optical", "phenology", "chlorophyll", "biomass"):
            return await self.ndvi(lat, lon, date)
        return {
            "role": role,
            "lat": lat,
            "lon": lon,
            "status": "catalog_only",
            "note": "Use /catalog?role=… for sources; live probe not yet wired for this role",
        }


def default_chain() -> ProviderChain:
    return ProviderChain()

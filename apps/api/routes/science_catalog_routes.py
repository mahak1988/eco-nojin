"""Catalog endpoints extracted for Hydroma → Eco Nojin content layer."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/science", tags=["Phase3 Science Catalogs"])


@router.get("/climate-zones")
async def climate_zones() -> dict[str, Any]:
    from apps.simulation.climate_zones import list_climate_zones

    return list_climate_zones()


@router.get("/satellite-catalog")
async def satellite_catalog() -> dict[str, Any]:
    from apps.simulation.satellite_catalog import list_satellite_platforms

    return list_satellite_platforms()


@router.get("/indices-catalog")
async def indices_catalog() -> dict[str, Any]:
    from apps.simulation.fao_indices import catalog

    return catalog()


@router.post("/climate-zone-package")
async def climate_zone_package(body: dict[str, Any]) -> dict[str, Any]:
    """Apply selected climate zone defaults (models + risk triggers) to decision support."""
    from apps.simulation.threshold_store import apply_climate_zone_package

    zone_id = str((body or {}).get("zone_id") or "").strip()
    if not zone_id:
        return {"ok": False, "error": "zone_id required"}
    return apply_climate_zone_package(zone_id)


@router.get("/climate-zone-package/{zone_id}")
async def get_climate_zone_package(zone_id: str) -> dict[str, Any]:
    from apps.simulation.climate_zones import get_climate_zone
    from apps.simulation.threshold_store import ZONE_TO_PRESET

    z = get_climate_zone(zone_id)
    if not z:
        return {"ok": False, "error": "unknown zone"}
    return {
        "ok": True,
        "zone": z,
        "preset": ZONE_TO_PRESET.get(zone_id, "default"),
        "default_models": z.get("default_models") or [],
        "risk_triggers": z.get("risk_triggers") or [],
        "priority_packages": z.get("priority_packages") or [],
    }

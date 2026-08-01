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

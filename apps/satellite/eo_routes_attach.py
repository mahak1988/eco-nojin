"""Attach free EO stack routes onto the main satellite APIRouter."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from apps.satellite import eo_stack


def attach_eo_routes(router: APIRouter) -> None:
    @router.get("/eo/catalog")
    async def eo_catalog() -> dict[str, Any]:
        return eo_stack.catalog_overview()

    @router.get("/eo/scenes")
    async def eo_scenes(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
        collection: str = Query("sentinel-2-l2a"),
        days: int = Query(60, ge=7, le=365),
        max_items: int = Query(12, ge=1, le=50),
    ) -> dict[str, Any]:
        cloud = 40.0 if "sentinel-2" in collection or "landsat" in collection else None
        return await eo_stack.search_scenes(
            lat, lon, collection=collection, days=days, max_items=max_items, cloud_max=cloud
        )

    @router.get("/eo/sensors")
    async def eo_sensors(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
        days: int = Query(60, ge=14, le=180),
    ) -> dict[str, Any]:
        return await eo_stack.multi_sensor_availability(lat, lon, days=days)

    @router.get("/eo/vegetation")
    async def eo_vegetation(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
        days: int = Query(60, ge=14, le=180),
    ) -> dict[str, Any]:
        return await eo_stack.vegetation_bundle(lat, lon, days=days)

    @router.get("/eo/dem")
    async def eo_dem(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
    ) -> dict[str, Any]:
        return await eo_stack.dem_bundle(lat, lon)

    @router.get("/eo/erosion")
    async def eo_erosion(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
        days: int = Query(30, ge=14, le=90),
    ) -> dict[str, Any]:
        return await eo_stack.erosion_bundle(lat, lon, days=days)

    @router.get("/eo/climate")
    async def eo_climate(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
    ) -> dict[str, Any]:
        return await eo_stack.climate_bundle(lat, lon)

    @router.get("/eo/summary")
    async def eo_summary(
        lat: float = Query(32.65),
        lon: float = Query(51.67),
    ) -> dict[str, Any]:
        return await eo_stack.full_summary(lat, lon)

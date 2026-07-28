"""Satellite API — indices, timeseries, spatial cache."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.satellite.fetchers.sentinel2 import fetch_indices
from apps.satellite.storage import cache_samples, spatial_nearby
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission

router = APIRouter(prefix="/api/v1/satellite", tags=["Satellite"])


@router.get("/indices")
async def get_indices(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=10, le=365),
    cloud_max: int = Query(30, ge=0, le=100),
    farm_id: Optional[int] = None,
    persist: bool = Query(False),
    session: AsyncSession = Depends(get_db_session),
):
    """Sentinel-2 NDVI, NDWI, NDMI, SMI series."""
    end = date.today()
    start = end - timedelta(days=days)
    samples = fetch_indices(lat, lon, start, end, cloud_max)
    data = [s.to_dict() for s in samples]
    cached = 0
    if persist:
        cached = await cache_samples(session, data, lat, lon, farm_id)
    latest = data[-1] if data else None
    return {
        "lat": lat,
        "lon": lon,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "count": len(data),
        "latest": latest,
        "series": data,
        "cached_rows": cached,
    }


@router.get("/ndvi")
async def ndvi_compat(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=10, le=365),
):
    samples = fetch_indices(lat, lon, date.today() - timedelta(days=days), date.today())
    return {
        "provider": samples[-1].provider if samples else "none",
        "mean_ndvi": samples[-1].ndvi if samples else None,
        "series": [{"date": s.date, "ndvi": s.ndvi} for s in samples],
    }


@router.get("/timeseries")
async def timeseries(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=10, le=365),
):
    samples = fetch_indices(lat, lon, date.today() - timedelta(days=days), date.today())
    return {
        "data": [
            {
                "date": s.date,
                "ndvi": s.ndvi,
                "ndwi": s.ndwi,
                "ndmi": s.ndmi,
                "smi": s.smi,
                "cloud_pct": s.cloud_pct,
                "provider": s.provider,
            }
            for s in samples
        ]
    }


@router.get("/spatial/nearby")
async def nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: float = Query(5000, ge=100, le=100_000),
    session: AsyncSession = Depends(get_db_session),
):
    rows = await spatial_nearby(session, lat, lon, radius_m)
    return {"data": rows, "count": len(rows)}


@router.post("/indices/refresh")
async def refresh_and_cache(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    farm_id: Optional[int] = None,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("satellite:write")),
):
    samples = fetch_indices(lat, lon)
    data = [s.to_dict() for s in samples]
    n = await cache_samples(session, data, lat, lon, farm_id)
    return {"cached": n, "latest": data[-1] if data else None}

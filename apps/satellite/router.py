"""Satellite API routes."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Query

from apps.satellite.gee_status import probe_gee
from apps.satellite.providers.base import BBox
from apps.satellite.service import get_satellite_service

router = APIRouter(prefix="/api/v1/satellite", tags=["Satellite"])


@router.get("/gee/status")
async def gee_status() -> dict[str, Any]:
    return probe_gee()


@router.get("/availability")
async def availability(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(60, ge=7, le=365),
) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox(min_lon=lon - 0.05, min_lat=lat - 0.05, max_lon=lon + 0.05, max_lat=lat + 0.05)
    svc = get_satellite_service()
    return await svc.check_availability(bbox, start, end)


@router.get("/timeseries")
async def timeseries(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(90, ge=7, le=365),
    farm_id: int = Query(0),
) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=days)
    bbox = BBox(min_lon=lon - 0.05, min_lat=lat - 0.05, max_lon=lon + 0.05, max_lat=lat + 0.05)
    svc = get_satellite_service()
    rows = await svc.get_ndvi_timeseries(farm_id, bbox, start, end)
    return {
        "lat": lat,
        "lon": lon,
        "count": len(rows),
        "provider": rows[0].provider if rows else None,
        "data": [r.to_dict() for r in rows],
    }


@router.get("/ndvi")
async def ndvi_point(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
) -> dict[str, Any]:
    bbox = BBox(min_lon=lon - 0.02, min_lat=lat - 0.02, max_lon=lon + 0.02, max_lat=lat + 0.02)
    svc = get_satellite_service()
    row = await svc.get_ndvi_image(bbox, date.today() - timedelta(days=15))
    return row.to_dict()


@router.get("/indices")
async def indices(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(60, ge=7, le=365),
) -> dict[str, Any]:
    try:
        from apps.satellite.fetchers.sentinel2_fetcher import fetch_indices

        end = date.today()
        start = end - timedelta(days=days)
        rows = fetch_indices(lat, lon, start, end)
        return {
            "lat": lat,
            "lon": lon,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "count": len(rows),
            "data": [r.__dict__ if hasattr(r, "__dict__") else r for r in rows],
        }
    except Exception as e:
        return {"lat": lat, "lon": lon, "count": 0, "error": str(e)[:200], "data": []}


@router.post("/change-detection")
async def change_detection(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(120, ge=30, le=365),
) -> dict[str, Any]:
    end = date.today()
    mid = end - timedelta(days=days // 2)
    start = end - timedelta(days=days)
    bbox = BBox(min_lon=lon - 0.05, min_lat=lat - 0.05, max_lon=lon + 0.05, max_lat=lat + 0.05)
    svc = get_satellite_service()
    a = await svc.get_ndvi_timeseries(0, bbox, start, mid)
    b = await svc.get_ndvi_timeseries(0, bbox, mid, end)
    ma = sum(r.mean_ndvi for r in a) / max(len(a), 1) if a else 0.0
    mb = sum(r.mean_ndvi for r in b) / max(len(b), 1) if b else 0.0
    delta = mb - ma
    return {
        "period_a": {"start": start.isoformat(), "end": mid.isoformat(), "mean_ndvi": round(ma, 4)},
        "period_b": {"start": mid.isoformat(), "end": end.isoformat(), "mean_ndvi": round(mb, 4)},
        "delta_ndvi": round(delta, 4),
        "signal": "greening" if delta > 0.05 else ("browning" if delta < -0.05 else "stable"),
    }


@router.get("/fields")
async def fields_stub(farm_id: Optional[int] = None) -> dict[str, Any]:
    return {"data": [], "farm_id": farm_id, "message": "Link farm GeoJSON via /api/v1/farms/:id/geojson"}

"""Satellite API — catalog + Section-6 service orchestration."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from apps.satellite.catalog import ROLES, catalog_by_role, roles_list
from apps.satellite.providers.base import BBox
from apps.satellite.providers.chain import default_chain
from apps.satellite.service import get_satellite_service

router = APIRouter(prefix="/api/v1/satellite", tags=["Satellite"])
_chain = default_chain()


class ChangeRequest(BaseModel):
    lat: float = 32.65
    lon: float = 51.67
    date_a: Optional[str] = None
    date_b: Optional[str] = None
    period_a_start: Optional[str] = None
    period_a_end: Optional[str] = None
    period_b_start: Optional[str] = None
    period_b_end: Optional[str] = None
    farm_id: Optional[int] = None
    async_mode: bool = False


@router.get("/catalog")
async def satellite_catalog(role: Optional[str] = None):
    return {
        "roles": ROLES,
        "roles_count": len(ROLES),
        "items": catalog_by_role(role),
        "items_count": len(catalog_by_role(role)),
    }


@router.get("/roles")
async def satellite_roles():
    return {"count": len(ROLES), "items": roles_list()}


@router.get("/availability")
async def availability(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    min_lng: Optional[float] = None,
    min_lat: Optional[float] = None,
    max_lng: Optional[float] = None,
    max_lat: Optional[float] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    today = date.today()
    start = start_date or (today - timedelta(days=90))
    end = end_date or today
    if None not in (min_lng, min_lat, max_lng, max_lat):
        bbox = BBox(min_lng, min_lat, max_lng, max_lat)  # type: ignore[arg-type]
    else:
        bbox = BBox.from_point(lat, lon)
    svc = get_satellite_service()
    return await svc.check_availability(bbox, start, end)


@router.get("/ndvi")
async def ndvi(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    date_str: Optional[str] = Query(None, alias="date"),
):
    svc = get_satellite_service()
    d = date.fromisoformat(date_str) if date_str else date.today()
    r = await svc.get_ndvi_image(BBox.from_point(lat, lon), d)
    out = r.to_dict()
    out["lat"] = lat
    out["lon"] = lon
    out["ndvi"] = r.mean_ndvi
    return out


@router.get("/timeseries")
async def timeseries(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    start: Optional[str] = None,
    end: Optional[str] = None,
    farm_id: int = 0,
):
    today = date.today()
    end_d = date.fromisoformat(end) if end else today
    start_d = date.fromisoformat(start) if start else (today - timedelta(days=180))
    svc = get_satellite_service()
    rows = await svc.get_ndvi_timeseries(farm_id, BBox.from_point(lat, lon), start_d, end_d)
    return {
        "farm_id": farm_id,
        "lat": lat,
        "lon": lon,
        "start": start_d.isoformat(),
        "end": end_d.isoformat(),
        "points": [{"date": r.date.isoformat(), "ndvi": r.mean_ndvi} for r in rows],
        "data": [r.to_dict() for r in rows],
        "provider": rows[0].provider if rows else None,
    }


@router.get("/topography")
async def topography(lat: float = Query(32.65), lon: float = Query(51.67)):
    return await _chain.by_role("topography", lat, lon)


@router.get("/thermal")
async def thermal(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    date: Optional[str] = None,
):
    return await _chain.by_role("thermal", lat, lon, date)


@router.get("/soil-moisture")
async def soil_moisture(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    date: Optional[str] = None,
):
    return await _chain.by_role("soil_moisture", lat, lon, date)


@router.get("/by-role")
async def by_role(
    role: str = Query(...),
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    date: Optional[str] = None,
):
    return await _chain.by_role(role, lat, lon, date)


@router.post("/change-detection")
async def change_detection(body: ChangeRequest):
    today = date.today()
    pa_s = body.period_a_start or body.date_a or (today - timedelta(days=90)).isoformat()
    pa_e = body.period_a_end or (today - timedelta(days=45)).isoformat()
    pb_s = body.period_b_start or (today - timedelta(days=30)).isoformat()
    pb_e = body.period_b_end or body.date_b or today.isoformat()

    if body.async_mode:
        try:
            from apps.satellite.tasks import change_detection_task

            task = change_detection_task.delay(
                lat=body.lat,
                lon=body.lon,
                period_a_start=pa_s,
                period_a_end=pa_e,
                period_b_start=pb_s,
                period_b_end=pb_e,
                farm_id=body.farm_id,
            )
            return {"task_id": task.id, "status": "processing"}
        except Exception as e:
            pass  # fall through sync

    from apps.satellite.tasks import _change_detection_sync

    result = _change_detection_sync(
        body.lat, body.lon, pa_s, pa_e, pb_s, pb_e, body.farm_id
    )
    # legacy fields
    result["delta"] = result.get("delta_ndvi")
    result["interpretation"] = result.get("status")
    result["ndvi_a"] = result.get("mean_ndvi_a")
    result["ndvi_b"] = result.get("mean_ndvi_b")
    return result


@router.post("/aquacrop-calibrate")
async def aquacrop_calibrate(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=180),
):
    from apps.satellite.aquacrop_bridge import run_aquacrop_with_satellite

    end = date.today()
    start = end - timedelta(days=days)
    return await run_aquacrop_with_satellite(lat, lon, start, end)


@router.get("/fields")
async def satellite_fields():
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"id": "f1", "name": "North Field", "ndvi": 0.62},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [51.66, 32.64],
                            [51.68, 32.64],
                            [51.68, 32.66],
                            [51.66, 32.66],
                            [51.66, 32.64],
                        ]
                    ],
                },
            }
        ],
    }

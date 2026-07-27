"""Satellite API — catalog, NDVI, topography, thermal, change detection."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from apps.satellite.catalog import ROLES, catalog_by_role
from apps.satellite.providers.chain import default_chain

router = APIRouter(prefix="/api/v1/satellite", tags=["Satellite"])
_chain = default_chain()


class ChangeRequest(BaseModel):
    lat: float = 32.65
    lon: float = 51.67
    date_a: Optional[str] = None
    date_b: Optional[str] = None


@router.get("/catalog")
async def satellite_catalog(role: Optional[str] = None):
    return {"roles": ROLES, "items": catalog_by_role(role)}


@router.get("/roles")
async def satellite_roles():
    return ROLES


@router.get("/availability")
async def availability(lat: float = Query(32.65), lon: float = Query(51.67)):
    return await _chain.availability(lat, lon)


@router.get("/ndvi")
async def ndvi(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    date: Optional[str] = None,
):
    return await _chain.ndvi(lat, lon, date)


@router.get("/timeseries")
async def timeseries(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    start: Optional[str] = None,
    end: Optional[str] = None,
):
    today = date.today()
    end_s = end or today.isoformat()
    start_s = start or (today - timedelta(days=180)).isoformat()
    return await _chain.timeseries(lat, lon, start_s, end_s)


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


@router.get("/by-role")
async def by_role(
    role: str = Query(..., description="vegetation|thermal|topography|optical"),
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    date: Optional[str] = None,
):
    return await _chain.by_role(role, lat, lon, date)


@router.post("/change-detection")
async def change_detection(body: ChangeRequest):
    today = date.today()
    da = body.date_a or (today - timedelta(days=90)).isoformat()
    db = body.date_b or today.isoformat()
    a = await _chain.ndvi(body.lat, body.lon, da)
    b = await _chain.ndvi(body.lat, body.lon, db)
    va = float(a.get("ndvi") or 0)
    vb = float(b.get("ndvi") or 0)
    delta = round(vb - va, 3)
    return {
        "lat": body.lat,
        "lon": body.lon,
        "date_a": da,
        "date_b": db,
        "ndvi_a": va,
        "ndvi_b": vb,
        "delta": delta,
        "interpretation": (
            "greening" if delta > 0.05 else "browning" if delta < -0.05 else "stable"
        ),
        "provider": a.get("provider"),
    }


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

"""Spatial farm queries (PostGIS when available)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.shared_core.geo.postgis import query_farms_nearby

router = APIRouter(prefix="/api/v1/farms", tags=["FarmsSpatial"])


@router.get("/spatial/nearby")
async def farms_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: float = Query(10000, ge=100, le=200_000),
    session: AsyncSession = Depends(get_db_session),
):
    rows = await query_farms_nearby(session, lat, lon, radius_m)
    return {"data": rows, "count": len(rows)}

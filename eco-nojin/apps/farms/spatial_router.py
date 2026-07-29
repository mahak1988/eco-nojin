"""Spatial farm queries (PostGIS when available)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session, get_engine
from apps.shared_core.geo.postgis import ensure_farms_spatial, query_farms_nearby

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


@router.post("/spatial/ensure-index")
async def ensure_spatial_index() -> dict[str, Any]:
    """Idempotent: PostGIS extension + farms.geom + GIST index + backfill."""
    eng = get_engine()
    return await ensure_farms_spatial(eng)

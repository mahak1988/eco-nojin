"""PostGIS helpers — enable extension + spatial SQL utilities."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def ensure_postgis(engine: AsyncEngine) -> bool:
    """CREATE EXTENSION IF NOT EXISTS postgis — no-op on SQLite."""
    if engine.dialect.name != "postgresql":
        return False
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        logger.info("PostGIS extension ensured")
        return True
    except Exception as e:
        logger.warning("PostGIS enable failed: %s", e)
        return False


def farms_within_radius_sql() -> str:
    return """
    SELECT id, name, latitude, longitude,
           ST_DistanceSphere(
             ST_MakePoint(longitude, latitude),
             ST_MakePoint(:lon, :lat)
           ) AS dist_m
    FROM farms
    WHERE is_deleted IS FALSE
      AND latitude IS NOT NULL AND longitude IS NOT NULL
      AND ST_DWithin(
            ST_MakePoint(longitude, latitude)::geography,
            ST_MakePoint(:lon, :lat)::geography,
            :radius_m
          )
    ORDER BY dist_m
    LIMIT :lim
    """


async def query_farms_nearby(
    session,
    lat: float,
    lon: float,
    radius_m: float = 10000,
    limit: int = 50,
) -> list[dict[str, Any]]:
    bind = session.get_bind()
    dialect = bind.dialect.name if bind is not None else "sqlite"
    if dialect == "postgresql":
        try:
            rows = (
                await session.execute(
                    text(farms_within_radius_sql()),
                    {"lat": lat, "lon": lon, "radius_m": radius_m, "lim": limit},
                )
            ).mappings().all()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning("PostGIS farm query failed: %s", e)

    # fallback — load farms with coords via ORM if available
    try:
        from sqlalchemy import select

        from apps.farms.models import Farm

        result = await session.execute(
            select(Farm).where(Farm.is_deleted.is_(False)).limit(200)
        )
        farms = result.scalars().all()
        from apps.satellite.storage import _haversine_m

        out = []
        for f in farms:
            if f.latitude is None or f.longitude is None:
                continue
            d = _haversine_m(lat, lon, f.latitude, f.longitude)
            if d <= radius_m:
                out.append(
                    {
                        "id": f.id,
                        "name": f.name,
                        "latitude": f.latitude,
                        "longitude": f.longitude,
                        "dist_m": round(d, 1),
                    }
                )
        out.sort(key=lambda x: x["dist_m"])
        return out[:limit]
    except Exception as e:
        logger.warning("Farm nearby fallback failed: %s", e)
        return []

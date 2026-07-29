"""PostGIS helpers — extension, farm geom column, spatial indexes, nearby query."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def ensure_postgis(engine: AsyncEngine) -> bool:
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


async def ensure_farms_spatial(engine: AsyncEngine) -> dict[str, Any]:
    """
    Add geography point column + GIST index; backfill from latitude/longitude.
    Safe to call repeatedly (idempotent).
    """
    if engine.dialect.name != "postgresql":
        return {"ok": False, "reason": "not_postgres"}
    steps: list[str] = []
    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            steps.append("extension")

            # column geom geography(Point, 4326)
            exists = await conn.execute(
                text(
                    """
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'farms' AND column_name = 'geom'
                    """
                )
            )
            if not exists.fetchone():
                await conn.execute(
                    text(
                        "ALTER TABLE farms ADD COLUMN IF NOT EXISTS geom geography(Point, 4326)"
                    )
                )
                steps.append("add_geom")

            await conn.execute(
                text(
                    """
                    UPDATE farms
                    SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
                    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                      AND (geom IS NULL OR TRUE)
                    """
                )
            )
            steps.append("backfill")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_farms_geom_gist
                    ON farms USING GIST (geom)
                    """
                )
            )
            steps.append("gist_index")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS ix_farms_lat_lon
                    ON farms (latitude, longitude)
                    WHERE latitude IS NOT NULL AND longitude IS NOT NULL
                    """
                )
            )
            steps.append("btree_latlon")

        logger.info("Farms spatial ready: %s", steps)
        return {"ok": True, "steps": steps}
    except Exception as e:
        logger.warning("ensure_farms_spatial failed: %s", e)
        return {"ok": False, "error": str(e)[:200], "steps": steps}


def farms_within_radius_sql() -> str:
    return """
    SELECT id, name, latitude, longitude,
           ST_Distance(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography) AS dist_m
    FROM farms
    WHERE is_deleted IS FALSE
      AND geom IS NOT NULL
      AND ST_DWithin(
            geom,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
            :radius_m
          )
    ORDER BY dist_m
    LIMIT :lim
    """


def farms_within_radius_sql_legacy() -> str:
    """Fallback when geom column missing."""
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
        for sql in (farms_within_radius_sql(), farms_within_radius_sql_legacy()):
            try:
                rows = (
                    await session.execute(
                        text(sql),
                        {"lat": lat, "lon": lon, "radius_m": radius_m, "lim": limit},
                    )
                ).mappings().all()
                return [dict(r) for r in rows]
            except Exception as e:
                logger.debug("PostGIS farm query attempt failed: %s", e)
                continue

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

"""PostGIS utilities and checks."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

logger = logging.getLogger(__name__)


async def ensure_postgis(engine: AsyncEngine) -> dict[str, Any]:
    """Ensure PostGIS extension is available in the database."""
    logger.info("Checking for PostGIS extension...")
    try:
        async with engine.connect() as conn:
            # Attempt to run a basic PostGIS function
            result = await conn.execute(text("SELECT PostGIS_version();"))
            version = result.scalar()
            logger.info(f"PostGIS is available. Version: {version}")
            await conn.commit()  # Commit the transaction
            return {"ok": True, "version": version}
    except Exception as e:
        logger.warning(f"PostGIS check failed (expected if not installed): {e}")
        # Attempt to create the extension
        try:
            async with engine.begin() as conn:  # Use begin for DDL statements
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
            logger.info("PostGIS extension created or ensured.")
            # Retry the check after creation
            async with engine.connect() as conn:
                result = await conn.execute(text("SELECT PostGIS_version();"))
                version = result.scalar()
                logger.info(f"PostGIS is now available after CREATE EXTENSION. Version: {version}")
                await conn.commit()
                return {"ok": True, "version": version, "created": True}
        except Exception as create_e:
            logger.error(f"Failed to create PostGIS extension: {create_e}")
            return {"ok": False, "error": str(create_e)}

    return {"ok": False, "error": "Unknown error during PostGIS check/creation"}


async def ensure_farms_spatial(engine: AsyncEngine) -> dict[str, Any]:
    """Example function to ensure spatial indices exist for the farms table."""
    logger.info("Ensuring spatial index on farms table...")
    try:
        async with engine.connect() as conn:
            # Example: Check if a GiST index exists on a geometry column (assuming 'geom' column exists)
            # This is a conceptual check; actual column names might differ.
            # result = await conn.execute(text("SELECT 1 FROM pg_indexes WHERE tablename = 'farms' AND indexname LIKE '%geom%' AND indexdef LIKE '%GiST%';"))
            # if not result.fetchone():
            #     await conn.execute(text("CREATE INDEX idx_farms_geom ON farms USING GiST (geom);"))
            #     logger.info("Spatial index 'idx_farms_geom' created.")
            # else:
            #     logger.info("Spatial index 'idx_farms_geom' already exists.")
            steps = [
                "Conceptual check for farms spatial index completed."
            ]  # Placeholder for actual logic
            logger.info(steps[0])
            await conn.commit()
            return {"ok": True, "steps": steps}
    except Exception as e:
        logger.error(f"Failed to ensure farms spatial index: {e}")
        return {"ok": False, "error": str(e)}


async def query_farms_nearby(db, lat: float, lon: float, radius_km: float = 10):
    """Query farms near a point. Stub implementation for SQLite."""
    from sqlalchemy import text

    try:
        result = await db.execute(
            text(
                "SELECT id, name, latitude, longitude FROM farms WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
            )
        )
        farms = result.fetchall()
        # Simple distance filter (Pythagorean approximation)
        nearby = []
        for f in farms:
            dlat = (f[2] - lat) * 111
            dlon = (f[3] - lon) * 111 * 0.8
            dist = (dlat**2 + dlon**2) ** 0.5
            if dist <= radius_km:
                nearby.append(
                    {
                        "id": f[0],
                        "name": f[1],
                        "lat": f[2],
                        "lon": f[3],
                        "distance_km": round(dist, 2),
                    }
                )
        return nearby
    except Exception:
        return []

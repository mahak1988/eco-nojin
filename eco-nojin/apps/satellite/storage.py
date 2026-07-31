"""Cache EO index samples — PostGIS when available, else JSON table."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime, Float, Integer, String, Text, select
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base

logger = logging.getLogger(__name__)


class SatelliteIndexCache(Base):
    __tablename__ = "satellite_index_cache"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    # WKT point for PostGIS-compatible storage (ST_GeomFromText on PG)
    geom_wkt: Mapped[str] = mapped_column(String(128), nullable=False)
    acquired_on: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    ndvi: Mapped[float] = mapped_column(Float, nullable=False)
    ndwi: Mapped[float] = mapped_column(Float, nullable=False)
    ndmi: Mapped[float] = mapped_column(Float, nullable=False)
    smi: Mapped[float] = mapped_column(Float, nullable=False)
    cloud_pct: Mapped[float] = mapped_column(Float, default=0.0)
    provider: Mapped[str] = mapped_column(String(64), default="synthetic-s2")
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


def point_wkt(lat: float, lon: float) -> str:
    return f"POINT({lon} {lat})"


async def cache_samples(
    session,
    samples: list[dict[str, Any]],
    lat: float,
    lon: float,
    farm_id: int | None = None,
) -> int:
    n = 0
    for s in samples:
        row = SatelliteIndexCache(
            farm_id=farm_id,
            lat=lat,
            lon=lon,
            geom_wkt=point_wkt(lat, lon),
            acquired_on=s["date"],
            ndvi=s["ndvi"],
            ndwi=s["ndwi"],
            ndmi=s.get("ndmi", 0.0),
            smi=s["smi"],
            cloud_pct=s.get("cloud_pct", 0.0),
            provider=s.get("provider", ""),
            payload_json=json.dumps(s),
        )
        session.add(row)
        n += 1
    await session.flush()
    return n


async def spatial_nearby(
    session,
    lat: float,
    lon: float,
    radius_m: float = 5000,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """
    Prefer PostGIS ST_DWithin when dialect is postgresql;
    else Haversine filter in Python after coarse bbox query.
    """
    bind = session.get_bind()
    dialect = bind.dialect.name if bind is not None else "sqlite"

    if dialect == "postgresql":
        try:
            sql = """
            SELECT id, farm_id, lat, lon, acquired_on, ndvi, ndwi, smi, provider,
                   ST_Distance(
                     ST_GeogFromText(geom_wkt),
                     ST_GeogFromText(:pt)
                   ) AS dist_m
            FROM satellite_index_cache
            WHERE ST_DWithin(
              ST_GeogFromText(geom_wkt),
              ST_GeogFromText(:pt),
              :radius
            )
            ORDER BY dist_m
            LIMIT :lim
            """
            # geom_wkt is 'POINT(lon lat)' — ST_GeogFromText needs SRID; use MakePoint fallback
            sql = """
            SELECT id, farm_id, lat, lon, acquired_on, ndvi, ndwi, smi, provider,
                   ST_DistanceSphere(
                     ST_MakePoint(lon, lat),
                     ST_MakePoint(:lon, :lat)
                   ) AS dist_m
            FROM satellite_index_cache
            WHERE ST_DWithin(
              ST_MakePoint(lon, lat)::geography,
              ST_MakePoint(:lon, :lat)::geography,
              :radius
            )
            ORDER BY dist_m
            LIMIT :lim
            """
            from sqlalchemy import text

            rows = (
                await session.execute(
                    text(sql), {"lat": lat, "lon": lon, "radius": radius_m, "lim": limit}
                )
            ).mappings().all()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.warning("PostGIS spatial query failed, fallback: %s", e)

    # SQLite / fallback
    result = await session.execute(
        select(SatelliteIndexCache).order_by(SatelliteIndexCache.acquired_on.desc()).limit(500)
    )
    rows = result.scalars().all()
    out = []
    for r in rows:
        d = _haversine_m(lat, lon, r.lat, r.lon)
        if d <= radius_m:
            out.append(
                {
                    "id": r.id,
                    "farm_id": r.farm_id,
                    "lat": r.lat,
                    "lon": r.lon,
                    "acquired_on": r.acquired_on,
                    "ndvi": r.ndvi,
                    "ndwi": r.ndwi,
                    "smi": r.smi,
                    "provider": r.provider,
                    "dist_m": round(d, 1),
                }
            )
        if len(out) >= limit:
            break
    out.sort(key=lambda x: x["dist_m"])
    return out


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    import math

    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))

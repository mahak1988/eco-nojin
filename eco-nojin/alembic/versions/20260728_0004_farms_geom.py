"""farms.geom geography + gist index

Revision ID: 20260728_0004
Revises: 20260728_0003
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "20260728_0004"
down_revision: str | None = "20260728_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    try:
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        op.execute(
            "ALTER TABLE farms ADD COLUMN IF NOT EXISTS geom geography(Point, 4326)"
        )
        op.execute(
            """
            UPDATE farms
            SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND geom IS NULL
            """
        )
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_farms_geom_gist ON farms USING GIST (geom)"
        )
        op.execute(
            """
            CREATE INDEX IF NOT EXISTS ix_farms_lat_lon
            ON farms (latitude, longitude)
            WHERE latitude IS NOT NULL AND longitude IS NOT NULL
            """
        )
    except Exception:
        pass


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    try:
        op.execute("DROP INDEX IF EXISTS ix_farms_geom_gist")
        op.execute("DROP INDEX IF EXISTS ix_farms_lat_lon")
        op.execute("ALTER TABLE farms DROP COLUMN IF EXISTS geom")
    except Exception:
        pass

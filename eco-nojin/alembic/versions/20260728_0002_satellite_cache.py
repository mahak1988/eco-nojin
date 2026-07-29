"""satellite_index_cache table

Revision ID: 20260728_0002
Revises: 20260728_0001
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260728_0002"
down_revision: Union[str, None] = "20260728_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "satellite_index_cache" in insp.get_table_names():
        return
    op.create_table(
        "satellite_index_cache",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("farm_id", sa.Integer(), nullable=True),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("geom_wkt", sa.String(128), nullable=False),
        sa.Column("acquired_on", sa.String(16), nullable=False),
        sa.Column("ndvi", sa.Float(), nullable=False),
        sa.Column("ndwi", sa.Float(), nullable=False),
        sa.Column("ndmi", sa.Float(), nullable=False),
        sa.Column("smi", sa.Float(), nullable=False),
        sa.Column("cloud_pct", sa.Float(), server_default="0"),
        sa.Column("provider", sa.String(64), server_default="synthetic-s2"),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sat_cache_farm", "satellite_index_cache", ["farm_id"])
    op.create_index("ix_sat_cache_date", "satellite_index_cache", ["acquired_on"])


def downgrade() -> None:
    try:
        op.drop_table("satellite_index_cache")
    except Exception:
        pass

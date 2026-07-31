"""Create satellite_index_cache table."""

from __future__ import annotations

from contextlib import suppress

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260728_0002"
down_revision = "20260728_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: Create satellite_index_cache table."""
    op.create_table(
        "satellite_index_cache",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("location_wkt", sa.String(length=255), nullable=False),
        sa.Column("ndvi_mean", sa.Float(), nullable=True),
        sa.Column("ndvi_std", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("date", "location_wkt", name="uq_date_location"),
    )
    op.create_index(op.f("ix_satellite_index_cache_date"), "satellite_index_cache", ["date"], unique=False)


def downgrade() -> None:
    """Downgrade: Drop satellite_index_cache table."""
    with suppress(Exception):
        op.drop_table("satellite_index_cache")

"""Phase 3 science models — RothC, AquaCrop, coupling.

Revision ID: 20260728_0003
Revises: 20260728_0002
"""

from __future__ import annotations

from contextlib import suppress

import sqlalchemy as sa

from alembic import op

revision = "20260728_0003"
down_revision = "20260728_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: Create science model tables."""
    # Detect dialect and handle PostGIS
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        with suppress(Exception):
            op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    # RothC model table
    op.create_table(
        "rothc_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("input_params", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # AquaCrop model table
    op.create_table(
        "aquacrop_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("input_params", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Coupling engine table
    op.create_table(
        "coupling_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("input_params", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # Spatial farm boundaries
    if dialect == "postgresql":
        op.create_table(
            "farm_boundaries",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("farm_id", sa.Integer(), nullable=False),
            sa.Column("geom", sa.dialects.postgresql.GEOMETRY('POLYGON'), nullable=False),
            sa.Column("area_hectares", sa.Float(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(['farm_id'], ['farms.id'], ),
        )
        op.create_index('idx_farm_boundaries_geom', 'farm_boundaries', ['geom'], postgresql_using='gist')


def downgrade() -> None:
    """Downgrade: Drop science model tables."""
    with suppress(Exception):
        op.drop_table("coupling_runs")
    with suppress(Exception):
        op.drop_table("aquacrop_runs")
    with suppress(Exception):
        op.drop_table("rothc_runs")
    with suppress(Exception):
        op.drop_table("farm_boundaries")

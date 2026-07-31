"""phase2 farms sensors alerts

Revision ID: 20260728_0001
Revises: 20260727_0003
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260728_0001"
down_revision: str | None = "20260727_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return name in insp.get_table_names()


def upgrade() -> None:
    if not _table_exists("farms"):
        op.create_table(
            "farms",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("area_ha", sa.Float(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=True),
            sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    if not _table_exists("sensors"):
        op.create_table(
            "sensors",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("sensor_type", sa.String(40), nullable=False),
            sa.Column("unit", sa.String(20), server_default=""),
            sa.Column("farm_id", sa.Integer(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("1")),
            sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )

    if not _table_exists("sensor_readings"):
        op.create_table(
            "sensor_readings",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("sensor_id", sa.Integer(), nullable=False),
            sa.Column("value", sa.Float(), nullable=False),
            sa.Column("recorded_at", sa.DateTime(), nullable=True),
        )

    if not _table_exists("alert_rules"):
        op.create_table(
            "alert_rules",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("sensor_type", sa.String(40), nullable=False),
            sa.Column("operator", sa.String(8), server_default="lt"),
            sa.Column("threshold", sa.Float(), nullable=False),
            sa.Column("severity", sa.String(20), server_default="warning"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("1")),
            sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("0")),
        )

    if not _table_exists("alert_events"):
        op.create_table(
            "alert_events",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("rule_id", sa.Integer(), nullable=True),
            sa.Column("sensor_id", sa.Integer(), nullable=True),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("severity", sa.String(20), server_default="warning"),
            sa.Column("is_acked", sa.Boolean(), server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        )


def downgrade() -> None:
    for t in ("alert_events", "alert_rules", "sensor_readings", "sensors", "farms"):
        if _table_exists(t):
            op.drop_table(t)

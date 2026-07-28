"""phase2 farms crops monitoring inventory

Revision ID: 20260728_0001
Revises: 20260727_0002_rbac
Create Date: 2026-07-28
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260728_0001"
down_revision: Union[str, None] = "20260727_0002_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Idempotent-ish: create if not exists via try/except pattern not in alembic;
    # use IF NOT EXISTS where dialect supports (Postgres).
    bind = op.get_bind()
    dialect = bind.dialect.name

    def _create(table: str, cols: list):
        if dialect == "postgresql":
            # check existence
            exists = bind.execute(
                sa.text("SELECT to_regclass(:t)"),
                {"t": table},
            ).scalar()
            if exists:
                return
        op.create_table(table, *cols)

    _create(
        "farms",
        [
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("area_ha", sa.Float(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=True),
            sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        ],
    )
    _create(
        "sensors",
        [
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("sensor_type", sa.String(40), nullable=False),
            sa.Column("unit", sa.String(20), server_default=""),
            sa.Column("farm_id", sa.Integer(), nullable=True),
            sa.Column("latitude", sa.Float(), nullable=True),
            sa.Column("longitude", sa.Float(), nullable=True),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        ],
    )
    _create(
        "sensor_readings",
        [
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("sensor_id", sa.Integer(), nullable=False),
            sa.Column("value", sa.Float(), nullable=False),
            sa.Column("recorded_at", sa.DateTime(), nullable=True),
        ],
    )
    _create(
        "alert_rules",
        [
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("name", sa.String(120), nullable=False),
            sa.Column("sensor_type", sa.String(40), nullable=False),
            sa.Column("operator", sa.String(8), server_default="lt"),
            sa.Column("threshold", sa.Float(), nullable=False),
            sa.Column("severity", sa.String(20), server_default="warning"),
            sa.Column("is_active", sa.Boolean(), server_default=sa.text("true")),
            sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false")),
        ],
    )
    _create(
        "alert_events",
        [
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("rule_id", sa.Integer(), nullable=True),
            sa.Column("sensor_id", sa.Integer(), nullable=True),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("severity", sa.String(20), server_default="warning"),
            sa.Column("is_acked", sa.Boolean(), server_default=sa.text("false")),
            sa.Column("created_at", sa.DateTime(), nullable=True),
        ],
    )


def downgrade() -> None:
    for t in ("alert_events", "alert_rules", "sensor_readings", "sensors", "farms"):
        try:
            op.drop_table(t)
        except Exception:
            pass

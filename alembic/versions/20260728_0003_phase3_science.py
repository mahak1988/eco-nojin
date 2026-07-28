"""phase3 simulation_runs + postgis enable attempt

Revision ID: 20260728_0003
Revises: 20260728_0002
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260728_0003"
down_revision: Union[str, None] = "20260728_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        try:
            op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
        except Exception:
            pass

    insp = sa.inspect(bind)
    if "simulation_runs" not in insp.get_table_names():
        op.create_table(
            "simulation_runs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("model", sa.String(64), nullable=False),
            sa.Column("status", sa.String(32), server_default="completed"),
            sa.Column("params_json", sa.Text(), nullable=True),
            sa.Column("result_json", sa.Text(), nullable=True),
            sa.Column("task_id", sa.String(128), nullable=True),
            sa.Column("farm_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_sim_runs_model", "simulation_runs", ["model"])


def downgrade() -> None:
    try:
        op.drop_table("simulation_runs")
    except Exception:
        pass

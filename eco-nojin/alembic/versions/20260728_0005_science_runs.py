"""science_runs table (phase3 persist, avoids legacy simulation_runs conflict)

Revision ID: 20260728_0005
Revises: 20260728_0004
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260728_0005"
down_revision: Union[str, None] = "20260728_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "science_runs" not in insp.get_table_names():
        op.create_table(
            "science_runs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("model", sa.String(64), nullable=False),
            sa.Column("status", sa.String(32), server_default="completed"),
            sa.Column("params_json", sa.Text(), nullable=True),
            sa.Column("result_json", sa.Text(), nullable=True),
            sa.Column("task_id", sa.String(128), nullable=True),
            sa.Column("farm_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP")),
        )
        op.create_index("ix_science_runs_model", "science_runs", ["model"])


def downgrade() -> None:
    try:
        op.drop_table("science_runs")
    except Exception:
        pass

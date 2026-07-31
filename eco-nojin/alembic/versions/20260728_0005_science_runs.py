"""Create science_runs table for tracking model executions."""

from __future__ import annotations

from contextlib import suppress

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "20260728_0005"
down_revision = "20260728_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade: Create science_runs table."""
    op.create_table(
        "science_runs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_type", sa.String(length=100), nullable=False),
        sa.Column("parameters", sa.JSON(), nullable=False),
        sa.Column("results", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_science_runs_model_type"), "science_runs", ["model_type"], unique=False)
    op.create_index(op.f("ix_science_runs_status"), "science_runs", ["status"], unique=False)
    op.create_index(op.f("ix_science_runs_created_at"), "science_runs", ["created_at"], unique=False)


def downgrade() -> None:
    """Downgrade: Drop science_runs table."""
    with suppress(Exception):
        op.drop_table("science_runs")

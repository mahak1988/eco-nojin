"""ecocoin_mint_events table

Revision ID: 20260729_0001
Revises: 20260728_0005
Create Date: 2026-07-29
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260729_0001"
down_revision: str | None = "20260728_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "ecocoin_mint_events" in insp.get_table_names():
        return
    op.create_table(
        "ecocoin_mint_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("tx_hash", sa.String(length=80), nullable=False),
        sa.Column("recipient", sa.String(length=128), nullable=False),
        sa.Column("project_id", sa.String(length=128), nullable=False),
        sa.Column("credit_type", sa.Integer(), nullable=False),
        sa.Column("credit_name", sa.String(length=32), nullable=False),
        sa.Column("measured_value", sa.Float(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=False),
        sa.Column("region_multiplier", sa.Float(), nullable=False),
        sa.Column("scarcity_factor", sa.Float(), nullable=False),
        sa.Column("mint_total", sa.Float(), nullable=False),
        sa.Column("steward_share", sa.Float(), nullable=False),
        sa.Column("verifier_share", sa.Float(), nullable=False),
        sa.Column("treasury_share", sa.Float(), nullable=False),
        sa.Column("community_share", sa.Float(), nullable=False),
        sa.Column("verification_hash", sa.String(length=128), nullable=False),
        sa.Column("oracle_signature", sa.Text(), nullable=False),
        sa.Column("oracle_payload", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tx_hash"),
    )
    op.create_index("ix_ecocoin_mint_events_tx_hash", "ecocoin_mint_events", ["tx_hash"])
    op.create_index("ix_ecocoin_mint_events_recipient", "ecocoin_mint_events", ["recipient"])
    op.create_index("ix_ecocoin_mint_events_project_id", "ecocoin_mint_events", ["project_id"])


def downgrade() -> None:
    try:
        op.drop_index("ix_ecocoin_mint_events_project_id", table_name="ecocoin_mint_events")
        op.drop_index("ix_ecocoin_mint_events_recipient", table_name="ecocoin_mint_events")
        op.drop_index("ix_ecocoin_mint_events_tx_hash", table_name="ecocoin_mint_events")
        op.drop_table("ecocoin_mint_events")
    except Exception:
        pass

"""eco impact tables — evidence, peer votes, caps, verifiers

Revision ID: 20260731_0002
Revises: 20260731_0001
Create Date: 2026-07-31
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260731_0002"
down_revision: Union[str, None] = "20260731_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "eco_evidence",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("evidence_uid", sa.String(length=64), nullable=False),
        sa.Column("claim_uid", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=32), nullable=False),
        sa.Column("content_hash", sa.String(length=128), nullable=False),
        sa.Column("perceptual_hash", sa.String(length=64), nullable=True),
        sa.Column("storage_uri", sa.String(length=512), nullable=True),
        sa.Column("mime_type", sa.String(length=64), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("geo_lat", sa.Numeric(10, 7), nullable=True),
        sa.Column("geo_lng", sa.Numeric(10, 7), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("anomaly_flags", sa.Text(), nullable=True),
        sa.Column("uploader_id", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("evidence_uid"),
    )
    op.create_index("ix_eco_evidence_claim_uid", "eco_evidence", ["claim_uid"])
    op.create_index("ix_eco_evidence_claim_kind", "eco_evidence", ["claim_uid", "kind"])
    op.create_index("ix_eco_evidence_phash", "eco_evidence", ["perceptual_hash"])

    op.create_table(
        "eco_peer_votes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("claim_uid", sa.String(length=64), nullable=False),
        sa.Column("voter_id", sa.String(length=64), nullable=False),
        sa.Column("decision", sa.String(length=16), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("weight", sa.Numeric(6, 3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("claim_uid", "voter_id", name="uq_peer_vote_claim_voter"),
    )
    op.create_index("ix_eco_peer_claim", "eco_peer_votes", ["claim_uid"])

    op.create_table(
        "eco_verifier_profiles",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("reputation", sa.Numeric(8, 3), nullable=False),
        sa.Column("votes_cast", sa.Integer(), nullable=False),
        sa.Column("votes_aligned", sa.Integer(), nullable=False),
        sa.Column("is_accredited", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "eco_cap_ledger",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("amount_eco", sa.Numeric(28, 18), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_index("ix_eco_cap_user", "eco_cap_ledger", ["user_id"])


def downgrade() -> None:
    op.drop_table("eco_cap_ledger")
    op.drop_table("eco_verifier_profiles")
    op.drop_table("eco_peer_votes")
    op.drop_table("eco_evidence")

"""eco core tables + seed treasury buckets

Revision ID: 20260731_0001
Revises:
Create Date: 2026-07-31
"""
from typing import Sequence, Union
from decimal import Decimal

from alembic import op
import sqlalchemy as sa

revision: str = "20260731_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

BUCKET_SEED = [
    {
        "code": "COMMUNITY",
        "name": "Community Rewards",
        "allocation": Decimal("550000000"),
        "remaining": Decimal("550000000"),
        "description": "55% — Education, verified actions, livelihood for poor/unemployed",
    },
    {
        "code": "ORG",
        "name": "Organization Operations",
        "allocation": Decimal("250000000"),
        "remaining": Decimal("250000000"),
        "description": "25% — Salaries, ops, scientific verification, micro-loans",
    },
    {
        "code": "TREASURY",
        "name": "Ecosystem Treasury",
        "allocation": Decimal("100000000"),
        "remaining": Decimal("100000000"),
        "description": "10% — DEX liquidity, grants matching, emergency restoration",
    },
    {
        "code": "SCIENCE",
        "name": "Scientific & Assurance",
        "allocation": Decimal("70000000"),
        "remaining": Decimal("70000000"),
        "description": "7% — Audits, dMRV, Hypercert capacity, research",
    },
    {
        "code": "FOUNDERS",
        "name": "Founders & Early Contributors",
        "allocation": Decimal("30000000"),
        "remaining": Decimal("30000000"),
        "description": "3% — Core team, 6-mo cliff + 24-mo linear vesting",
    },
]


def upgrade() -> None:
    op.create_table(
        "eco_treasury_buckets",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("code", sa.Enum("COMMUNITY", "ORG", "TREASURY", "SCIENCE", "FOUNDERS", name="bucketcode"), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("allocation", sa.Numeric(precision=28, scale=18), nullable=False),
        sa.Column("remaining", sa.Numeric(precision=28, scale=18), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "eco_claims",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("claim_uid", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("level", sa.Enum("L1", "L2", "L3", "L4", name="assurancelevel"), nullable=False),
        sa.Column("status", sa.Enum("DRAFT", "SUBMITTED", "IN_REVIEW", "APPROVED", "REJECTED", "NEEDS_EVIDENCE", "REWARDED", name="claimstatus"), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("evidence_hash", sa.String(length=128), nullable=True),
        sa.Column("geo_lat", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("geo_lng", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("quality_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("reward_amount", sa.Numeric(precision=28, scale=18), nullable=True),
        sa.Column("verifier_id", sa.String(length=64), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("rewarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("claim_uid"),
    )
    op.create_index("ix_eco_claims_claim_uid", "eco_claims", ["claim_uid"])
    op.create_index("ix_eco_claims_user_id", "eco_claims", ["user_id"])
    op.create_index("ix_eco_claims_user_status", "eco_claims", ["user_id", "status"])
    op.create_index("ix_eco_claims_category_level", "eco_claims", ["category", "level"])

    op.create_table(
        "eco_mint_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_uid", sa.String(length=64), nullable=False),
        sa.Column("claim_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("amount", sa.Numeric(precision=28, scale=18), nullable=False),
        sa.Column("bucket", sa.Enum("COMMUNITY", "ORG", "TREASURY", "SCIENCE", "FOUNDERS", name="bucketcode", create_type=False), nullable=False),
        sa.Column("level", sa.Enum("L1", "L2", "L3", "L4", name="assurancelevel", create_type=False), nullable=True),
        sa.Column("mode", sa.Enum("local_ledger", "evm", name="mintmode"), nullable=False),
        sa.Column("tx_hash", sa.String(length=128), nullable=True),
        sa.Column("ledger_hash", sa.String(length=128), nullable=True),
        sa.Column("idempotency_key", sa.String(length=128), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["eco_claims.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_uid"),
        sa.UniqueConstraint("idempotency_key"),
    )
    op.create_index("ix_eco_mint_events_event_uid", "eco_mint_events", ["event_uid"])
    op.create_index("ix_eco_mint_events_user_id", "eco_mint_events", ["user_id"])
    op.create_index("ix_eco_mint_user_created", "eco_mint_events", ["user_id", "created_at"])

    op.create_table(
        "eco_balances",
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("balance", sa.Numeric(precision=28, scale=18), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "eco_idempotency_keys",
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("key"),
    )

    buckets = sa.table(
        "eco_treasury_buckets",
        sa.column("code", sa.Enum("COMMUNITY", "ORG", "TREASURY", "SCIENCE", "FOUNDERS", name="bucketcode")),
        sa.column("name", sa.String),
        sa.column("allocation", sa.Numeric),
        sa.column("remaining", sa.Numeric),
        sa.column("status", sa.String),
        sa.column("description", sa.Text),
    )
    op.bulk_insert(
        buckets,
        [
            {
                "code": b["code"],
                "name": b["name"],
                "allocation": b["allocation"],
                "remaining": b["remaining"],
                "status": "active",
                "description": b["description"],
            }
            for b in BUCKET_SEED
        ],
    )


def downgrade() -> None:
    op.drop_table("eco_idempotency_keys")
    op.drop_table("eco_balances")
    op.drop_index("ix_eco_mint_user_created", table_name="eco_mint_events")
    op.drop_index("ix_eco_mint_events_user_id", table_name="eco_mint_events")
    op.drop_index("ix_eco_mint_events_event_uid", table_name="eco_mint_events")
    op.drop_table("eco_mint_events")
    op.drop_index("ix_eco_claims_category_level", table_name="eco_claims")
    op.drop_index("ix_eco_claims_user_status", table_name="eco_claims")
    op.drop_index("ix_eco_claims_user_id", table_name="eco_claims")
    op.drop_index("ix_eco_claims_claim_uid", table_name="eco_claims")
    op.drop_table("eco_claims")
    op.drop_table("eco_treasury_buckets")
    op.execute("DROP TYPE IF EXISTS mintmode")
    op.execute("DROP TYPE IF EXISTS claimstatus")
    op.execute("DROP TYPE IF EXISTS assurancelevel")
    op.execute("DROP TYPE IF EXISTS bucketcode")

"""
EcoCoin core models — local_ledger + future EVM bridge.
Aligned with docs/ECOCOIN_MONETARY_SYSTEM.md and ECOCOIN_IMPACT_STANDARD.md
"""
from __future__ import annotations

import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class BucketCode(str, enum.Enum):
    COMMUNITY = "COMMUNITY"      # A – 55%
    ORG = "ORG"                  # B – 25%
    TREASURY = "TREASURY"        # C – 10%
    SCIENCE = "SCIENCE"          # D – 7%
    FOUNDERS = "FOUNDERS"        # E – 3%


class ClaimStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
    REWARDED = "REWARDED"


class AssuranceLevel(str, enum.Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class MintMode(str, enum.Enum):
    LOCAL_LEDGER = "local_ledger"
    EVM = "evm"


class EcoTreasuryBucket(Base):
    __tablename__ = "eco_treasury_buckets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[BucketCode] = mapped_column(Enum(BucketCode), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    allocation: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)  # total allocated
    remaining: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="active", nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<EcoTreasuryBucket {self.code} remaining={self.remaining}>"


class EcoClaim(Base):
    __tablename__ = "eco_claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(32), nullable=False)  # TREE_PLANT, EDUCATE, ...
    level: Mapped[AssuranceLevel] = mapped_column(Enum(AssuranceLevel), default=AssuranceLevel.L1)
    status: Mapped[ClaimStatus] = mapped_column(Enum(ClaimStatus), default=ClaimStatus.DRAFT)
    title: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evidence_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    geo_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    quality_score: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    reward_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(28, 18), nullable=True)
    verifier_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # extra JSON
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    rewarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    mint_events: Mapped[list["EcoMintEvent"]] = relationship(back_populates="claim")

    __table_args__ = (
        Index("ix_eco_claims_user_status", "user_id", "status"),
        Index("ix_eco_claims_category_level", "category", "level"),
    )


class EcoMintEvent(Base):
    __tablename__ = "eco_mint_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    claim_id: Mapped[Optional[int]] = mapped_column(ForeignKey("eco_claims.id"), nullable=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(28, 18), nullable=False)
    bucket: Mapped[BucketCode] = mapped_column(Enum(BucketCode), nullable=False)
    level: Mapped[Optional[AssuranceLevel]] = mapped_column(Enum(AssuranceLevel), nullable=True)
    mode: Mapped[MintMode] = mapped_column(Enum(MintMode), default=MintMode.LOCAL_LEDGER)
    tx_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ledger_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, unique=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    claim: Mapped[Optional[EcoClaim]] = relationship(back_populates="mint_events")

    __table_args__ = (
        Index("ix_eco_mint_user_created", "user_id", "created_at"),
    )


class EcoBalance(Base):
    """Materialized balance for fast reads. Source of truth is EcoMintEvent sum."""
    __tablename__ = "eco_balances"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(28, 18), default=Decimal("0"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EcoIdempotencyKey(Base):
    __tablename__ = "eco_idempotency_keys"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    result_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

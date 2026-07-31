"""
Phase 2 models — evidence, peer verification, soft caps, verifier profile.
Extends core EcoCoin models; keep FK soft (string claim_uid) for easier SQLite tests.
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
from sqlalchemy.orm import Mapped, mapped_column

from apps.api.models.ecocoin import Base


class EvidenceKind(str, enum.Enum):
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"
    SENSOR = "SENSOR"
    GEO = "GEO"
    OTHER = "OTHER"


class VoteDecision(str, enum.Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


class EcoEvidence(Base):
    """Attached evidence for a claim (photo, doc, sensor snapshot)."""

    __tablename__ = "eco_evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evidence_uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    claim_uid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    kind: Mapped[EvidenceKind] = mapped_column(Enum(EvidenceKind), default=EvidenceKind.PHOTO)
    content_hash: Mapped[str] = mapped_column(String(128), nullable=False)  # sha256
    perceptual_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    storage_uri: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    geo_lat: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    geo_lng: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    anomaly_flags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list
    uploader_id: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_eco_evidence_claim_kind", "claim_uid", "kind"),
        Index("ix_eco_evidence_phash", "perceptual_hash"),
    )


class EcoPeerVote(Base):
    """L2 community / peer confirmation."""

    __tablename__ = "eco_peer_votes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    claim_uid: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    voter_id: Mapped[str] = mapped_column(String(64), nullable=False)
    decision: Mapped[VoteDecision] = mapped_column(Enum(VoteDecision), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    weight: Mapped[Decimal] = mapped_column(Numeric(6, 3), default=Decimal("1.0"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("claim_uid", "voter_id", name="uq_peer_vote_claim_voter"),
        Index("ix_eco_peer_claim", "claim_uid"),
    )


class EcoVerifierProfile(Base):
    """Reputation for peer / staff verifiers."""

    __tablename__ = "eco_verifier_profiles"

    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    role: Mapped[str] = mapped_column(String(32), default="peer")  # peer | staff | expert
    reputation: Mapped[Decimal] = mapped_column(Numeric(8, 3), default=Decimal("1.0"))
    votes_cast: Mapped[int] = mapped_column(Integer, default=0)
    votes_aligned: Mapped[int] = mapped_column(Integer, default=0)  # matched final decision
    is_accredited: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EcoCapLedger(Base):
    """
    Soft daily/weekly claim counters per user+category.
    key format: {user_id}|{period}|{category}  period=YYYY-MM-DD or YYYY-Www
    """

    __tablename__ = "eco_cap_ledger"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    period: Mapped[str] = mapped_column(String(16), nullable=False)
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    count: Mapped[int] = mapped_column(Integer, default=0)
    amount_eco: Mapped[Decimal] = mapped_column(Numeric(28, 18), default=Decimal("0"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

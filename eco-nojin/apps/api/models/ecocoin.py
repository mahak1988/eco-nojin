"""EcoCoin ORM — mint events persisted for audit / oracle trail."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base


def _utcnow() -> datetime:
    return datetime.now(UTC)


class MintEvent(Base):
    __tablename__ = "ecocoin_mint_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tx_hash: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    recipient: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    project_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    credit_type: Mapped[int] = mapped_column(Integer, nullable=False)
    credit_name: Mapped[str] = mapped_column(String(32), nullable=False)
    measured_value: Mapped[float] = mapped_column(Float, nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    region_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    scarcity_factor: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    mint_total: Mapped[float] = mapped_column(Float, nullable=False)
    steward_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    verifier_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    treasury_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    community_share: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    verification_hash: Mapped[str] = mapped_column(String(128), nullable=False, default="")
    oracle_signature: Mapped[str] = mapped_column(Text, nullable=False, default="")
    oracle_payload: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "tx_hash": self.tx_hash,
            "recipient": self.recipient,
            "project_id": self.project_id,
            "credit_type": self.credit_type,
            "credit_name": self.credit_name,
            "measured_value": self.measured_value,
            "quality_score": self.quality_score,
            "region_multiplier": self.region_multiplier,
            "scarcity_factor": self.scarcity_factor,
            "mint_total": self.mint_total,
            "distribution": {
                "steward": self.steward_share,
                "verifier": self.verifier_share,
                "treasury": self.treasury_share,
                "community": self.community_share,
            },
            "verification_hash": self.verification_hash,
            "oracle_signature": self.oracle_signature,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

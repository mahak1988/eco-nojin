"""
Pydantic v2 schemas for EcoCoin API (Phase 1).
English-only field names; messages can be i18n at presentation layer.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssuranceLevelStr(str, Enum):
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"
    L4 = "L4"


class ClaimStatusStr(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    NEEDS_EVIDENCE = "NEEDS_EVIDENCE"
    REWARDED = "REWARDED"


class BucketCodeStr(str, Enum):
    COMMUNITY = "COMMUNITY"
    ORG = "ORG"
    TREASURY = "TREASURY"
    SCIENCE = "SCIENCE"
    FOUNDERS = "FOUNDERS"


# --- Claims ---

ALLOWED_CATEGORIES = frozenset(
    {
        "TREE_PLANT",
        "SOIL_RESTO",
        "WATER_CONS",
        "BIODIV",
        "WASTE_RED",
        "EDUCATE",
        "STEWARD",
    }
)


class ClaimCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    category: str = Field(..., min_length=2, max_length=32)
    level: AssuranceLevelStr = AssuranceLevelStr.L1
    title: Optional[str] = Field(None, max_length=256)
    description: Optional[str] = None
    evidence_hash: Optional[str] = Field(None, max_length=128)
    geo_lat: Optional[Decimal] = Field(None, ge=Decimal("-90"), le=Decimal("90"))
    geo_lng: Optional[Decimal] = Field(None, ge=Decimal("-180"), le=Decimal("180"))
    metadata: Optional[dict[str, Any]] = None
    submit: bool = Field(
        True,
        description="If true, status becomes SUBMITTED; else DRAFT",
    )

    @field_validator("category")
    @classmethod
    def category_allowed(cls, v: str) -> str:
        u = v.upper().strip()
        if u not in ALLOWED_CATEGORIES:
            raise ValueError(f"category must be one of {sorted(ALLOWED_CATEGORIES)}")
        return u


class ClaimVerify(BaseModel):
    action: str = Field(..., description="approve | reject | needs_evidence | reward")
    verifier_id: str = Field(..., min_length=1, max_length=64)
    quality_score: Optional[Decimal] = Field(
        None, ge=Decimal("0.5"), le=Decimal("1.5")
    )
    rejection_reason: Optional[str] = None
    idempotency_key: Optional[str] = Field(None, max_length=128)

    @field_validator("action")
    @classmethod
    def action_ok(cls, v: str) -> str:
        a = v.lower().strip()
        if a not in ("approve", "reject", "needs_evidence", "reward"):
            raise ValueError("action must be approve|reject|needs_evidence|reward")
        return a


class ClaimOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_uid: str
    user_id: str
    category: str
    level: AssuranceLevelStr
    status: ClaimStatusStr
    title: Optional[str] = None
    description: Optional[str] = None
    evidence_hash: Optional[str] = None
    geo_lat: Optional[Decimal] = None
    geo_lng: Optional[Decimal] = None
    quality_score: Optional[Decimal] = None
    reward_amount: Optional[Decimal] = None
    verifier_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    rewarded_at: Optional[datetime] = None


class ClaimListOut(BaseModel):
    data: list[ClaimOut]
    meta: dict[str, Any]


# --- Reward / Mint ---

class RewardRequest(BaseModel):
    """Internal / oracle trigger to mint after verification."""
    user_id: str = Field(..., min_length=1, max_length=64)
    amount: Optional[Decimal] = Field(None, gt=0)
    claim_uid: Optional[str] = None
    category: Optional[str] = None
    level: AssuranceLevelStr = AssuranceLevelStr.L1
    quality_score: Optional[Decimal] = Field(None, ge=Decimal("0.5"), le=Decimal("1.5"))
    idempotency_key: str = Field(..., min_length=8, max_length=128)
    note: Optional[str] = None


class MintEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    event_uid: str
    claim_id: Optional[int] = None
    user_id: str
    amount: Decimal
    bucket: BucketCodeStr
    level: Optional[AssuranceLevelStr] = None
    mode: str
    tx_hash: Optional[str] = None
    ledger_hash: Optional[str] = None
    idempotency_key: Optional[str] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None


# --- Balance & Treasury ---

class BalanceOut(BaseModel):
    user_id: str
    balance: Decimal
    updated_at: Optional[datetime] = None


class BucketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: BucketCodeStr
    name: str
    allocation: Decimal
    remaining: Decimal
    status: str
    description: Optional[str] = None


class TreasuryOut(BaseModel):
    buckets: list[BucketOut]
    total_allocated: Decimal
    total_remaining: Decimal
    mode: str = "local_ledger"


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[Any] = Field(default_factory=list)
    request_id: Optional[str] = None

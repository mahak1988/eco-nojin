"""Phase 2 Pydantic schemas — evidence, peer votes, queue, packages."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EvidenceKindStr(str, Enum):
    PHOTO = "PHOTO"
    DOCUMENT = "DOCUMENT"
    SENSOR = "SENSOR"
    GEO = "GEO"
    OTHER = "OTHER"


class VoteDecisionStr(str, Enum):
    CONFIRM = "CONFIRM"
    REJECT = "REJECT"
    ABSTAIN = "ABSTAIN"


class EvidenceCreate(BaseModel):
    """Metadata path — binary body uploaded separately or base64 in pilot."""

    claim_uid: str
    uploader_id: str
    kind: EvidenceKindStr = EvidenceKindStr.PHOTO
    # Raw content as base64 for pilot (small payloads); production uses multipart + storage_uri
    content_base64: Optional[str] = None
    content_text: Optional[str] = Field(
        None, description="Alternative to base64 for text/sensor JSON"
    )
    storage_uri: Optional[str] = None
    mime_type: Optional[str] = None
    geo_lat: Optional[Decimal] = None
    geo_lng: Optional[Decimal] = None


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evidence_uid: str
    claim_uid: str
    kind: EvidenceKindStr
    content_hash: str
    perceptual_hash: Optional[str] = None
    storage_uri: Optional[str] = None
    mime_type: Optional[str] = None
    size_bytes: Optional[int] = None
    geo_lat: Optional[Decimal] = None
    geo_lng: Optional[Decimal] = None
    anomaly_flags: Optional[list[str]] = None
    uploader_id: str
    created_at: Optional[datetime] = None


class PeerVoteCreate(BaseModel):
    voter_id: str = Field(..., min_length=1, max_length=64)
    decision: VoteDecisionStr
    comment: Optional[str] = None


class PeerVoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_uid: str
    voter_id: str
    decision: VoteDecisionStr
    comment: Optional[str] = None
    weight: Decimal
    created_at: Optional[datetime] = None


class PeerSummaryOut(BaseModel):
    claim_uid: str
    confirm_weight: Decimal
    reject_weight: Decimal
    l2_ready: bool


class QueueListOut(BaseModel):
    data: list[dict[str, Any]]
    meta: dict[str, Any]


class QualityScoreOut(BaseModel):
    claim_uid: str
    quality_score: Decimal
    evidence_count: int
    confirm_weight: Decimal
    anomaly_flag_count: int


class ClaimPackageOut(BaseModel):
    package: dict[str, Any]

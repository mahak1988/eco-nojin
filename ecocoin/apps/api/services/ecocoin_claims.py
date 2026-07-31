"""
Claim lifecycle helpers for Phase 1.
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import (
    AssuranceLevel,
    ClaimStatus,
    EcoClaim,
)
from apps.api.schemas.ecocoin import ClaimCreate


def _uid() -> str:
    return uuid.uuid4().hex


async def create_claim(session: AsyncSession, body: ClaimCreate) -> EcoClaim:
    from apps.api.services import caps as caps_svc

    status = ClaimStatus.SUBMITTED if body.submit else ClaimStatus.DRAFT
    if body.submit:
        await caps_svc.check_claim_allowed(session, body.user_id, body.category)
    meta = json.dumps(body.metadata, ensure_ascii=False) if body.metadata else None
    claim = EcoClaim(
        claim_uid=_uid(),
        user_id=body.user_id,
        category=body.category,
        level=AssuranceLevel(body.level.value),
        status=status,
        title=body.title,
        description=body.description,
        evidence_hash=body.evidence_hash,
        geo_lat=body.geo_lat,
        geo_lng=body.geo_lng,
        metadata_json=meta,
    )
    session.add(claim)
    await session.flush()
    if body.submit:
        await caps_svc.record_claim_submit(session, body.user_id, body.category)
    return claim


async def get_claim_by_uid(session: AsyncSession, claim_uid: str) -> Optional[EcoClaim]:
    r = await session.execute(select(EcoClaim).where(EcoClaim.claim_uid == claim_uid))
    return r.scalar_one_or_none()


async def get_claim_by_id(session: AsyncSession, claim_id: int) -> Optional[EcoClaim]:
    r = await session.execute(select(EcoClaim).where(EcoClaim.id == claim_id))
    return r.scalar_one_or_none()


async def list_claims(
    session: AsyncSession,
    *,
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[EcoClaim], int]:
    page = max(1, page)
    size = min(max(1, size), 100)
    q = select(EcoClaim)
    count_q = select(func.count()).select_from(EcoClaim)
    if user_id:
        q = q.where(EcoClaim.user_id == user_id)
        count_q = count_q.where(EcoClaim.user_id == user_id)
    if status:
        q = q.where(EcoClaim.status == ClaimStatus(status))
        count_q = count_q.where(EcoClaim.status == ClaimStatus(status))
    if category:
        q = q.where(EcoClaim.category == category.upper())
        count_q = count_q.where(EcoClaim.category == category.upper())
    total = (await session.execute(count_q)).scalar() or 0
    q = q.order_by(EcoClaim.id.desc()).offset((page - 1) * size).limit(size)
    rows = (await session.execute(q)).scalars().all()
    return list(rows), int(total)


async def apply_verify(
    session: AsyncSession,
    claim: EcoClaim,
    *,
    action: str,
    verifier_id: str,
    quality_score: Optional[Decimal] = None,
    rejection_reason: Optional[str] = None,
) -> EcoClaim:
    """Update status without minting. Use action=reward via chain adapter separately."""
    if action == "reject":
        claim.status = ClaimStatus.REJECTED
        claim.rejection_reason = rejection_reason or "Rejected by verifier"
        claim.verifier_id = verifier_id
    elif action == "needs_evidence":
        claim.status = ClaimStatus.NEEDS_EVIDENCE
        claim.verifier_id = verifier_id
        claim.rejection_reason = rejection_reason
    elif action == "approve":
        claim.status = ClaimStatus.APPROVED
        claim.verifier_id = verifier_id
        if quality_score is not None:
            claim.quality_score = quality_score
    else:
        raise ValueError(f"Unknown verify action: {action}")
    await session.flush()
    return claim

"""
L2 peer verification — votes, weights, promotion toward approval.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import AssuranceLevel, ClaimStatus, EcoClaim
from apps.api.models.ecocoin_impact import (
    EcoPeerVote,
    EcoVerifierProfile,
    VoteDecision,
)

# Minimum confirm weight to auto-suggest L2 readiness
L2_CONFIRM_THRESHOLD = Decimal("2.0")


async def get_or_create_verifier(
    session: AsyncSession, user_id: str, role: str = "peer"
) -> EcoVerifierProfile:
    r = await session.execute(
        select(EcoVerifierProfile).where(EcoVerifierProfile.user_id == user_id)
    )
    row = r.scalar_one_or_none()
    if row:
        return row
    row = EcoVerifierProfile(user_id=user_id, role=role)
    session.add(row)
    await session.flush()
    return row


async def cast_vote(
    session: AsyncSession,
    *,
    claim: EcoClaim,
    voter_id: str,
    decision: VoteDecision,
    comment: Optional[str] = None,
) -> EcoPeerVote:
    if voter_id == claim.user_id:
        raise ValueError("Claimant cannot peer-verify own claim")
    if claim.status not in (
        ClaimStatus.SUBMITTED,
        ClaimStatus.IN_REVIEW,
        ClaimStatus.NEEDS_EVIDENCE,
    ):
        raise ValueError(f"Cannot vote on claim in status {claim.status}")

    profile = await get_or_create_verifier(session, voter_id)
    weight = profile.reputation if profile.reputation > 0 else Decimal("1.0")

    existing = await session.execute(
        select(EcoPeerVote).where(
            EcoPeerVote.claim_uid == claim.claim_uid,
            EcoPeerVote.voter_id == voter_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("Voter already voted on this claim")

    vote = EcoPeerVote(
        claim_uid=claim.claim_uid,
        voter_id=voter_id,
        decision=decision,
        comment=comment,
        weight=weight,
    )
    session.add(vote)
    profile.votes_cast = (profile.votes_cast or 0) + 1
    if claim.status == ClaimStatus.SUBMITTED:
        claim.status = ClaimStatus.IN_REVIEW
    await session.flush()
    return vote


async def confirm_weight(session: AsyncSession, claim_uid: str) -> Decimal:
    r = await session.execute(
        select(func.coalesce(func.sum(EcoPeerVote.weight), 0)).where(
            EcoPeerVote.claim_uid == claim_uid,
            EcoPeerVote.decision == VoteDecision.CONFIRM,
        )
    )
    return Decimal(str(r.scalar() or 0))


async def reject_weight(session: AsyncSession, claim_uid: str) -> Decimal:
    r = await session.execute(
        select(func.coalesce(func.sum(EcoPeerVote.weight), 0)).where(
            EcoPeerVote.claim_uid == claim_uid,
            EcoPeerVote.decision == VoteDecision.REJECT,
        )
    )
    return Decimal(str(r.scalar() or 0))


async def maybe_promote_level(session: AsyncSession, claim: EcoClaim) -> EcoClaim:
    """If peer confirms >= threshold and level is L1, mark ready for L2 semantics."""
    conf = await confirm_weight(session, claim.claim_uid)
    if conf >= L2_CONFIRM_THRESHOLD and claim.level == AssuranceLevel.L1:
        claim.level = AssuranceLevel.L2
        await session.flush()
    return claim


async def list_queue(
    session: AsyncSession,
    *,
    status: Optional[str] = None,
    level: Optional[str] = None,
    page: int = 1,
    size: int = 20,
) -> tuple[list[EcoClaim], int]:
    page = max(1, page)
    size = min(max(1, size), 100)
    statuses = (
        ClaimStatus.SUBMITTED,
        ClaimStatus.IN_REVIEW,
        ClaimStatus.NEEDS_EVIDENCE,
    )
    q = select(EcoClaim).where(EcoClaim.status.in_(statuses))
    count_q = select(func.count()).select_from(EcoClaim).where(EcoClaim.status.in_(statuses))
    if status:
        q = q.where(EcoClaim.status == ClaimStatus(status))
        count_q = count_q.where(EcoClaim.status == ClaimStatus(status))
    if level:
        q = q.where(EcoClaim.level == AssuranceLevel(level))
        count_q = count_q.where(EcoClaim.level == AssuranceLevel(level))
    total = (await session.execute(count_q)).scalar() or 0
    q = q.order_by(EcoClaim.created_at.asc()).offset((page - 1) * size).limit(size)
    rows = list((await session.execute(q)).scalars().all())
    return rows, int(total)

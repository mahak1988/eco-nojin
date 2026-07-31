"""
EcoCoin reward engine — pure business logic.
Works in local_ledger mode; later bridged to EVM via ecocoin_chain.py.
"""
from __future__ import annotations

import hashlib
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import (
    AssuranceLevel,
    BucketCode,
    ClaimStatus,
    EcoBalance,
    EcoClaim,
    EcoIdempotencyKey,
    EcoMintEvent,
    EcoTreasuryBucket,
    MintMode,
)

# L-level multipliers (from IMPACT_STANDARD)
LEVEL_MULTIPLIER = {
    AssuranceLevel.L1: Decimal("1.0"),
    AssuranceLevel.L2: Decimal("1.5"),
    AssuranceLevel.L3: Decimal("2.5"),
    AssuranceLevel.L4: Decimal("4.0"),
}

# Base reward per category (ECO, whole units — adjust in production)
BASE_REWARD = {
    "TREE_PLANT": Decimal("10"),
    "SOIL_RESTO": Decimal("15"),
    "WATER_CONS": Decimal("12"),
    "BIODIV": Decimal("20"),
    "WASTE_RED": Decimal("5"),
    "EDUCATE": Decimal("3"),
    "STEWARD": Decimal("25"),
}


def _uid() -> str:
    return uuid.uuid4().hex


def _ledger_hash(user_id: str, amount: Decimal, claim_uid: str, event_uid: str) -> str:
    raw = f"{user_id}|{amount}|{claim_uid}|{event_uid}"
    return hashlib.sha256(raw.encode()).hexdigest()


async def get_bucket(session: AsyncSession, code: BucketCode) -> EcoTreasuryBucket:
    result = await session.execute(
        select(EcoTreasuryBucket).where(EcoTreasuryBucket.code == code)
    )
    bucket = result.scalar_one_or_none()
    if not bucket:
        raise ValueError(f"Bucket {code} not found")
    return bucket


async def get_balance(session: AsyncSession, user_id: str) -> Decimal:
    result = await session.execute(
        select(EcoBalance).where(EcoBalance.user_id == user_id)
    )
    row = result.scalar_one_or_none()
    return row.balance if row else Decimal("0")


async def calculate_reward(
    category: str,
    level: AssuranceLevel,
    quality_score: Optional[Decimal] = None,
) -> Decimal:
    base = BASE_REWARD.get(category, Decimal("5"))
    mult = LEVEL_MULTIPLIER.get(level, Decimal("1.0"))
    quality = quality_score if quality_score is not None else Decimal("1.0")
    # quality expected 0.5–1.5 range
    return (base * mult * quality).quantize(Decimal("0.000000000000000001"))


async def mint_reward(
    session: AsyncSession,
    *,
    user_id: str,
    amount: Decimal,
    bucket: BucketCode = BucketCode.COMMUNITY,
    claim: Optional[EcoClaim] = None,
    level: Optional[AssuranceLevel] = None,
    idempotency_key: Optional[str] = None,
    mode: MintMode = MintMode.LOCAL_LEDGER,
    note: Optional[str] = None,
) -> EcoMintEvent:
    """
    Core mint path. Decrements bucket remaining, credits user balance,
    records MintEvent. Idempotent when key is provided.
    """
    if amount <= 0:
        raise ValueError("amount must be positive")

    # Idempotency check
    if idempotency_key:
        existing = await session.execute(
            select(EcoMintEvent).where(EcoMintEvent.idempotency_key == idempotency_key)
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Idempotency key already used: {idempotency_key}")

    treasury = await get_bucket(session, bucket)
    if treasury.remaining < amount:
        raise ValueError(f"Insufficient remaining in bucket {bucket}: {treasury.remaining}")

    event_uid = _uid()
    claim_uid = claim.claim_uid if claim else ""
    ledger = _ledger_hash(user_id, amount, claim_uid, event_uid)

    # Decrement bucket
    treasury.remaining -= amount

    # Upsert balance
    bal_result = await session.execute(
        select(EcoBalance).where(EcoBalance.user_id == user_id)
    )
    bal = bal_result.scalar_one_or_none()
    if bal:
        bal.balance += amount
    else:
        bal = EcoBalance(user_id=user_id, balance=amount)
        session.add(bal)

    event = EcoMintEvent(
        event_uid=event_uid,
        claim_id=claim.id if claim else None,
        user_id=user_id,
        amount=amount,
        bucket=bucket,
        level=level,
        mode=mode,
        ledger_hash=ledger,
        idempotency_key=idempotency_key,
        note=note,
    )
    session.add(event)

    if claim:
        claim.status = ClaimStatus.REWARDED
        claim.reward_amount = amount
        from datetime import datetime, timezone
        claim.rewarded_at = datetime.now(timezone.utc)

    await session.flush()
    return event


async def approve_and_reward(
    session: AsyncSession,
    claim: EcoClaim,
    *,
    quality_score: Optional[Decimal] = None,
    verifier_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> EcoMintEvent:
    """Approve a claim and mint the calculated reward from COMMUNITY bucket."""
    from apps.api.services import caps as caps_svc

    if claim.status not in (ClaimStatus.SUBMITTED, ClaimStatus.IN_REVIEW, ClaimStatus.APPROVED):
        raise ValueError(f"Cannot reward claim in status {claim.status}")

    amount = await calculate_reward(claim.category, claim.level, quality_score)
    await caps_svc.check_reward_allowed(session, claim.user_id, amount)

    claim.status = ClaimStatus.APPROVED
    claim.quality_score = quality_score
    claim.verifier_id = verifier_id

    event = await mint_reward(
        session,
        user_id=claim.user_id,
        amount=amount,
        bucket=BucketCode.COMMUNITY,
        claim=claim,
        level=claim.level,
        idempotency_key=idempotency_key or f"claim:{claim.claim_uid}",
        note=f"Reward for claim {claim.claim_uid}",
    )
    await caps_svc.record_reward(session, claim.user_id, amount)
    return event

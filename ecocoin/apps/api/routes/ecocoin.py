"""
FastAPI router — EcoCoin Phase 1 (local_ledger).
Mount under prefix /api/v1/ecocoin
"""
from __future__ import annotations

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import EcoTreasuryBucket
from apps.api.schemas.ecocoin import (
    BalanceOut,
    BucketOut,
    ClaimCreate,
    ClaimListOut,
    ClaimOut,
    ClaimVerify,
    MintEventOut,
    RewardRequest,
    TreasuryOut,
)
from apps.api.services import ecocoin_chain as chain
from apps.api.services import ecocoin_claims as claims_svc
from apps.api.services import ecocoin_engine as engine

router = APIRouter(prefix="/ecocoin", tags=["ecocoin"])


async def get_db() -> AsyncSession:
    """Override in main app: Depends(get_async_session)."""
    raise RuntimeError("get_db must be overridden by host application")


def request_id(request: Request) -> Optional[str]:
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID")


@router.post("/claims", response_model=ClaimOut, status_code=201)
async def submit_claim(
    body: ClaimCreate,
    session: AsyncSession = Depends(get_db),
):
    claim = await claims_svc.create_claim(session, body)
    await session.commit()
    await session.refresh(claim)
    return ClaimOut.model_validate(claim)


@router.get("/claims", response_model=ClaimListOut)
async def list_claims(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    rows, total = await claims_svc.list_claims(
        session, user_id=user_id, status=status, category=category, page=page, size=size
    )
    pages = (total + size - 1) // size if size else 0
    return ClaimListOut(
        data=[ClaimOut.model_validate(r) for r in rows],
        meta={"total": total, "page": page, "size": size, "pages": pages},
    )


@router.get("/claims/{claim_uid}", response_model=ClaimOut)
async def get_claim(claim_uid: str, session: AsyncSession = Depends(get_db)):
    claim = await claims_svc.get_claim_by_uid(session, claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return ClaimOut.model_validate(claim)


@router.post("/claims/{claim_uid}/verify", response_model=ClaimOut | MintEventOut)
async def verify_claim(
    claim_uid: str,
    body: ClaimVerify,
    session: AsyncSession = Depends(get_db),
):
    claim = await claims_svc.get_claim_by_uid(session, claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    try:
        if body.action == "reward":
            event = await chain.approve_and_settle(
                session,
                claim,
                quality_score=body.quality_score,
                verifier_id=body.verifier_id,
                idempotency_key=body.idempotency_key or f"claim:{claim.claim_uid}",
            )
            await session.commit()
            await session.refresh(event)
            return MintEventOut.model_validate(event)

        await claims_svc.apply_verify(
            session,
            claim,
            action=body.action,
            verifier_id=body.verifier_id,
            quality_score=body.quality_score,
            rejection_reason=body.rejection_reason,
        )
        await session.commit()
        await session.refresh(claim)
        return ClaimOut.model_validate(claim)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except NotImplementedError as e:
        await session.rollback()
        raise HTTPException(status_code=501, detail=str(e)) from e


@router.post("/reward", response_model=MintEventOut)
async def trigger_reward(
    body: RewardRequest,
    session: AsyncSession = Depends(get_db),
    x_idempotency_key: Optional[str] = Header(None, alias="X-Idempotency-Key"),
):
    key = body.idempotency_key or x_idempotency_key
    if not key:
        raise HTTPException(status_code=400, detail="idempotency_key required")

    claim = None
    if body.claim_uid:
        claim = await claims_svc.get_claim_by_uid(session, body.claim_uid)
        if not claim:
            raise HTTPException(status_code=404, detail="Claim not found")

    from apps.api.models.ecocoin import AssuranceLevel

    try:
        if claim is not None:
            event = await chain.approve_and_settle(
                session,
                claim,
                quality_score=body.quality_score,
                idempotency_key=key,
            )
        else:
            level = AssuranceLevel(body.level.value)
            amount = body.amount
            if amount is None:
                amount = await engine.calculate_reward(
                    body.category or "EDUCATE",
                    level,
                    body.quality_score,
                )
            event = await chain.settle_reward(
                session,
                user_id=body.user_id,
                amount=amount,
                level=level,
                idempotency_key=key,
                note=body.note,
            )
        await session.commit()
        await session.refresh(event)
        return MintEventOut.model_validate(event)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e
    except NotImplementedError as e:
        await session.rollback()
        raise HTTPException(status_code=501, detail=str(e)) from e


@router.get("/balance/{user_id}", response_model=BalanceOut)
async def get_balance(user_id: str, session: AsyncSession = Depends(get_db)):
    bal = await engine.get_balance(session, user_id)
    return BalanceOut(user_id=user_id, balance=bal, updated_at=None)


@router.get("/treasury", response_model=TreasuryOut)
async def get_treasury(session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(EcoTreasuryBucket).order_by(EcoTreasuryBucket.id))
    buckets = list(result.scalars().all())
    total_alloc = sum((b.allocation for b in buckets), Decimal("0"))
    total_rem = sum((b.remaining for b in buckets), Decimal("0"))
    return TreasuryOut(
        buckets=[BucketOut.model_validate(b) for b in buckets],
        total_allocated=total_alloc,
        total_remaining=total_rem,
        mode=chain.current_mode().value,
    )

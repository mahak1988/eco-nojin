"""
Phase 2 routes — evidence, peer votes, admin queue, claim package export.
Mount under same /api/v1 prefix; router prefix /ecocoin
"""
from __future__ import annotations

import base64
import json
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin_impact import EvidenceKind, VoteDecision
from apps.api.schemas.ecocoin import ClaimOut
from apps.api.schemas.ecocoin_impact import (
    ClaimPackageOut,
    EvidenceCreate,
    EvidenceOut,
    PeerSummaryOut,
    PeerVoteCreate,
    PeerVoteOut,
    QualityScoreOut,
    QueueListOut,
)
from apps.api.services import evidence as evidence_svc
from apps.api.services import impact_package
from apps.api.services import peer_verify
from apps.api.services import ecocoin_claims as claims_svc

from apps.api.routes.ecocoin import get_db

router = APIRouter(prefix="/ecocoin", tags=["ecocoin-impact"])


def _parse_flags(raw: Optional[str]) -> Optional[list[str]]:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return [raw]


@router.post("/evidence", response_model=EvidenceOut, status_code=201)
async def upload_evidence(body: EvidenceCreate, session: AsyncSession = Depends(get_db)):
    claim = await claims_svc.get_claim_by_uid(session, body.claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    if body.content_base64:
        try:
            data = base64.b64decode(body.content_base64)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64: {e}") from e
    elif body.content_text is not None:
        data = body.content_text.encode("utf-8")
    else:
        data = b""

    if not data and not body.storage_uri:
        raise HTTPException(status_code=400, detail="content or storage_uri required")

    try:
        ev, flags = await evidence_svc.attach_evidence(
            session,
            claim_uid=body.claim_uid,
            uploader_id=body.uploader_id,
            data=data or (body.storage_uri or "").encode(),
            kind=EvidenceKind(body.kind.value),
            mime_type=body.mime_type,
            storage_uri=body.storage_uri,
            geo_lat=body.geo_lat,
            geo_lng=body.geo_lng,
        )
        await session.commit()
        await session.refresh(ev)
        out = EvidenceOut.model_validate(ev)
        out.anomaly_flags = flags or _parse_flags(ev.anomaly_flags)
        return out
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/claims/{claim_uid}/evidence", response_model=list[EvidenceOut])
async def list_evidence(claim_uid: str, session: AsyncSession = Depends(get_db)):
    from apps.api.models.ecocoin_impact import EcoEvidence

    rows = (
        await session.execute(
            select(EcoEvidence).where(EcoEvidence.claim_uid == claim_uid)
        )
    ).scalars().all()
    result = []
    for e in rows:
        o = EvidenceOut.model_validate(e)
        o.anomaly_flags = _parse_flags(e.anomaly_flags)
        result.append(o)
    return result


@router.post("/claims/{claim_uid}/peer-vote", response_model=PeerVoteOut, status_code=201)
async def peer_vote(
    claim_uid: str,
    body: PeerVoteCreate,
    session: AsyncSession = Depends(get_db),
):
    claim = await claims_svc.get_claim_by_uid(session, claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    try:
        vote = await peer_verify.cast_vote(
            session,
            claim=claim,
            voter_id=body.voter_id,
            decision=VoteDecision(body.decision.value),
            comment=body.comment,
        )
        await peer_verify.maybe_promote_level(session, claim)
        await session.commit()
        await session.refresh(vote)
        return PeerVoteOut.model_validate(vote)
    except ValueError as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/claims/{claim_uid}/peer-summary", response_model=PeerSummaryOut)
async def peer_summary(claim_uid: str, session: AsyncSession = Depends(get_db)):
    claim = await claims_svc.get_claim_by_uid(session, claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    conf = await peer_verify.confirm_weight(session, claim_uid)
    rej = await peer_verify.reject_weight(session, claim_uid)
    return PeerSummaryOut(
        claim_uid=claim_uid,
        confirm_weight=conf,
        reject_weight=rej,
        l2_ready=conf >= peer_verify.L2_CONFIRM_THRESHOLD,
    )


@router.get("/admin/verification-queue", response_model=QueueListOut)
async def verification_queue(
    status: Optional[str] = None,
    level: Optional[str] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    rows, total = await peer_verify.list_queue(
        session, status=status, level=level, page=page, size=size
    )
    pages = (total + size - 1) // size if size else 0
    return QueueListOut(
        data=[ClaimOut.model_validate(r).model_dump(mode="json") for r in rows],
        meta={"total": total, "page": page, "size": size, "pages": pages},
    )


@router.get("/claims/{claim_uid}/quality", response_model=QualityScoreOut)
async def compute_quality(claim_uid: str, session: AsyncSession = Depends(get_db)):
    from apps.api.models.ecocoin_impact import EcoEvidence

    claim = await claims_svc.get_claim_by_uid(session, claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    evs = (
        await session.execute(
            select(EcoEvidence).where(EcoEvidence.claim_uid == claim_uid)
        )
    ).scalars().all()
    anomaly_n = 0
    for e in evs:
        if e.anomaly_flags:
            try:
                anomaly_n += len(json.loads(e.anomaly_flags))
            except json.JSONDecodeError:
                anomaly_n += 1
    conf = await peer_verify.confirm_weight(session, claim_uid)
    score = evidence_svc.quality_score_from_evidence(
        evidence_count=len(evs),
        anomaly_flag_count=anomaly_n,
        has_geo=claim.geo_lat is not None,
        peer_confirm_weight=conf,
        level=claim.level.value if claim.level else "L1",
    )
    return QualityScoreOut(
        claim_uid=claim_uid,
        quality_score=score,
        evidence_count=len(evs),
        confirm_weight=conf,
        anomaly_flag_count=anomaly_n,
    )


@router.get("/claims/{claim_uid}/package", response_model=ClaimPackageOut)
async def export_package(claim_uid: str, session: AsyncSession = Depends(get_db)):
    claim = await claims_svc.get_claim_by_uid(session, claim_uid)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    pkg = await impact_package.build_claim_package(session, claim)
    return ClaimPackageOut(package=pkg)

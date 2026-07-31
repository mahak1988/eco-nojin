"""
Export claim package for L3/L4 (methodology-ready JSON).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import EcoClaim, EcoMintEvent
from apps.api.models.ecocoin_impact import EcoEvidence, EcoPeerVote
from apps.api.services import peer_verify


async def build_claim_package(session: AsyncSession, claim: EcoClaim) -> dict[str, Any]:
    ev_rows = (
        await session.execute(
            select(EcoEvidence).where(EcoEvidence.claim_uid == claim.claim_uid)
        )
    ).scalars().all()
    votes = (
        await session.execute(
            select(EcoPeerVote).where(EcoPeerVote.claim_uid == claim.claim_uid)
        )
    ).scalars().all()
    mints = (
        await session.execute(
            select(EcoMintEvent).where(EcoMintEvent.claim_id == claim.id)
        )
    ).scalars().all()

    conf = await peer_verify.confirm_weight(session, claim.claim_uid)
    rej = await peer_verify.reject_weight(session, claim.claim_uid)

    package = {
        "schema": "econojin.ecocoin.claim_package.v1",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "disclaimer": (
            "Educational–scientific pilot package. Not a carbon credit. "
            "No registry claim. For PES/CSR evidence support only when independently verified."
        ),
        "claim": {
            "claim_uid": claim.claim_uid,
            "user_id": claim.user_id,
            "category": claim.category,
            "level": claim.level.value if claim.level else None,
            "status": claim.status.value if claim.status else None,
            "title": claim.title,
            "description": claim.description,
            "evidence_hash": claim.evidence_hash,
            "geo": {"lat": _dec(claim.geo_lat), "lng": _dec(claim.geo_lng)},
            "quality_score": _dec(claim.quality_score),
            "reward_amount": _dec(claim.reward_amount),
            "verifier_id": claim.verifier_id,
            "created_at": claim.created_at.isoformat() if claim.created_at else None,
            "rewarded_at": claim.rewarded_at.isoformat() if claim.rewarded_at else None,
        },
        "peer_summary": {
            "confirm_weight": str(conf),
            "reject_weight": str(rej),
        },
        "evidence": [
            {
                "evidence_uid": e.evidence_uid,
                "kind": e.kind.value if e.kind else None,
                "content_hash": e.content_hash,
                "perceptual_hash": e.perceptual_hash,
                "storage_uri": e.storage_uri,
                "mime_type": e.mime_type,
                "size_bytes": e.size_bytes,
                "geo": {"lat": _dec(e.geo_lat), "lng": _dec(e.geo_lng)},
                "anomaly_flags": json.loads(e.anomaly_flags) if e.anomaly_flags else [],
                "uploader_id": e.uploader_id,
            }
            for e in ev_rows
        ],
        "peer_votes": [
            {
                "voter_id": v.voter_id,
                "decision": v.decision.value if v.decision else None,
                "weight": str(v.weight),
                "comment": v.comment,
            }
            for v in votes
        ],
        "mint_events": [
            {
                "event_uid": m.event_uid,
                "amount": str(m.amount),
                "bucket": m.bucket.value if m.bucket else None,
                "ledger_hash": m.ledger_hash,
                "mode": m.mode.value if m.mode else None,
            }
            for m in mints
        ],
        "methodology_notes": {
            "L1": "Self-declared + photo / geo",
            "L2": "Peer confirm weight >= 2.0 recommended",
            "L3": "Expert visit or remote-sensing cross-check required beyond this package",
            "L4": "Quantitative dMRV + optional third-party audit required",
        },
    }
    return package


def _dec(v: Decimal | None) -> float | None:
    if v is None:
        return None
    return float(v)

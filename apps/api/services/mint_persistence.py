"""Persist mint events to SQLite/Postgres via AsyncSession."""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import MintEvent
from apps.api.services.oracle_sign import sign_mint_payload

logger = logging.getLogger(__name__)


async def persist_mint_event(
    session: AsyncSession,
    *,
    tx_hash: str,
    recipient: str,
    project_id: str,
    credit_type: int,
    credit_name: str,
    measured_value: float,
    quality_score: float,
    region_multiplier: float,
    scarcity_factor: float,
    mint_total: float,
    distribution: dict[str, float],
    verification_hash: str,
) -> MintEvent:
    sign_body = {
        "tx_hash": tx_hash,
        "recipient": recipient,
        "project_id": project_id,
        "credit_type": credit_type,
        "measured_value": measured_value,
        "quality_score": quality_score,
        "mint_total": mint_total,
        "verification_hash": verification_hash,
    }
    signed = sign_mint_payload(sign_body)
    row = MintEvent(
        tx_hash=tx_hash,
        recipient=recipient,
        project_id=project_id,
        credit_type=credit_type,
        credit_name=credit_name,
        measured_value=measured_value,
        quality_score=quality_score,
        region_multiplier=region_multiplier,
        scarcity_factor=scarcity_factor,
        mint_total=mint_total,
        steward_share=float(distribution.get("steward", 0.0)),
        verifier_share=float(distribution.get("verifier", 0.0)),
        treasury_share=float(distribution.get("treasury", 0.0)),
        community_share=float(distribution.get("community", 0.0)),
        verification_hash=verification_hash,
        oracle_signature=signed["signature"],
        oracle_payload=signed["payload"],
    )
    session.add(row)
    await session.flush()
    return row


async def list_mint_events(
    session: AsyncSession,
    *,
    limit: int = 20,
    recipient: str | None = None,
) -> list[dict[str, Any]]:
    q = select(MintEvent).order_by(MintEvent.id.desc()).limit(limit)
    if recipient:
        q = q.where(MintEvent.recipient == recipient)
    result = await session.execute(q)
    rows = result.scalars().all()
    return [r.to_dict() for r in rows]

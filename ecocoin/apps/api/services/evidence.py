"""
Evidence helpers — content hash + lightweight perceptual fingerprint.
No external image library required (pilot-safe).
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin_impact import EcoEvidence, EvidenceKind


def content_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def perceptual_hash_bytes(data: bytes, blocks: int = 16) -> str:
    """
    Structural fingerprint: average intensity of fixed blocks of the byte stream.
    Not a full pHash, but stable for duplicate / near-duplicate detection in pilot.
    """
    if not data:
        return "0" * 16
    n = max(1, len(data) // blocks)
    parts: list[str] = []
    for i in range(blocks):
        chunk = data[i * n : (i + 1) * n] or data[-n:]
        avg = sum(chunk) // max(1, len(chunk))
        parts.append(f"{avg:02x}")
    return "".join(parts)[:32]


def hamming_distance_hex(a: str, b: str) -> int:
    """Approximate distance on hex fingerprints (nibble-wise)."""
    a, b = a.ljust(32, "0"), b.ljust(32, "0")
    dist = 0
    for x, y in zip(a, b):
        if x != y:
            dist += 1
    return dist


async def find_similar_evidence(
    session: AsyncSession,
    perceptual_hash: str,
    *,
    max_distance: int = 4,
    limit: int = 5,
) -> list[EcoEvidence]:
    """Scan recent evidence for near-duplicate pHash (pilot: load candidates)."""
    result = await session.execute(
        select(EcoEvidence)
        .where(EcoEvidence.perceptual_hash.isnot(None))
        .order_by(EcoEvidence.id.desc())
        .limit(500)
    )
    out: list[EcoEvidence] = []
    for row in result.scalars().all():
        if row.perceptual_hash and hamming_distance_hex(perceptual_hash, row.perceptual_hash) <= max_distance:
            out.append(row)
            if len(out) >= limit:
                break
    return out


async def attach_evidence(
    session: AsyncSession,
    *,
    claim_uid: str,
    uploader_id: str,
    data: bytes,
    kind: EvidenceKind = EvidenceKind.PHOTO,
    mime_type: Optional[str] = None,
    storage_uri: Optional[str] = None,
    geo_lat: Optional[Decimal] = None,
    geo_lng: Optional[Decimal] = None,
    captured_at: Optional[datetime] = None,
) -> tuple[EcoEvidence, list[str]]:
    """
    Store evidence metadata + hashes. Returns (evidence, anomaly_flags).
    """
    flags: list[str] = []
    c_hash = content_sha256(data)
    p_hash = perceptual_hash_bytes(data)

    existing = await session.execute(
        select(EcoEvidence).where(
            EcoEvidence.claim_uid == claim_uid,
            EcoEvidence.content_hash == c_hash,
        )
    )
    if existing.scalar_one_or_none():
        flags.append("duplicate_content_on_claim")

    similar = await find_similar_evidence(session, p_hash)
    cross = [s for s in similar if s.claim_uid != claim_uid]
    if cross:
        flags.append(f"near_duplicate_phash:{cross[0].claim_uid}")

    if len(data) < 100:
        flags.append("suspiciously_small_payload")

    ev = EcoEvidence(
        evidence_uid=uuid.uuid4().hex,
        claim_uid=claim_uid,
        kind=kind,
        content_hash=c_hash,
        perceptual_hash=p_hash,
        storage_uri=storage_uri,
        mime_type=mime_type,
        size_bytes=len(data),
        geo_lat=geo_lat,
        geo_lng=geo_lng,
        captured_at=captured_at or datetime.now(timezone.utc),
        anomaly_flags=json.dumps(flags) if flags else None,
        uploader_id=uploader_id,
    )
    session.add(ev)
    await session.flush()
    return ev, flags


def quality_score_from_evidence(
    evidence_count: int,
    anomaly_flag_count: int,
    has_geo: bool,
    peer_confirm_weight: Decimal,
    level: str,
) -> Decimal:
    """
    Heuristic quality in [0.5, 1.5] for reward multiplier.
    """
    base = Decimal("0.85")
    if evidence_count >= 1:
        base += Decimal("0.05")
    if evidence_count >= 3:
        base += Decimal("0.05")
    if has_geo:
        base += Decimal("0.05")
    if peer_confirm_weight >= Decimal("2.0"):
        base += Decimal("0.10")
    if level in ("L3", "L4"):
        base += Decimal("0.05")
    base -= Decimal("0.08") * min(anomaly_flag_count, 3)
    if base < Decimal("0.5"):
        base = Decimal("0.5")
    if base > Decimal("1.5"):
        base = Decimal("1.5")
    return base.quantize(Decimal("0.01"))

"""
Phase 4 — Oracle settlement worker (batch / single claim).

Signs EIP-712 payloads when ECOCOIN_ORACLE_KEY is set; otherwise records
pending settlements for later. Safe for local_ledger dual-write mode.
"""
from __future__ import annotations

import hashlib
import logging
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

from apps.api.services import ecocoin_evm as evm

logger = logging.getLogger("econojin.ecocoin.oracle")


def build_settlement_job(
    *,
    claim_uid: str,
    beneficiary: str,
    amount: Decimal,
    level: str,
    content_parts: list[str],
    deadline_hours: int = 24,
    nonce: int = 0,
) -> dict[str, Any]:
    deadline = int(
        (datetime.now(timezone.utc) + timedelta(hours=deadline_hours)).timestamp()
    )
    payload = evm.settle_payload(
        claim_uid=claim_uid,
        beneficiary=beneficiary,
        amount=amount,
        level=level,
        content_parts=content_parts,
        deadline_ts=deadline,
        nonce=nonce,
    )
    job = {
        "claim_uid": claim_uid,
        "beneficiary": beneficiary,
        "amount": str(amount),
        "level": level,
        "deadline": deadline,
        "eip712": payload,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return job


def try_sign_eip712(payload: dict[str, Any]) -> Optional[str]:
    """
    Return hex signature if eth_account + ECOCOIN_ORACLE_KEY available.
    """
    key = os.getenv("ECOCOIN_ORACLE_KEY")
    if not key:
        logger.info("ECOCOIN_ORACLE_KEY not set — leave settlement unsigned")
        return None
    try:
        from eth_account import Account  # type: ignore
        from eth_account.messages import encode_typed_data  # type: ignore
    except ImportError:
        logger.warning("eth_account not installed — cannot sign")
        return None

    try:
        structured = {
            "types": payload["types"],
            "primaryType": payload["primaryType"],
            "domain": payload["domain"],
            "message": payload["message"],
        }
        signable = encode_typed_data(full_message=structured)
        signed = Account.from_key(key).sign_message(signable)
        return signed.signature.hex()
    except Exception as e:
        logger.exception("EIP-712 sign failed: %s", e)
        return None


def process_settlement_job(job: dict[str, Any]) -> dict[str, Any]:
    """
    Attempt sign; mark ready_for_chain or awaiting_key.
    Does not broadcast unless ECOCOIN_MODE=evm and RPC configured (see ecocoin_evm).
    """
    sig = try_sign_eip712(job["eip712"])
    out = dict(job)
    if sig:
        out["signature"] = sig
        out["status"] = "signed"
        out["signed_at"] = datetime.now(timezone.utc).isoformat()
    else:
        out["status"] = "awaiting_oracle_key"
    raw = f"{job['claim_uid']}|{job['beneficiary']}|{job['amount']}"
    out["job_id"] = hashlib.sha256(raw.encode()).hexdigest()[:24]
    return out


async def enqueue_after_reward(
    *,
    claim_uid: str,
    beneficiary_address: str,
    amount: Decimal,
    level: str,
    evidence_hash: str = "",
) -> dict[str, Any]:
    """Call from reward path when ECOCOIN_MODE=evm to queue oracle work."""
    job = build_settlement_job(
        claim_uid=claim_uid,
        beneficiary=beneficiary_address,
        amount=amount,
        level=level,
        content_parts=[claim_uid, evidence_hash or "none"],
    )
    return process_settlement_job(job)

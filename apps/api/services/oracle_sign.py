"""
Oracle signature for EcoCoin mint previews / events.

Local / CI: HMAC-SHA256 with ECOCOIN_ORACLE_SECRET (or deterministic dev secret).
Production path can swap to RSA/ECDSA without changing call sites.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from typing import Any


def _secret() -> bytes:
    raw = (os.getenv("ECOCOIN_ORACLE_SECRET") or "econojin-dev-oracle-not-for-prod").encode(
        "utf-8"
    )
    return raw


def canonical_payload(data: dict[str, Any]) -> str:
    """Stable JSON for signing (sorted keys, no whitespace noise)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def sign_mint_payload(payload: dict[str, Any]) -> dict[str, str]:
    body = canonical_payload(payload)
    sig = hmac.new(_secret(), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "algorithm": "HMAC-SHA256",
        "payload": body,
        "signature": "0x" + sig,
    }


def verify_mint_signature(payload: dict[str, Any], signature: str) -> bool:
    expected = sign_mint_payload(payload)["signature"]
    got = signature if signature.startswith("0x") else "0x" + signature
    return hmac.compare_digest(expected, got)

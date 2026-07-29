"""
Oracle signature for EcoCoin mint previews / events.

Default: HMAC-SHA256 (ECOCOIN_ORACLE_SECRET).
Optional RSA: set ECOCOIN_ORACLE_PRIVATE_PEM path to a PEM file (PKCS8).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any


def _secret() -> bytes:
    return (os.getenv("ECOCOIN_ORACLE_SECRET") or "econojin-dev-oracle-not-for-prod").encode(
        "utf-8"
    )


def canonical_payload(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)


def _sign_rsa(body: str) -> dict[str, str] | None:
    pem_path = (os.getenv("ECOCOIN_ORACLE_PRIVATE_PEM") or "").strip()
    if not pem_path or not Path(pem_path).is_file():
        return None
    try:
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        key = serialization.load_pem_private_key(
            Path(pem_path).read_bytes(),
            password=None,
            backend=default_backend(),
        )
        sig = key.sign(
            body.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return {
            "algorithm": "RSA-SHA256-PKCS1v15",
            "payload": body,
            "signature": "0x" + base64.b64encode(sig).hex(),
        }
    except Exception:
        return None


def sign_mint_payload(payload: dict[str, Any]) -> dict[str, str]:
    body = canonical_payload(payload)
    rsa = _sign_rsa(body)
    if rsa is not None:
        return rsa
    sig = hmac.new(_secret(), body.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "algorithm": "HMAC-SHA256",
        "payload": body,
        "signature": "0x" + sig,
    }


def verify_mint_signature(payload: dict[str, Any], signature: str) -> bool:
    """Verify HMAC signatures only (RSA verify needs public key — separate endpoint later)."""
    body = canonical_payload(payload)
    expected = "0x" + hmac.new(_secret(), body.encode("utf-8"), hashlib.sha256).hexdigest()
    got = signature if signature.startswith("0x") else "0x" + signature
    return hmac.compare_digest(expected, got)

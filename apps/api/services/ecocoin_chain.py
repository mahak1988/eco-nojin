"""EcoCoin chain bridge — local ledger + optional EVM RPC (when configured)."""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timezone
from typing import Any

# In-process append-only ledger (simulates L2 / sidechain until RPC is set)
_LEDGER: list[dict[str, Any]] = []


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


def chain_config() -> dict[str, Any]:
    rpc = _env("ECOCOIN_RPC_URL")
    addr = _env("ECOCOIN_CONTRACT_ADDRESS")
    chain_id = _env("ECOCOIN_CHAIN_ID", "31337")
    mode = "evm" if rpc and addr else "local_ledger"
    return {
        "mode": mode,
        "rpc_url": rpc or None,
        "contract_address": addr or None,
        "chain_id": int(chain_id) if str(chain_id).isdigit() else chain_id,
        "abi_note": "contracts/contracts/EcoCoin.sol (mint/stake/transfer)",
        "ledger_depth": len(_LEDGER),
    }


def ledger_append(
    action: str,
    *parts: Any,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw = "|".join(str(p) for p in (action, *parts, datetime.now(timezone.utc).isoformat()))
    h = "0x" + hashlib.sha256(raw.encode()).hexdigest()
    entry = {
        "tx_hash": h,
        "action": action,
        "parts": [str(p) for p in parts],
        "meta": meta or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": chain_config()["mode"],
        "block_index": len(_LEDGER) + 1,
    }
    _LEDGER.insert(0, entry)
    # Cap memory
    if len(_LEDGER) > 500:
        del _LEDGER[500:]
    return entry


def ledger_recent(limit: int = 20) -> list[dict[str, Any]]:
    return _LEDGER[: max(1, min(limit, 100))]


def try_evm_mint_stub(recipient: str, amount_wei_hint: float) -> dict[str, Any]:
    """When RPC+contract set, callers can extend with web3; default records intent."""
    cfg = chain_config()
    if cfg["mode"] != "evm":
        return {"submitted": False, "reason": "local_ledger_only"}
    # Real web3 submission requires private key + ABI encode — keep safe stub
    return {
        "submitted": False,
        "reason": "rpc_configured_but_server_signer_disabled",
        "hint": "Set ECOCOIN_ORACLE_PRIVATE_KEY in production to enable oracle mint",
        "contract": cfg["contract_address"],
        "recipient": recipient,
        "amount_hint": amount_wei_hint,
    }

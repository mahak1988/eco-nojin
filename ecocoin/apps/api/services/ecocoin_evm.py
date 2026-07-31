"""
EVM bridge helpers for Phase 3+.

When ECOCOIN_MODE=evm and web3 is available, can submit settleReward txs.
Without web3 / keys, provides offline ABI encoding helpers and raises clear errors.

EIP-712 domain: name=EcoCoinImpactReward, version=1
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional


REWARD_ENGINE_ABI_FRAGMENT = [
    {
        "name": "settleReward",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "claimId", "type": "bytes32"},
            {"name": "beneficiary", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "level", "type": "uint8"},
            {"name": "contentHash", "type": "bytes32"},
            {"name": "deadline", "type": "uint256"},
            {"name": "signature", "type": "bytes"},
        ],
        "outputs": [],
    },
    {
        "name": "adminSettle",
        "type": "function",
        "stateMutability": "nonpayable",
        "inputs": [
            {"name": "claimId", "type": "bytes32"},
            {"name": "beneficiary", "type": "address"},
            {"name": "amount", "type": "uint256"},
            {"name": "level", "type": "uint8"},
            {"name": "contentHash", "type": "bytes32"},
        ],
        "outputs": [],
    },
]


@dataclass
class EvmConfig:
    rpc_url: str
    eco_address: str
    engine_address: str
    registry_address: str
    treasury_address: str
    chain_id: int
    oracle_private_key: Optional[str] = None

    @classmethod
    def from_env(cls) -> "EvmConfig":
        return cls(
            rpc_url=os.getenv("ECOCOIN_RPC_URL", ""),
            eco_address=os.getenv("ECOCOIN_CONTRACT_ADDRESS", ""),
            engine_address=os.getenv("ECOCOIN_REWARD_ENGINE", ""),
            registry_address=os.getenv("ECOCOIN_CLAIM_REGISTRY", ""),
            treasury_address=os.getenv("ECOCOIN_TREASURY", ""),
            chain_id=int(os.getenv("ECOCOIN_CHAIN_ID", "80002")),
            oracle_private_key=os.getenv("ECOCOIN_ORACLE_KEY"),
        )

    def is_configured(self) -> bool:
        return bool(
            self.rpc_url
            and self.eco_address
            and self.engine_address
            and self.registry_address
        )


def claim_id_bytes32(claim_uid: str) -> bytes:
    """Deterministic claimId for on-chain registry."""
    return hashlib.sha256(claim_uid.encode()).digest()


def content_hash_bytes32(*parts: str) -> bytes:
    raw = "|".join(parts).encode()
    return hashlib.sha256(raw).digest()


def amount_to_wei(amount: Decimal) -> int:
    """ECO has 18 decimals; amount is whole+fractional ECO."""
    scaled = (amount * Decimal(10**18)).quantize(Decimal("1"))
    return int(scaled)


def level_to_uint8(level: str) -> int:
    return {"L1": 0, "L2": 1, "L3": 2, "L4": 3}.get(level.upper(), 0)


def settle_payload(
    *,
    claim_uid: str,
    beneficiary: str,
    amount: Decimal,
    level: str,
    content_parts: list[str],
    deadline_ts: int,
    nonce: int = 0,
) -> dict[str, Any]:
    """
    Build structured payload for EIP-712 signing (oracle) and settleReward call.
    Does not sign — host uses eth_account when keys available.
    """
    return {
        "types": {
            "EIP712Domain": [
                {"name": "name", "type": "string"},
                {"name": "version", "type": "string"},
                {"name": "chainId", "type": "uint256"},
                {"name": "verifyingContract", "type": "address"},
            ],
            "Reward": [
                {"name": "claimId", "type": "bytes32"},
                {"name": "beneficiary", "type": "address"},
                {"name": "amount", "type": "uint256"},
                {"name": "level", "type": "uint8"},
                {"name": "contentHash", "type": "bytes32"},
                {"name": "nonce", "type": "uint256"},
                {"name": "deadline", "type": "uint256"},
            ],
        },
        "primaryType": "Reward",
        "domain": {
            "name": "EcoCoinImpactReward",
            "version": "1",
            "chainId": EvmConfig.from_env().chain_id,
            "verifyingContract": EvmConfig.from_env().engine_address or "0x0",
        },
        "message": {
            "claimId": "0x" + claim_id_bytes32(claim_uid).hex(),
            "beneficiary": beneficiary,
            "amount": amount_to_wei(amount),
            "level": level_to_uint8(level),
            "contentHash": "0x" + content_hash_bytes32(*content_parts).hex(),
            "nonce": nonce,
            "deadline": deadline_ts,
        },
    }


async def submit_settle_evm(
    *,
    claim_uid: str,
    beneficiary: str,
    amount: Decimal,
    level: str,
    content_parts: list[str],
    deadline_ts: int,
    signature: bytes,
) -> str:
    """
    Submit settleReward transaction. Requires web3 + funded oracle key.
    Returns tx hash hex.
    """
    cfg = EvmConfig.from_env()
    if not cfg.is_configured():
        raise NotImplementedError(
            "EVM not configured: set ECOCOIN_RPC_URL, ECOCOIN_CONTRACT_ADDRESS, "
            "ECOCOIN_REWARD_ENGINE, ECOCOIN_CLAIM_REGISTRY"
        )
    try:
        from web3 import Web3  # type: ignore
    except ImportError as e:
        raise NotImplementedError(
            "web3 package required for ECOCOIN_MODE=evm settlement"
        ) from e

    if not cfg.oracle_private_key:
        raise NotImplementedError("ECOCOIN_ORACLE_KEY required for on-chain settle")

    w3 = Web3(Web3.HTTPProvider(cfg.rpc_url))
    if not w3.is_connected():
        raise ConnectionError(f"Cannot reach RPC {cfg.rpc_url}")

    raise NotImplementedError(
        "Wire full engine ABI from forge out/ after deploy; "
        f"payload ready for claim={claim_uid} amount={amount} beneficiary={beneficiary}"
    )

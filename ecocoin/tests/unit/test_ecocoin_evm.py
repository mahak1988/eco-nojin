"""Unit tests for EVM payload helpers (no RPC required)."""
from decimal import Decimal

from apps.api.services import ecocoin_evm as evm


def test_claim_id_stable():
    a = evm.claim_id_bytes32("abc")
    b = evm.claim_id_bytes32("abc")
    assert a == b
    assert len(a) == 32
    assert a != evm.claim_id_bytes32("abd")


def test_amount_to_wei():
    assert evm.amount_to_wei(Decimal("1")) == 10**18
    assert evm.amount_to_wei(Decimal("10.5")) == 105 * 10**17


def test_level_map():
    assert evm.level_to_uint8("L1") == 0
    assert evm.level_to_uint8("L4") == 3


def test_settle_payload_structure():
    p = evm.settle_payload(
        claim_uid="c1",
        beneficiary="0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
        amount=Decimal("12"),
        level="L2",
        content_parts=["photo", "32.6", "51.6"],
        deadline_ts=1_900_000_000,
        nonce=0,
    )
    assert p["primaryType"] == "Reward"
    assert p["domain"]["name"] == "EcoCoinImpactReward"
    assert p["message"]["amount"] == 12 * 10**18
    assert p["message"]["level"] == 1
    assert p["message"]["claimId"].startswith("0x")

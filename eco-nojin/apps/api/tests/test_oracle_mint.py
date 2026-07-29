"""Oracle sign + mint payload unit tests (no DB required)."""

from apps.api.services.ecocoin_engine import CREDIT_FACTORS, compute_impact_mint
from apps.api.services.oracle_sign import sign_mint_payload, verify_mint_signature


def test_oracle_sign_roundtrip():
    payload = {
        "tx_hash": "0xabc",
        "recipient": "0x1",
        "project_id": "p1",
        "credit_type": 0,
        "measured_value": 40.0,
        "quality_score": 1.0,
        "mint_total": 1000.0,
        "verification_hash": "vh",
    }
    signed = sign_mint_payload(payload)
    assert signed["signature"].startswith("0x")
    assert verify_mint_signature(payload, signed["signature"]) is True
    assert verify_mint_signature(payload, "0xdead") is False


def test_water_and_biodiversity_credit_factors():
    assert 1 in CREDIT_FACTORS and CREDIT_FACTORS[1][0] == "water"
    assert 3 in CREDIT_FACTORS and CREDIT_FACTORS[3][0] == "biodiversity"
    w = compute_impact_mint(1, measured_value=1000.0, quality_score=1.0)
    assert w["ok"] and w["credit_name"] == "water"
    b = compute_impact_mint(3, measured_value=50.0, quality_score=1.0)
    assert b["ok"] and b["credit_name"] == "biodiversity"

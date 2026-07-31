"""
Unit tests for EcoCoin reward engine (no DB required for pure calc).
"""
from decimal import Decimal

import pytest

from apps.api.models.ecocoin import AssuranceLevel
from apps.api.services.ecocoin_engine import (
    BASE_REWARD,
    LEVEL_MULTIPLIER,
    _ledger_hash,
    calculate_reward,
)


@pytest.mark.asyncio
async def test_calculate_reward_l1_tree():
    amt = await calculate_reward("TREE_PLANT", AssuranceLevel.L1, Decimal("1.0"))
    assert amt == BASE_REWARD["TREE_PLANT"] * LEVEL_MULTIPLIER[AssuranceLevel.L1]


@pytest.mark.asyncio
async def test_calculate_reward_l4_quality():
    amt = await calculate_reward("BIODIV", AssuranceLevel.L4, Decimal("1.2"))
    expected = (BASE_REWARD["BIODIV"] * LEVEL_MULTIPLIER[AssuranceLevel.L4] * Decimal("1.2"))
    assert amt == expected.quantize(Decimal("0.000000000000000001"))


@pytest.mark.asyncio
async def test_unknown_category_default():
    amt = await calculate_reward("UNKNOWN_X", AssuranceLevel.L1)
    assert amt == Decimal("5")


def test_ledger_hash_stable():
    a = _ledger_hash("u1", Decimal("10"), "c1", "e1")
    b = _ledger_hash("u1", Decimal("10"), "c1", "e1")
    assert a == b
    assert len(a) == 64
    c = _ledger_hash("u1", Decimal("11"), "c1", "e1")
    assert a != c

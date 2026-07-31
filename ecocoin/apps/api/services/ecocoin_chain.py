"""
EcoCoin chain adapter — local_ledger (default) vs EVM bridge (Phase 3+).
"""
from __future__ import annotations

import os
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin import EcoClaim, EcoMintEvent, MintMode
from apps.api.services import ecocoin_engine as engine


def current_mode() -> MintMode:
    raw = (os.getenv("ECOCOIN_MODE") or "local_ledger").strip().lower()
    if raw in ("evm", "onchain", "chain"):
        return MintMode.EVM
    return MintMode.LOCAL_LEDGER


async def settle_reward(
    session: AsyncSession,
    *,
    user_id: str,
    amount: Decimal,
    claim: Optional[EcoClaim] = None,
    level=None,
    idempotency_key: Optional[str] = None,
    note: Optional[str] = None,
) -> EcoMintEvent:
    mode = current_mode()
    if mode == MintMode.EVM:
        event = await engine.mint_reward(
            session,
            user_id=user_id,
            amount=amount,
            claim=claim,
            level=level,
            idempotency_key=idempotency_key,
            mode=MintMode.EVM,
            note=(note or "") + " [evm-pending]",
        )
        try:
            from apps.api.services import ecocoin_evm as evm

            cfg = evm.EvmConfig.from_env()
            if not cfg.is_configured():
                event.note = (event.note or "") + " [evm-not-configured-ledger-only]"
        except Exception:
            pass
        return event

    return await engine.mint_reward(
        session,
        user_id=user_id,
        amount=amount,
        claim=claim,
        level=level,
        idempotency_key=idempotency_key,
        mode=MintMode.LOCAL_LEDGER,
        note=note,
    )


async def approve_and_settle(
    session: AsyncSession,
    claim: EcoClaim,
    *,
    quality_score=None,
    verifier_id: Optional[str] = None,
    idempotency_key: Optional[str] = None,
) -> EcoMintEvent:
    mode = current_mode()
    event = await engine.approve_and_reward(
        session,
        claim,
        quality_score=quality_score,
        verifier_id=verifier_id,
        idempotency_key=idempotency_key,
    )
    if mode == MintMode.EVM:
        event.mode = MintMode.EVM
        event.note = (event.note or "") + " [evm-pending-settlement]"
    return event

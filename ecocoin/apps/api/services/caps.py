"""
Soft daily / weekly claim and reward caps (anti-fraud).
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.ecocoin_impact import EcoCapLedger

# Soft limits (pilot — tunable via env later)
DAILY_CLAIMS_PER_CATEGORY = 5
WEEKLY_CLAIMS_PER_CATEGORY = 20
DAILY_ECO_PER_USER = Decimal("200")
WEEKLY_ECO_PER_USER = Decimal("800")


def _day_key(d: Optional[date] = None) -> str:
    d = d or datetime.now(timezone.utc).date()
    return d.isoformat()


def _week_key(d: Optional[date] = None) -> str:
    d = d or datetime.now(timezone.utc).date()
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


async def _get_or_create(
    session: AsyncSession, user_id: str, period: str, category: str
) -> EcoCapLedger:
    key = f"{user_id}|{period}|{category}"
    r = await session.execute(select(EcoCapLedger).where(EcoCapLedger.key == key))
    row = r.scalar_one_or_none()
    if row:
        return row
    row = EcoCapLedger(
        key=key,
        user_id=user_id,
        period=period,
        category=category,
        count=0,
        amount_eco=Decimal("0"),
    )
    session.add(row)
    await session.flush()
    return row


async def check_claim_allowed(
    session: AsyncSession, user_id: str, category: str
) -> None:
    """Raise ValueError if soft claim caps exceeded."""
    day = await _get_or_create(session, user_id, _day_key(), category)
    week = await _get_or_create(session, user_id, _week_key(), category)
    if day.count >= DAILY_CLAIMS_PER_CATEGORY:
        raise ValueError(
            f"Daily claim cap reached for {category} ({DAILY_CLAIMS_PER_CATEGORY})"
        )
    if week.count >= WEEKLY_CLAIMS_PER_CATEGORY:
        raise ValueError(
            f"Weekly claim cap reached for {category} ({WEEKLY_CLAIMS_PER_CATEGORY})"
        )


async def record_claim_submit(
    session: AsyncSession, user_id: str, category: str
) -> None:
    day = await _get_or_create(session, user_id, _day_key(), category)
    week = await _get_or_create(session, user_id, _week_key(), category)
    day.count += 1
    week.count += 1
    await session.flush()


async def check_reward_allowed(
    session: AsyncSession, user_id: str, amount: Decimal
) -> None:
    """Cap total ECO rewarded per day/week across categories."""
    cat = "_ALL_"
    day = await _get_or_create(session, user_id, _day_key(), cat)
    week = await _get_or_create(session, user_id, _week_key(), cat)
    if day.amount_eco + amount > DAILY_ECO_PER_USER:
        raise ValueError(f"Daily ECO reward cap ({DAILY_ECO_PER_USER}) would be exceeded")
    if week.amount_eco + amount > WEEKLY_ECO_PER_USER:
        raise ValueError(f"Weekly ECO reward cap ({WEEKLY_ECO_PER_USER}) would be exceeded")


async def record_reward(
    session: AsyncSession, user_id: str, amount: Decimal
) -> None:
    cat = "_ALL_"
    day = await _get_or_create(session, user_id, _day_key(), cat)
    week = await _get_or_create(session, user_id, _week_key(), cat)
    day.amount_eco += amount
    week.amount_eco += amount
    await session.flush()

"""Seed demo chart of accounts + journal so summary is non-zero."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.accounting import Account, AccountType, EntryType, JournalEntry, JournalItem
from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/accounting", tags=["accounting"])


@router.post("/seed-demo")
async def seed_accounting_demo(session: AsyncSession = Depends(get_db_session)):
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Seed disabled in production")

    defaults = [
        ("1000", "Cash", "نقد", AccountType.ASSET),
        ("4000", "Farm Income", "درآمد مزرعه", AccountType.INCOME),
        ("5000", "Operating Expense", "هزینه عملیاتی", AccountType.EXPENSE),
    ]
    created_accounts = 0
    for code, name, name_fa, atype in defaults:
        exists = await session.execute(select(Account).where(Account.code == code))
        if exists.scalar_one_or_none() is None:
            session.add(
                Account(
                    id=code,
                    code=code,
                    name=name,
                    name_fa=name_fa,
                    account_type=atype,
                    is_active=True,
                    is_system=True,
                )
            )
            created_accounts += 1
    await session.flush()

    # Avoid duplicate demo journals
    existing = await session.execute(
        select(JournalEntry).where(JournalEntry.reference == "DEMO-SEED")
    )
    if existing.scalar_one_or_none() is not None:
        return {"ok": True, "accounts_created": created_accounts, "journal": "already_exists"}

    entry_id = f"JE-{uuid4().hex[:10]}"
    entry = JournalEntry(
        id=entry_id,
        date=datetime.utcnow(),
        description="Demo farm revenue and expense",
        reference="DEMO-SEED",
        is_posted=True,
        created_by="seed",
    )
    session.add(entry)
    await session.flush()

    # Income 2500 credit to 4000, debit cash 2500
    session.add(
        JournalItem(
            entry_id=entry_id,
            account_id="4000",
            entry_type=EntryType.CREDIT,
            amount=Decimal("2500.00"),
            description="Crop sales",
        )
    )
    session.add(
        JournalItem(
            entry_id=entry_id,
            account_id="1000",
            entry_type=EntryType.DEBIT,
            amount=Decimal("2500.00"),
            description="Cash received",
        )
    )
    # Expense 800 debit to 5000, credit cash 800
    entry2_id = f"JE-{uuid4().hex[:10]}"
    entry2 = JournalEntry(
        id=entry2_id,
        date=datetime.utcnow(),
        description="Demo operating expense",
        reference="DEMO-SEED",
        is_posted=True,
        created_by="seed",
    )
    session.add(entry2)
    await session.flush()
    session.add(
        JournalItem(
            entry_id=entry2_id,
            account_id="5000",
            entry_type=EntryType.DEBIT,
            amount=Decimal("800.00"),
            description="Fertilizer",
        )
    )
    session.add(
        JournalItem(
            entry_id=entry2_id,
            account_id="1000",
            entry_type=EntryType.CREDIT,
            amount=Decimal("800.00"),
            description="Cash paid",
        )
    )

    return {
        "ok": True,
        "accounts_created": created_accounts,
        "journal": "created",
        "expected_income": "2500.00",
        "expected_expense": "800.00",
    }

"""
Accounting Service | لایه کسب‌وکار حسابداری
============================================
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.accounting import Account, JournalEntry
from apps.api.repositories.accounting import (
    AccountRepository,
    BudgetRepository,
    InvoiceRepository,
    JournalEntryRepository,
    PaymentRepository,
)
from apps.api.schemas.accounting import (
    AccountCreate,
    AccountUpdate,
    BudgetCreate,
    BudgetUpdate,
    InvoiceCreate,
    InvoiceUpdate,
    JournalEntryCreate,
    PaymentCreate,
)

logger = logging.getLogger(__name__)


def _attach_balance(account: Account, balance: Decimal) -> Account:
    """Attach computed balance using Account.balance setter (_balance backing)."""
    try:
        account.balance = balance
    except AttributeError:
        # Fallback if an older model without setter is loaded
        object.__setattr__(account, "_balance", balance)
    return account


class AccountingService:
    def __init__(self, session: AsyncSession) -> None:
        self.accounts = AccountRepository(session)
        self.journal_entries = JournalEntryRepository(session)
        self.invoices = InvoiceRepository(session)
        self.payments = PaymentRepository(session)
        self.budgets = BudgetRepository(session)
        self.session = session


class AccountService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = AccountRepository(session)

    async def get(self, account_id: str) -> Account:
        obj = await self.repo.get_by_id(account_id)
        if not obj:
            raise ValueError(f"Account with id={account_id} not found")
        bal = await self.repo.calculate_balance(account_id)
        return _attach_balance(obj, bal)

    async def list(
        self, skip: int = 0, limit: int = 100, account_type: Optional[str] = None
    ) -> tuple[List[Account], int]:
        limit = min(limit, 1000)
        accounts, total = await self.repo.list(skip, limit, account_type)
        for account in accounts:
            bal = await self.repo.calculate_balance(account.id)
            _attach_balance(account, bal)
        return accounts, total

    async def create(self, data: AccountCreate) -> Account:
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise ValueError(f"Account with code={data.code} already exists")
        return await self.repo.create(data)

    async def update(self, account_id: str, data: AccountUpdate) -> Account:
        obj = await self.repo.get_by_id(account_id)
        if not obj:
            raise ValueError(f"Account with id={account_id} not found")
        return await self.repo.update(account_id, data)

    async def delete(self, account_id: str) -> None:
        obj = await self.repo.get_by_id(account_id)
        if not obj:
            raise ValueError(f"Account with id={account_id} not found")
        if obj.is_system:
            raise ValueError("System accounts cannot be deleted")
        await self.repo.delete(account_id)


class JournalEntryService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = JournalEntryRepository(session)

    async def get(self, entry_id: str) -> JournalEntry:
        obj = await self.repo.get_by_id(entry_id)
        if not obj:
            raise ValueError(f"Journal entry with id={entry_id} not found")
        return obj

    async def list(
        self, skip: int = 0, limit: int = 100, is_posted: Optional[bool] = None
    ) -> tuple[List[JournalEntry], int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit, is_posted)

    async def create(self, data: JournalEntryCreate) -> JournalEntry:
        total_debits = sum(
            item.amount for item in data.items if item.entry_type == "debit"
        )
        total_credits = sum(
            item.amount for item in data.items if item.entry_type == "credit"
        )
        if total_debits != total_credits:
            raise ValueError("Journal entry must be balanced (debits = credits)")
        entry = await self.repo.create(data)
        if total_debits > 0:
            await self.repo.post_entry(entry.id)
        return entry

    async def post_entry(self, entry_id: str) -> JournalEntry:
        obj = await self.repo.post_entry(entry_id)
        if not obj:
            raise ValueError(f"Journal entry with id={entry_id} not found")
        return obj


class InvoiceService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = InvoiceRepository(session)
        self.session = session

    async def get(self, invoice_id: str):
        obj = await self.repo.get_by_id(invoice_id)
        if not obj:
            raise ValueError(f"Invoice with id={invoice_id} not found")
        return obj

    async def list(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> tuple[list, int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit, status)

    async def create(self, data: InvoiceCreate):
        return await self.repo.create(data)

    async def update(self, invoice_id: str, data: InvoiceUpdate):
        obj = await self.repo.update(invoice_id, data)
        if not obj:
            raise ValueError(f"Invoice with id={invoice_id} not found")
        return obj

    async def delete(self, invoice_id: str) -> None:
        obj = await self.repo.get_by_id(invoice_id)
        if not obj:
            raise ValueError(f"Invoice with id={invoice_id} not found")
        await self.session.delete(obj)


class PaymentService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PaymentRepository(session)

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit)

    async def create(self, data: PaymentCreate):
        return await self.repo.create(data)


class BudgetService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = BudgetRepository(session)

    async def get(self, budget_id: str):
        obj = await self.repo.get_by_id(budget_id)
        if not obj:
            raise ValueError(f"Budget with id={budget_id} not found")
        return obj

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit)

    async def create(self, data: BudgetCreate):
        return await self.repo.create(data)

    async def update(self, budget_id: str, data: BudgetUpdate):
        obj = await self.repo.update(budget_id, data)
        if not obj:
            raise ValueError(f"Budget with id={budget_id} not found")
        return obj

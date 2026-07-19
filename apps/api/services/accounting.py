"""
Accounting Service | لایه کسب‌وکار حسابداری
============================================
Business logic layer — orchestrates repositories and enforces rules.
Controllers (routers) call services; services call repositories.
"""

from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.repositories.accounting import (
    AccountRepository, JournalEntryRepository, InvoiceRepository,
    PaymentRepository, BudgetRepository
)
from apps.api.schemas.accounting import (
    AccountCreate, AccountUpdate,
    JournalEntryCreate,
    InvoiceCreate, InvoiceUpdate,
    PaymentCreate,
    BudgetCreate, BudgetUpdate,
    DashboardSummaryResponse,
    BalanceSheetResponse, IncomeStatementResponse
)
from apps.api.models.accounting import Account, AccountType, JournalEntry, JournalItem


class AccountingService:
    """Main service for accounting operations."""

    def __init__(self, session: AsyncSession):
        self.accounts = AccountRepository(session)
        self.journal_entries = JournalEntryRepository(session)
        self.invoices = InvoiceRepository(session)
        self.payments = PaymentRepository(session)
        self.budgets = BudgetRepository(session)
        self.session = session


class AccountService:
    """Service for account operations."""

    def __init__(self, session: AsyncSession):
        self.repo = AccountRepository(session)

    async def get(self, account_id: str) -> Account:
        obj = await self.repo.get_by_id(account_id)
        if not obj:
            raise ValueError(f"Account with id={account_id} not found")
        # Calculate and attach balance
        obj.balance = await self.repo.calculate_balance(account_id)
        return obj

    async def list(
        self, skip: int = 0, limit: int = 100, account_type: Optional[str] = None
    ) -> tuple[List[Account], int]:
        limit = min(limit, 1000)
        accounts, total = await self.repo.list(skip, limit, account_type)
        # Calculate balances for all accounts
        for account in accounts:
            account.balance = await self.repo.calculate_balance(account.id)
        return accounts, total

    async def create(self, data: AccountCreate) -> Account:
        # Check code uniqueness
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
    """Service for journal entry operations."""

    def __init__(self, session: AsyncSession):
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
        # Validate double-entry balance
        total_debits = sum(
            item.amount for item in data.items
            if item.entry_type == "debit"
        )
        total_credits = sum(
            item.amount for item in data.items
            if item.entry_type == "credit"
        )
        if total_debits != total_credits:
            raise ValueError("Journal entry must be balanced (debits = credits)")
        
        # Generate ID if not provided
        entry = await self.repo.create(data)
        
        # Auto-post if balanced
        if total_debits > 0:
            await self.repo.post_entry(entry.id)
        
        return entry

    async def post_entry(self, entry_id: str) -> JournalEntry:
        obj = await self.repo.post_entry(entry_id)
        if not obj:
            raise ValueError(f"Journal entry with id={entry_id} not found")
        return obj


class InvoiceService:
    """Service for invoice operations."""

    def __init__(self, session: AsyncSession):
        self.repo = InvoiceRepository(session)

    async def get(self, invoice_id: str) -> "Invoice":
        from apps.api.models.accounting import Invoice as InvoiceModel
        obj = await self.repo.get_by_id(invoice_id)
        if not obj:
            raise ValueError(f"Invoice with id={invoice_id} not found")
        return obj

    async def list(
        self, skip: int = 0, limit: int = 100, status: Optional[str] = None
    ) -> tuple[list, int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit, status)

    async def create(self, data: InvoiceCreate) -> "Invoice":
        return await self.repo.create(data)

    async def update(self, invoice_id: str, data: InvoiceUpdate) -> "Invoice":
        obj = await self.repo.update(invoice_id, data)
        if not obj:
            raise ValueError(f"Invoice with id={invoice_id} not found")
        return obj

    async def delete(self, invoice_id: str) -> None:
        # Will need to add delete method to repository
        obj = await self.repo.get_by_id(invoice_id)
        if not obj:
            raise ValueError(f"Invoice with id={invoice_id} not found")
        # Add delete logic
        await self.session.delete(obj)


class PaymentService:
    """Service for payment operations."""

    def __init__(self, session: AsyncSession):
        self.repo = PaymentRepository(session)

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit)

    async def create(self, data: PaymentCreate) -> "Payment":
        from apps.api.models.accounting import Payment as PaymentModel
        return await self.repo.create(data)


class BudgetService:
    """Service for budget operations."""

    def __init__(self, session: AsyncSession):
        self.repo = BudgetRepository(session)

    async def get(self, budget_id: str) -> "Budget":
        from apps.api.models.accounting import Budget as BudgetModel
        obj = await self.repo.get_by_id(budget_id)
        if not obj:
            raise ValueError(f"Budget with id={budget_id} not found")
        return obj

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list, int]:
        limit = min(limit, 1000)
        return await self.repo.list(skip, limit)

    async def create(self, data: BudgetCreate) -> "Budget":
        return await self.repo.create(data)

    async def update(self, budget_id: str, data: BudgetUpdate) -> "Budget":
        obj = await self.repo.update(budget_id, data)
        if not obj:
            raise ValueError(f"Budget with id={budget_id} not found")
        return obj


# TODO: Add delete methods to repository if needed
# Import for Invoice and Payment
from apps.api.models.accounting import Invoice, Payment, Budget
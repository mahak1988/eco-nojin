"""
Accounting Repository | لایه دسترسی داده حسابداری
==================================================
Data access layer — all database queries live here.
Services call repositories; repositories never call services.
"""

from __future__ import annotations

import builtins
import logging
from decimal import Decimal

from sqlalchemy import case, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.api.models.accounting import (
    Account,
    Budget,
    FixedAsset,
    Invoice,
    InvoiceItem,
    JournalEntry,
    JournalItem,
    Payment,
    TaxRate,
)
from apps.api.schemas.accounting import (
    AccountCreate,
    AccountUpdate,
    BudgetCreate,
    BudgetUpdate,
    FixedAssetCreate,
    InvoiceCreate,
    InvoiceUpdate,
    JournalEntryCreate,
    PaymentCreate,
)

logger = logging.getLogger(__name__)


class AccountRepository:
    """Repository for Account entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, account_id: str) -> Account | None:
        result = await self.session.execute(select(Account).where(Account.id == account_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> Account | None:
        result = await self.session.execute(select(Account).where(Account.code == code))
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        account_type: str | None = None,
        is_active: bool | None = None,
    ) -> tuple[builtins.list[Account], int]:
        query = select(Account)
        if account_type:
            query = query.where(Account.account_type == account_type)
        if is_active is not None:
            query = query.where(Account.is_active == is_active)

        query = query.order_by(Account.code).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(Account)
        if account_type:
            count_query = count_query.where(Account.account_type == account_type)
        if is_active is not None:
            count_query = count_query.where(Account.is_active == is_active)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: AccountCreate) -> Account:
        obj = Account(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, account_id: str, data: AccountUpdate) -> Account | None:
        obj = await self.get_by_id(account_id)
        if not obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, account_id: str) -> bool:
        obj = await self.get_by_id(account_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def calculate_balance(self, account_id: str) -> Decimal:
        """Calculate account balance from journal items (debit positive)."""
        balance_expr = case(
            (JournalItem.entry_type == "debit", JournalItem.amount),
            else_=-JournalItem.amount,
        )
        result = await self.session.execute(
            select(func.coalesce(func.sum(balance_expr), 0)).where(
                JournalItem.account_id == account_id
            )
        )
        balance = result.scalar_one()
        return Decimal(str(balance)) if balance is not None else Decimal("0.00")


class JournalEntryRepository:
    """Repository for JournalEntry entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, entry_id: str) -> JournalEntry | None:
        result = await self.session.execute(
            select(JournalEntry)
            .options(selectinload(JournalEntry.items))
            .where(JournalEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        is_posted: bool | None = None,
    ) -> tuple[builtins.list[JournalEntry], int]:
        query = select(JournalEntry).options(selectinload(JournalEntry.items))
        if is_posted is not None:
            query = query.where(JournalEntry.is_posted == is_posted)

        query = query.order_by(desc(JournalEntry.date)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().unique().all())

        count_query = select(func.count()).select_from(JournalEntry)
        if is_posted is not None:
            count_query = count_query.where(JournalEntry.is_posted == is_posted)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: JournalEntryCreate) -> JournalEntry:
        obj = JournalEntry(
            date=data.date,
            description=data.description,
            reference=data.reference,
            is_posted=data.is_posted,
        )
        for item_data in data.items:
            item = JournalItem(**item_data.model_dump())
            obj.items.append(item)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj, attribute_names=["items"])
        return obj

    async def post_entry(self, entry_id: str) -> JournalEntry | None:
        obj = await self.get_by_id(entry_id)
        if not obj:
            return None
        obj.is_posted = True
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class InvoiceRepository:
    """Repository for Invoice entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, invoice_id: str) -> Invoice | None:
        result = await self.session.execute(
            select(Invoice).options(selectinload(Invoice.items)).where(Invoice.id == invoice_id)
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, number: str) -> Invoice | None:
        result = await self.session.execute(select(Invoice).where(Invoice.number == number))
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
    ) -> tuple[builtins.list[Invoice], int]:
        query = select(Invoice).options(selectinload(Invoice.items))
        if status:
            query = query.where(Invoice.status == status)

        query = query.order_by(desc(Invoice.issue_date)).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().unique().all())

        count_query = select(func.count()).select_from(Invoice)
        if status:
            count_query = count_query.where(Invoice.status == status)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: InvoiceCreate) -> Invoice:
        subtotal = sum((item.quantity * item.unit_price) for item in data.items)
        tax_amount = sum(
            (item.quantity * item.unit_price * item.tax_rate / 100) for item in data.items
        )
        total = subtotal + tax_amount

        obj = Invoice(
            client_name=data.client_name,
            client_email=data.client_email,
            issue_date=data.issue_date,
            due_date=data.due_date,
            notes=data.notes,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total=total,
        )
        for item_data in data.items:
            item = InvoiceItem(**item_data.model_dump())
            obj.items.append(item)

        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj, attribute_names=["items"])
        return obj

    async def update(self, invoice_id: str, data: InvoiceUpdate) -> Invoice | None:
        obj = await self.get_by_id(invoice_id)
        if not obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class PaymentRepository:
    """Repository for Payment entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, payment_id: str) -> Payment | None:
        result = await self.session.execute(select(Payment).where(Payment.id == payment_id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[builtins.list[Payment], int]:
        query = select(Payment).order_by(desc(Payment.paid_at))
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_result = await self.session.execute(select(func.count()).select_from(Payment))
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: PaymentCreate) -> Payment:
        obj = Payment(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class BudgetRepository:
    """Repository for Budget entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, budget_id: str) -> Budget | None:
        result = await self.session.execute(select(Budget).where(Budget.id == budget_id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[builtins.list[Budget], int]:
        query = select(Budget).order_by(Budget.period_start)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_result = await self.session.execute(select(func.count()).select_from(Budget))
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: BudgetCreate) -> Budget:
        obj = Budget(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, budget_id: str, data: BudgetUpdate) -> Budget | None:
        obj = await self.get_by_id(budget_id)
        if not obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class TaxRateRepository:
    """Repository for TaxRate entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, tax_id: str) -> TaxRate | None:
        result = await self.session.execute(select(TaxRate).where(TaxRate.id == tax_id))
        return result.scalar_one_or_none()

    async def list_active(self) -> list[TaxRate]:
        result = await self.session.execute(select(TaxRate).where(TaxRate.is_active == True))
        return list(result.scalars().all())


class FixedAssetRepository:
    """Repository for FixedAsset entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, asset_id: str) -> FixedAsset | None:
        result = await self.session.execute(select(FixedAsset).where(FixedAsset.id == asset_id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[builtins.list[FixedAsset], int]:
        query = select(FixedAsset).order_by(FixedAsset.purchase_date)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_result = await self.session.execute(select(func.count()).select_from(FixedAsset))
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: FixedAssetCreate) -> FixedAsset:
        net_book_value = data.purchase_cost - Decimal("0.00")

        obj = FixedAsset(
            **data.model_dump(),
            accumulated_depreciation=Decimal("0.00"),
            net_book_value=net_book_value,
        )
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

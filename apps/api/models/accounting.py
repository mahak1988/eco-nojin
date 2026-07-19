"""
Econojin Accounting Models
==========================
Complete double-entry bookkeeping system with Chart of Accounts,
Journal Entries, Invoices, Payments, Budgets, and Tax management.
Adapted from best practices in open-source accounting systems.
"""

from sqlalchemy import (
    String, Numeric, DateTime, Text, Boolean, Integer,
    ForeignKey, Enum as SQLEnum, CheckConstraint, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from apps.shared_core.database.session import Base


# ── Enums ──────────────────────────────────────────────────────
class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    INCOME = "income"
    EXPENSE = "expense"


class EntryType(str, Enum):
    DEBIT = "debit"
    CREDIT = "credit"


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    ECOCOIN = "ecocoin"
    CARBON_CREDIT = "carbon_credit"


class TaxType(str, Enum):
    VAT = "vat"
    INCOME_TAX = "income_tax"
    CUSTOM = "custom"


# ── Chart of Accounts ──────────────────────────────────────────
class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    account_type: Mapped[AccountType] = mapped_column(SQLEnum(AccountType), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(20), ForeignKey("accounts.id"), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    parent: Mapped[Optional["Account"]] = relationship("Account", remote_side=[id], backref="children")
    journal_items: Mapped[List["JournalItem"]] = relationship("JournalItem", back_populates="account")

    __table_args__ = (
        Index("idx_accounts_type", "account_type"),
        Index("idx_accounts_parent", "parent_id"),
    )

    def __repr__(self):
        return f"<Account({self.code} {self.name})>"

    @property
    def balance(self) -> Decimal:
        """Calculate current balance from journal items."""
        # This is computed in the service layer
        return Decimal("0.00")


# ── Journal Entries ─────────────────────────────────────────────
class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items: Mapped[List["JournalItem"]] = relationship("JournalItem", back_populates="entry", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<JournalEntry({self.id} {self.date.date()})>"

    @property
    def total_debits(self) -> Decimal:
        return sum(item.amount for item in self.items if item.entry_type == EntryType.DEBIT)

    @property
    def total_credits(self) -> Decimal:
        return sum(item.amount for item in self.items if item.entry_type == EntryType.CREDIT)

    @property
    def is_balanced(self) -> bool:
        return self.total_debits == self.total_credits


class JournalItem(Base):
    __tablename__ = "journal_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entry_id: Mapped[str] = mapped_column(String(30), ForeignKey("journal_entries.id"), nullable=False, index=True)
    account_id: Mapped[str] = mapped_column(String(20), ForeignKey("accounts.id"), nullable=False, index=True)
    entry_type: Mapped[EntryType] = mapped_column(SQLEnum(EntryType), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="items")
    account: Mapped["Account"] = relationship("Account", back_populates="journal_items")

    def __repr__(self):
        return f"<JournalItem({self.entry_id} {self.account_id} {self.entry_type} {self.amount})>"


# ── Invoices ───────────────────────────────────────────────────
class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    client_name: Mapped[str] = mapped_column(String(255), nullable=False)
    client_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issue_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    journal_entry_id: Mapped[Optional[str]] = mapped_column(String(30), ForeignKey("journal_entries.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    items: Mapped[List["InvoiceItem"]] = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice({self.number} {self.client_name})>"


class InvoiceItem(Base):
    __tablename__ = "invoice_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[str] = mapped_column(String(30), ForeignKey("invoices.id"), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tax_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Relationships
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")

    def __repr__(self):
        return f"<InvoiceItem({self.description} {self.quantity}x{self.unit_price})>"


# ── Payments ───────────────────────────────────────────────────
class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    invoice_id: Mapped[Optional[str]] = mapped_column(String(30), ForeignKey("invoices.id"), nullable=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(SQLEnum(PaymentMethod), nullable=False)
    reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    journal_entry_id: Mapped[Optional[str]] = mapped_column(String(30), ForeignKey("journal_entries.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    invoice: Mapped[Optional["Invoice"]] = relationship("Invoice", back_populates="payments")

    def __repr__(self):
        return f"<Payment({self.id} {self.amount} {self.payment_method})>"


# ── Budgets ────────────────────────────────────────────────────
class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[str] = mapped_column(String(20), ForeignKey("accounts.id"), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    planned_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    variance: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Budget({self.name} {self.planned_amount})>"


class BudgetAlert(Base):
    __tablename__ = "budget_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[str] = mapped_column(String(30), ForeignKey("budgets.id"), nullable=False, index=True)
    threshold_percent: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    trigger_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


# ── Tax Rates ──────────────────────────────────────────────────
class TaxRate(Base):
    __tablename__ = "tax_rates"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    tax_type: Mapped[TaxType] = mapped_column(SQLEnum(TaxType), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    account_id: Mapped[str] = mapped_column(String(20), ForeignKey("accounts.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<TaxRate({self.name} {self.rate}%)>"


# ── Fixed Assets ───────────────────────────────────────────────
class FixedAsset(Base):
    __tablename__ = "fixed_assets"

    id: Mapped[str] = mapped_column(String(30), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    purchase_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    purchase_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    useful_life_years: Mapped[int] = mapped_column(Integer, nullable=False)
    salvage_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    depreciation_method: Mapped[str] = mapped_column(String(20), default="straight_line", nullable=False)
    accumulated_depreciation: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"), nullable=False)
    net_book_value: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    account_id: Mapped[str] = mapped_column(String(20), ForeignKey("accounts.id"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<FixedAsset({self.name} cost={self.purchase_cost})>"
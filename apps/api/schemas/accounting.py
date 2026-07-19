"""
Accounting Schemas | پ schemaهای حسابداری
========================================
Pydantic models for request/response validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict


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


# ── Account Schemas ────────────────────────────────────────────
class AccountBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, description="Account code")
    name: str = Field(..., min_length=1, max_length=255, description="Account name")
    name_fa: Optional[str] = Field(None, max_length=255, description="Persian name")
    account_type: AccountType = Field(..., description="Account type")
    parent_id: Optional[str] = Field(None, description="Parent account ID")
    description: Optional[str] = None
    is_active: bool = True
    is_system: bool = False


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    name_fa: Optional[str] = None
    account_type: Optional[AccountType] = None
    parent_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AccountResponse(AccountBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    balance: Decimal = Decimal("0.00")


class AccountListResponse(BaseModel):
    items: List[AccountResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ── Journal Entry Schemas ──────────────────────────────────────
class JournalItemBase(BaseModel):
    account_id: str = Field(..., description="Account ID")
    entry_type: EntryType = Field(..., description="Debit or Credit")
    amount: Decimal = Field(..., ge=0, description="Entry amount")
    description: Optional[str] = None


class JournalItemCreate(JournalItemBase):
    pass


class JournalItemResponse(JournalItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class JournalEntryBase(BaseModel):
    date: datetime = Field(..., description="Entry date")
    description: str = Field(..., min_length=1, max_length=500, description="Entry description")
    reference: Optional[str] = None
    is_posted: bool = False


class JournalEntryCreate(JournalEntryBase):
    items: List[JournalItemCreate] = Field(..., min_length=2, description="At least 2 items for double-entry")


class JournalEntryUpdate(BaseModel):
    date: Optional[datetime] = None
    description: Optional[str] = None
    reference: Optional[str] = None


class JournalEntryResponse(JournalEntryBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    total_debits: Decimal = Decimal("0.00")
    total_credits: Decimal = Decimal("0.00")
    is_balanced: bool = True
    items: List[JournalItemResponse] = []


class JournalEntryListResponse(BaseModel):
    items: List[JournalEntryResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ── Invoice Schemas ────────────────────────────────────────────
class InvoiceItemBase(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    quantity: Decimal = Field(..., ge=0)
    unit_price: Decimal = Field(..., ge=0)
    tax_rate: Decimal = Decimal("0.00")


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class InvoiceBase(BaseModel):
    client_name: str = Field(..., min_length=1, max_length=255)
    client_email: Optional[str] = None
    issue_date: datetime
    due_date: datetime
    notes: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate] = Field(..., min_length=1)


class InvoiceUpdate(BaseModel):
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    due_date: Optional[datetime] = None
    status: Optional[InvoiceStatus] = None
    notes: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    number: str
    status: InvoiceStatus
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[InvoiceItemResponse] = []


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ── Payment Schemas ────────────────────────────────────────────
class PaymentBase(BaseModel):
    invoice_id: Optional[str] = None
    amount: Decimal = Field(..., ge=0)
    currency: str = "USD"
    payment_method: PaymentMethod
    reference: Optional[str] = None
    notes: Optional[str] = None


class PaymentCreate(PaymentBase):
    paid_at: datetime = Field(default_factory=datetime.utcnow)


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    paid_at: datetime
    created_at: datetime


class PaymentListResponse(BaseModel):
    items: List[PaymentResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ── Budget Schemas ─────────────────────────────────────────────
class BudgetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    account_id: str
    period_start: datetime
    period_end: datetime
    planned_amount: Decimal = Field(..., ge=0)
    notes: Optional[str] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    name: Optional[str] = None
    planned_amount: Optional[Decimal] = None
    notes: Optional[str] = None


class BudgetResponse(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actual_amount: Decimal = Decimal("0.00")
    variance: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime


class BudgetListResponse(BaseModel):
    items: List[BudgetResponse]
    total: int
    skip: int = 0
    limit: int = 100


# ── Tax Rate Schemas ───────────────────────────────────────────
class TaxRateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    tax_type: TaxType
    rate: Decimal = Field(..., ge=0, le=100)
    account_id: str
    effective_from: datetime
    effective_to: Optional[datetime] = None


class TaxRateCreate(TaxRateBase):
    pass


class TaxRateUpdate(BaseModel):
    name: Optional[str] = None
    rate: Optional[Decimal] = None
    effective_to: Optional[datetime] = None
    is_active: Optional[bool] = None


class TaxRateResponse(TaxRateBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_active: bool
    created_at: datetime


# ── Fixed Asset Schemas ────────────────────────────────────────
class FixedAssetBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    purchase_date: datetime
    purchase_cost: Decimal = Field(..., ge=0)
    useful_life_years: int = Field(..., gt=0)
    salvage_value: Decimal = Decimal("0.00")
    depreciation_method: str = "straight_line"
    account_id: str


class FixedAssetCreate(FixedAssetBase):
    pass


class FixedAssetUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    salvage_value: Optional[Decimal] = None
    is_active: Optional[bool] = None


class FixedAssetResponse(FixedAssetBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    accumulated_depreciation: Decimal = Decimal("0.00")
    net_book_value: Decimal
    is_active: bool
    created_at: datetime
    updated_at: datetime


# ── Summary/Report Schemas ─────────────────────────────────────
class BalanceSheetResponse(BaseModel):
    """Response model for balance sheet report."""
    assets: Decimal = Decimal("0.00")
    liabilities: Decimal = Decimal("0.00")
    equity: Decimal = Decimal("0.00")


class IncomeStatementResponse(BaseModel):
    """Response model for income statement report."""
    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    net_profit: Decimal = Decimal("0.00")


class DashboardSummaryResponse(BaseModel):
    """Response model for accounting dashboard summary."""
    total_income: Decimal = Decimal("0.00")
    total_expense: Decimal = Decimal("0.00")
    net_profit: Decimal = Decimal("0.00")
    eco_rewards_distributed: Decimal = Decimal("0.00")
    carbon_credits_value: Decimal = Decimal("0.00")
    transactions_count: int = 0
    current_balance: Decimal = Decimal("0.00")
"""
Database Models for Accounting Module
مدل‌های پایگاه داده برای ماژول حسابداری و مالی

این ماژول شامل مدل‌های SQLAlchemy برای:
- چارت حساب‌ها (Chart of Accounts)
- اسناد حسابداری (Accounting Entries/Journal Entries)
- فاکتورها (Invoices)
- پرداخت‌ها و دریافت‌ها (Payments/Receipts)
- بودجه‌بندی (Budgets)
- گزارش‌های مالی (Financial Reports)
- توکن ECO (ECO Token)
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Text, Boolean, JSON, Numeric, Enum as SQLEnum, Table, Index, Date
)
from sqlalchemy.orm import relationship, declarative_base, Mapped, mapped_column
from sqlalchemy.sql import func

Base = declarative_base()


class AccountType(str, Enum):
    """انواع حساب‌های حسابداری"""
    ASSET = "asset"              # دارایی
    LIABILITY = "liability"      # بدهی
    EQUITY = "equity"            # حقوق صاحبان سهام
    REVENUE = "revenue"          # درآمد
    EXPENSE = "expense"          # هزینه
    
    # زیردسته‌های دارایی
    CURRENT_ASSET = "current_asset"       # دارایی جاری
    FIXED_ASSET = "fixed_asset"           # دارایی ثابت
    INTANGIBLE_ASSET = "intangible_asset" # دارایی نامشهود
    
    # زیردسته‌های بدهی
    CURRENT_LIABILITY = "current_liability"   # بدهی جاری
    LONG_TERM_LIABILITY = "long_term_liability"  # بدهی بلندمدت


class EntryType(str, Enum):
    """انواع سند حسابداری"""
    JOURNAL = "journal"          # سند عادی
    ADJUSTING = "adjusting"      # سند اصلاحی
    CLOSING = "closing"          # سند بستن
    REVERSING = "reversing"      # سند برگشتی
    OPENING = "opening"          # سند افتتاحیه


class InvoiceStatus(str, Enum):
    """وضعیت فاکتور"""
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentStatus(str, Enum):
    """وضعیت پرداخت"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class BudgetStatus(str, Enum):
    """وضعیت بودجه"""
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    CLOSED = "closed"
    REVISION = "revision"


# ============================================================================
# Chart of Accounts
# ============================================================================

class Account(Base):
    """
    حساب‌های حسابداری (چارت حساب‌ها)
    ساختار درختی برای سازماندهی حساب‌ها
    """
    __tablename__ = "accounting_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # کد حساب (ساختار سلسله مراتبی)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # نوع حساب
    account_type: Mapped[str] = mapped_column(SQLEnum(AccountType), nullable=False)
    
    # سطح در چارت حساب‌ها
    level: Mapped[int] = mapped_column(Integer, default=1)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_accounts.id"), nullable=True
    )
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # ارز
    currency: Mapped[str] = mapped_column(String(10), default="IRR")
    
    # وضعیت
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)  # حساب سیستمی، قابل حذف نیست
    allow_manual_entry: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # تراز فعلی
    current_balance: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    debit_balance: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    credit_balance: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    # متادیتا
    tax_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    parent: Mapped["Account"] = relationship(
        "Account",
        backref="children",
        remote_side=[id],
        foreign_keys=[parent_id]
    )
    journal_entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry", back_populates="account", cascade="all, delete-orphan"
    )
    budget_items: Mapped[List["BudgetItem"]] = relationship(
        "BudgetItem", back_populates="account"
    )
    
    # ایندکس‌ها
    __table_args__ = (
        Index('idx_account_code', 'code'),
        Index('idx_account_type', 'account_type'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Account(id={self.id}, code='{self.code}', name='{self.name}')>"


# ============================================================================
# Journal Entries (اسناد حسابداری)
# ============================================================================

class JournalEntry(Base):
    """
    اقلام دفتر روزنامه (سطرهای سند حسابداری)
    هر سند شامل چندین ژورنال-entry است که مجموع بدهکار و بستانکار برابر است
    """
    __tablename__ = "accounting_journal_entries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # شماره سند
    voucher_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entry_number: Mapped[int] = mapped_column(Integer, default=1)  # شماره سطر در سند
    
    # حساب
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounting_accounts.id"), nullable=False)
    
    # مبالغ
    debit_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    credit_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    # ارز و نرخ
    currency: Mapped[str] = mapped_column(String(10), default="IRR")
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # مرکز هزینه/درآمد (اختیاری)
    cost_center_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_cost_centers.id"), nullable=True
    )
    project_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_projects.id"), nullable=True
    )
    
    # ارجاع به اسناد دیگر
    invoice_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_invoices.id"), nullable=True
    )
    payment_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_payments.id"), nullable=True
    )
    
    # تاریخ
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # وضعیت
    is_posted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reconciled: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # روابط
    account: Mapped["Account"] = relationship("Account", back_populates="journal_entries")
    cost_center: Mapped["CostCenter"] = relationship("CostCenter")
    project: Mapped["AccountingProject"] = relationship("AccountingProject")
    
    __table_args__ = (
        Index('idx_entry_voucher', 'voucher_number'),
        Index('idx_entry_date', 'entry_date'),
        Index('idx_entry_account', 'account_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<JournalEntry(voucher='{self.voucher_number}', account={self.account_id}, debit={self.debit_amount}, credit={self.credit_amount})>"


class JournalVoucher(Base):
    """
    سند حسابداری (مجموعه‌ای از JournalEntryها)
    """
    __tablename__ = "accounting_journal_vouchers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # شماره سند
    voucher_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # نوع سند
    entry_type: Mapped[str] = mapped_column(SQLEnum(EntryType), default=EntryType.JOURNAL)
    
    # تاریخ
    voucher_date: Mapped[date] = mapped_column(Date, nullable=False)
    posting_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(
        SQLEnum("draft", "posted", "voided", name="voucher_status"),
        default="draft"
    )
    
    # مبالغ کل
    total_debit: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    total_credit: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    is_balanced: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # پیوست‌ها
    attachments: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # تاییدیه
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="voucher",
        cascade="all, delete-orphan",
        primaryjoin="JournalEntry.voucher_number == JournalVoucher.voucher_number",
        foreign_keys="JournalEntry.voucher_number"
    )
    
    __table_args__ = (
        Index('idx_voucher_date', 'voucher_date'),
        Index('idx_voucher_status', 'status'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<JournalVoucher(number='{self.voucher_number}', date={self.voucher_date}, status='{self.status}')>"


# ============================================================================
# Invoices (فاکتورها)
# ============================================================================

class Invoice(Base):
    """
    فاکتورهای فروش و خرید
    """
    __tablename__ = "accounting_invoices"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # شماره فاکتور
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # نوع فاکتور
    invoice_type: Mapped[str] = mapped_column(
        SQLEnum("sales", "purchase", "credit_note", "debit_note", name="invoice_type"),
        nullable=False
    )
    
    # طرف حساب
    customer_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    vendor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("vendors.id"), nullable=True)
    
    # تاریخ‌ها
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    # مبالغ
    subtotal: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    tax_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    shipping_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    paid_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    # ارز
    currency: Mapped[str] = mapped_column(String(10), default="IRR")
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)
    
    # شرایط پرداخت
    payment_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # یادداشت‌ها
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # فایل
    pdf_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    items: Mapped[List["InvoiceItem"]] = relationship(
        "InvoiceItem", back_populates="invoice", cascade="all, delete-orphan"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment", back_populates="invoice"
    )
    
    __table_args__ = (
        Index('idx_invoice_number', 'invoice_number'),
        Index('idx_invoice_status', 'status'),
        Index('idx_invoice_customer', 'customer_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Invoice(number='{self.invoice_number}', type='{self.invoice_type}', total={self.total_amount})>"


class InvoiceItem(Base):
    """
    اقلام فاکتور
    """
    __tablename__ = "accounting_invoice_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invoice_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounting_invoices.id"), nullable=False)
    
    # اطلاعات قلم
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"), nullable=True)
    account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_accounts.id"), nullable=True
    )
    
    # مقادیر
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    discount_percent: Mapped[float] = mapped_column(Float, default=0)
    tax_percent: Mapped[float] = mapped_column(Float, default=0)
    
    # مبالغ
    line_total: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    # ترتیب
    order: Mapped[int] = mapped_column(Integer, default=0)
    
    # روابط
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="items")
    
    __table_args__ = (
        Index('idx_item_invoice_order', 'invoice_id', 'order'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<InvoiceItem(invoice={self.invoice_id}, description='{self.description[:30]}...')>"


# ============================================================================
# Payments (پرداخت‌ها)
# ============================================================================

class Payment(Base):
    """
    پرداخت‌ها و دریافت‌ها
    """
    __tablename__ = "accounting_payments"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # شماره پرداخت
    payment_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    # نوع
    payment_type: Mapped[str] = mapped_column(
        SQLEnum("incoming", "outgoing", name="payment_type"),
        nullable=False
    )
    
    # روش پرداخت
    payment_method: Mapped[str] = mapped_column(
        SQLEnum(
            "cash", "bank_transfer", "check", "credit_card", 
            "crypto", "eco_token", "other", name="payment_method"
        ),
        nullable=False
    )
    
    # مبلغ
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="IRR")
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 6), nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # تاریخ
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # ارجاعات
    invoice_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_invoices.id"), nullable=True
    )
    
    # حساب بانکی/صندوق
    bank_account_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_bank_accounts.id"), nullable=True
    )
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # چک (اگر روش پرداخت چک باشد)
    check_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    check_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    check_bank: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    # روابط
    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="payments")
    
    __table_args__ = (
        Index('idx_payment_number', 'payment_number'),
        Index('idx_payment_date', 'payment_date'),
        Index('idx_payment_invoice', 'invoice_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Payment(number='{self.payment_number}', amount={self.amount}, type='{self.payment_type}')>"


# ============================================================================
# Budgeting (بودجه‌بندی)
# ============================================================================

class Budget(Base):
    """
    بودجه‌های سازمانی
    """
    __tablename__ = "accounting_budgets"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # اطلاعات بودجه
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # دوره بودجه
    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # وضعیت
    status: Mapped[str] = mapped_column(SQLEnum(BudgetStatus), default=BudgetStatus.DRAFT)
    
    # نوع بودجه
    budget_type: Mapped[str] = mapped_column(
        SQLEnum("operating", "capital", "cash", "project", name="budget_type"),
        nullable=False
    )
    
    # مبالغ کل
    total_budget: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    total_actual: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    variance: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # تاییدیه
    approved_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # روابط
    items: Mapped[List["BudgetItem"]] = relationship(
        "BudgetItem", back_populates="budget", cascade="all, delete-orphan"
    )
    
    __table_args__ = (
        Index('idx_budget_year', 'fiscal_year'),
        Index('idx_budget_status', 'status'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<Budget(id={self.id}, name='{self.name}', year={self.fiscal_year})>"


class BudgetItem(Base):
    """
    اقلام بودجه
    """
    __tablename__ = "accounting_budget_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    budget_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounting_budgets.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounting_accounts.id"), nullable=False)
    
    # مبالغ
    budgeted_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    # تقسیم زمانی (اختیاری)
    monthly_breakdown: Mapped[Optional[List[Decimal]]] = mapped_column(JSON, nullable=True)
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # روابط
    budget: Mapped["Budget"] = relationship("Budget", back_populates="items")
    account: Mapped["Account"] = relationship("Account", back_populates="budget_items")
    
    __table_args__ = (
        Index('idx_budget_item_budget', 'budget_id'),
        Index('idx_budget_item_account', 'account_id'),
        {'sqlite_autoincrement': True}
    )
    
    def __repr__(self):
        return f"<BudgetItem(budget={self.budget_id}, account={self.account_id}, amount={self.budgeted_amount})>"


# ============================================================================
# Additional Models
# ============================================================================

class CostCenter(Base):
    """
    مراکز هزینه
    """
    __tablename__ = "accounting_cost_centers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_fa: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("accounting_cost_centers.id"), nullable=True
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CostCenter(code='{self.code}', name='{self.name}')>"


class AccountingProject(Base):
    """
    پروژه‌های حسابداری (برای حسابداری پروژه‌ای)
    """
    __tablename__ = "accounting_projects"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    
    status: Mapped[str] = mapped_column(
        SQLEnum("planning", "active", "completed", "on_hold", "cancelled", name="project_status"),
        default="planning"
    )
    
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 4), nullable=True)
    actual_cost: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AccountingProject(code='{self.code}', name='{self.name}')>"


class BankAccount(Base):
    """
    حساب‌های بانکی
    """
    __tablename__ = "accounting_bank_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    account_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("accounting_accounts.id"), nullable=False
    )
    
    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    iban: Mapped[Optional[str]] = mapped_column(String(34), nullable=True)
    
    currency: Mapped[str] = mapped_column(String(10), default="IRR")
    current_balance: Mapped[Decimal] = mapped_column(Numeric(20, 4), default=0)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<BankAccount(number='{self.account_number}', bank='{self.bank_name}')>"


class EcoTokenTransaction(Base):
    """
    تراکنش‌های توکن ECO
    """
    __tablename__ = "accounting_eco_tokens"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # نوع تراکنش
    transaction_type: Mapped[str] = mapped_column(
        SQLEnum(
            "earn", "spend", "transfer_in", "transfer_out", 
            "reward", "penalty", "exchange", name="token_transaction_type"
        ),
        nullable=False
    )
    
    # مقدار
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=True)
    
    # منبع/مقصد
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    destination: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # توضیحات
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reference_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # وضعیت
    status: Mapped[str] = mapped_column(
        SQLEnum("pending", "confirmed", "failed", name="token_status"),
        default="pending"
    )
    
    # blockchain (اگر applicable باشد)
    tx_hash: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<EcoTokenTransaction(user={self.user_id}, type='{self.transaction_type}', amount={self.amount})>"


# Placeholder models for foreign key references
User = type("User", (), {})
Vendor = type("Vendor", (), {})
Product = type("Product", (), {})

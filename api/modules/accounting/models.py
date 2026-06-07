# api/modules/accounting/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


class AccountType(enum.Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"


class JournalEntryType(enum.Enum):
    MANUAL = "manual"
    AUTO = "auto"
    ADJUSTMENT = "adjustment"
    CLOSING = "closing"


class AssetType(enum.Enum):
    CURRENT = "current"
    FIXED = "fixed"
    INTANGIBLE = "intangible"
    INVESTMENT = "investment"


class BankAccount(Base):
    """حساب‌های بانکی شرکت (بدون نیاز به اتصال واقعی)"""
    __tablename__ = "bank_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_name = Column(String(200), nullable=False)
    bank_name = Column(String(200), nullable=False)
    account_number = Column(String(50), unique=True, nullable=False)
    sheba_number = Column(String(50))
    branch_name = Column(String(200))
    branch_code = Column(String(50))
    
    account_type = Column(String(50), default="current")  # current, savings, deposit
    currency = Column(String(10), default="IRR")
    
    balance = Column(Float, default=0.0)
    credit_limit = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    is_primary = Column(Boolean, default=False)
    
    # اطلاعات تکمیلی
    description = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    transactions = relationship("BankTransaction", back_populates="bank_account")


class BankTransaction(Base):
    """تراکنش‌های بانکی (ثبت دستی)"""
    __tablename__ = "bank_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False)
    
    transaction_type = Column(String(20), nullable=False)  # deposit, withdrawal, transfer
    amount = Column(Float, nullable=False)
    
    # اطلاعات تراکنش
    transaction_date = Column(DateTime, nullable=False)
    reference_number = Column(String(100))
    tracking_code = Column(String(100))
    check_number = Column(String(50))
    
    # طرف حساب
    counterparty_name = Column(String(200))
    counterparty_account = Column(String(50))
    
    description = Column(Text)
    notes = Column(Text)
    
    # وضعیت
    status = Column(String(20), default="completed")  # pending, completed, cancelled
    is_reconciled = Column(Boolean, default=False)
    
    # ارجاع به سند حسابداری
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    
    created_at = Column(DateTime, server_default=func.now())
    
    bank_account = relationship("BankAccount", back_populates="transactions")
    journal_entry = relationship("JournalEntry", back_populates="bank_transactions")


class ChartOfAccount(Base):
    """کدینگ حساب‌ها (Chart of Accounts)"""
    __tablename__ = "chart_of_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    
    account_type = Column(SQLEnum(AccountType), nullable=False)
    parent_id = Column(Integer, ForeignKey("chart_of_accounts.id"))
    level = Column(Integer, default=1)  # 1=کل, 2=معین, 3=تفصیلی
    
    # تنظیمات
    is_active = Column(Boolean, default=True)
    is_postable = Column(Boolean, default=True)  # آیا می‌توان سند زد؟
    
    # موجودی
    balance = Column(Float, default=0.0)
    debit_balance = Column(Float, default=0.0)
    credit_balance = Column(Float, default=0.0)
    
    description = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    
    parent = relationship("ChartOfAccount", remote_side=[id])
    journal_lines = relationship("JournalEntryLine", back_populates="account")


class JournalEntry(Base):
    """سند حسابداری (Journal Entry)"""
    __tablename__ = "journal_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    entry_number = Column(String(50), unique=True, nullable=False)
    
    entry_type = Column(SQLEnum(JournalEntryType), default=JournalEntryType.MANUAL)
    entry_date = Column(Date, nullable=False)
    
    description = Column(Text, nullable=False)
    notes = Column(Text)
    
    # مبالغ
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    
    # وضعیت
    status = Column(String(20), default="draft")  # draft, posted, cancelled
    is_posted = Column(Boolean, default=False)
    posted_at = Column(DateTime)
    posted_by = Column(Integer, ForeignKey("users.id"))
    
    # ارجاعات
    reference_type = Column(String(50))  # invoice, payment, payroll, etc.
    reference_id = Column(Integer)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    lines = relationship("JournalEntryLine", back_populates="journal_entry", cascade="all, delete-orphan")
    bank_transactions = relationship("BankTransaction", back_populates="journal_entry")


class JournalEntryLine(Base):
    """سطرهای سند حسابداری"""
    __tablename__ = "journal_entry_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("chart_of_accounts.id"), nullable=False)
    
    line_number = Column(Integer, nullable=False)
    description = Column(String(500))
    
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    
    # ابعاد تحلیلی
    cost_center = Column(String(100))
    project = Column(String(100))
    department = Column(String(100))
    
    journal_entry = relationship("JournalEntry", back_populates="lines")
    account = relationship("ChartOfAccount", back_populates="journal_lines")


class Asset(Base):
    """دارایی‌های شرکت"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    
    asset_type = Column(SQLEnum(AssetType), nullable=False)
    category = Column(String(100))
    
    # اطلاعات مالی
    purchase_date = Column(Date, nullable=False)
    purchase_cost = Column(Float, nullable=False)
    current_value = Column(Float)
    salvage_value = Column(Float, default=0.0)
    
    # استهلاک
    depreciation_method = Column(String(50), default="straight_line")
    useful_life_years = Column(Integer)
    accumulated_depreciation = Column(Float, default=0.0)
    last_depreciation_date = Column(Date)
    
    # موقعیت
    location = Column(String(200))
    department = Column(String(100))
    responsible_person = Column(String(200))
    
    # وضعیت
    status = Column(String(50), default="active")  # active, disposed, sold
    is_depreciable = Column(Boolean, default=True)
    
    # اطلاعات تکمیلی
    serial_number = Column(String(100))
    manufacturer = Column(String(200))
    model = Column(String(100))
    warranty_until = Column(Date)
    
    description = Column(Text)
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class PettyCash(Base):
    """تنخواه گردان"""
    __tablename__ = "petty_cash"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_name = Column(String(200), nullable=False)
    custodian_name = Column(String(200))  # مسئول تنخواه
    
    authorized_amount = Column(Float, default=0.0)
    current_balance = Column(Float, default=0.0)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    
    transactions = relationship("PettyCashTransaction", back_populates="petty_cash")


class PettyCashTransaction(Base):
    """تراکنش‌های تنخواه"""
    __tablename__ = "petty_cash_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    petty_cash_id = Column(Integer, ForeignKey("petty_cash.id"), nullable=False)
    
    transaction_type = Column(String(20), nullable=False)  # deposit, expense, reimbursement
    amount = Column(Float, nullable=False)
    
    transaction_date = Column(Date, nullable=False)
    description = Column(Text, nullable=False)
    
    receipt_number = Column(String(100))
    receipt_image_url = Column(String(500))
    
    category = Column(String(100))  # office supplies, transportation, etc.
    
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"))
    
    created_at = Column(DateTime, server_default=func.now())
    
    petty_cash = relationship("PettyCash", back_populates="transactions")


class AccountsReceivable(Base):
    """حساب‌های دریافتنی"""
    __tablename__ = "accounts_receivable"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(200), nullable=False)
    customer_id = Column(Integer, ForeignKey("users.id"))
    
    invoice_number = Column(String(50))
    invoice_date = Column(Date)
    due_date = Column(Date)
    
    amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, nullable=False)
    
    status = Column(String(20), default="open")  # open, partial, paid, overdue
    
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class AccountsPayable(Base):
    """حساب‌های پرداختنی"""
    __tablename__ = "accounts_payable"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_name = Column(String(200), nullable=False)
    
    invoice_number = Column(String(50))
    invoice_date = Column(Date)
    due_date = Column(Date)
    
    amount = Column(Float, nullable=False)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, nullable=False)
    
    status = Column(String(20), default="open")  # open, partial, paid, overdue
    
    notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

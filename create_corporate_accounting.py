#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB_DIR = ROOT / "apps" / "web" / "src"

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   + {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")

def main():
    print("Creating Corporate Accounting System...")
    print("=" * 70)

    # =========================================================================
    # 1. Models - Corporate Accounting
    # =========================================================================
    print("\n[1] Creating corporate accounting models...")
    
    models_content = '''# api/modules/accounting/models.py
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
'''
    
    write_file(API_DIR / "modules" / "accounting" / "models.py", models_content)

    # =========================================================================
    # 2. Router - Corporate Accounting
    # =========================================================================
    print("\n[2] Creating corporate accounting router...")
    
    router_content = '''# api/modules/accounting/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.accounting.models import (
    BankAccount, BankTransaction, ChartOfAccount, JournalEntry, JournalEntryLine,
    Asset, PettyCash, PettyCashTransaction, AccountsReceivable, AccountsPayable,
    AccountType, JournalEntryType, AssetType
)

router = APIRouter(prefix="/accounting", tags=["Corporate Accounting"])


# =========================================================================
# Pydantic Models
# =========================================================================
class BankAccountCreate(BaseModel):
    account_name: str
    bank_name: str
    account_number: str
    sheba_number: Optional[str] = None
    branch_name: Optional[str] = None
    branch_code: Optional[str] = None
    account_type: str = "current"
    currency: str = "IRR"
    balance: float = 0.0
    credit_limit: float = 0.0
    is_primary: bool = False
    description: Optional[str] = None


class BankTransactionCreate(BaseModel):
    bank_account_id: int
    transaction_type: str  # deposit, withdrawal, transfer
    amount: float
    transaction_date: str
    reference_number: Optional[str] = None
    tracking_code: Optional[str] = None
    check_number: Optional[str] = None
    counterparty_name: Optional[str] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class JournalEntryCreate(BaseModel):
    entry_date: str
    description: str
    notes: Optional[str] = None
    lines: List[dict]  # [{account_id, debit, credit, description}]


class AssetCreate(BaseModel):
    asset_code: str
    name: str
    name_en: Optional[str] = None
    asset_type: str
    category: Optional[str] = None
    purchase_date: str
    purchase_cost: float
    salvage_value: float = 0.0
    depreciation_method: str = "straight_line"
    useful_life_years: Optional[int] = None
    location: Optional[str] = None
    department: Optional[str] = None
    responsible_person: Optional[str] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    description: Optional[str] = None


class PettyCashCreate(BaseModel):
    fund_name: str
    custodian_name: Optional[str] = None
    authorized_amount: float
    current_balance: float = 0.0


# =========================================================================
# Bank Accounts
# =========================================================================
@router.get("/bank-accounts")
async def list_bank_accounts(db: AsyncSession = Depends(get_db)):
    """لیست حساب‌های بانکی"""
    result = await db.execute(select(BankAccount).where(BankAccount.is_active == True))
    accounts = result.scalars().all()
    
    return {
        "accounts": [
            {
                "id": a.id,
                "account_name": a.account_name,
                "bank_name": a.bank_name,
                "account_number": a.account_number,
                "sheba_number": a.sheba_number,
                "branch_name": a.branch_name,
                "account_type": a.account_type,
                "currency": a.currency,
                "balance": a.balance,
                "credit_limit": a.credit_limit,
                "is_primary": a.is_primary,
            }
            for a in accounts
        ],
        "total_balance": sum(a.balance for a in accounts),
    }


@router.post("/bank-accounts")
async def create_bank_account(data: BankAccountCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد حساب بانکی جدید"""
    account = BankAccount(**data.dict())
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    return {"id": account.id, "account_number": account.account_number, "status": "created"}


@router.get("/bank-accounts/{account_id}")
async def get_bank_account(account_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت جزئیات حساب بانکی"""
    result = await db.execute(select(BankAccount).where(BankAccount.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(404, "حساب بانکی یافت نشد")
    
    # دریافت تراکنش‌ها
    tx_result = await db.execute(
        select(BankTransaction)
        .where(BankTransaction.bank_account_id == account_id)
        .order_by(desc(BankTransaction.transaction_date))
        .limit(50)
    )
    transactions = tx_result.scalars().all()
    
    return {
        "account": {
            "id": account.id,
            "account_name": account.account_name,
            "bank_name": account.bank_name,
            "account_number": account.account_number,
            "sheba_number": account.sheba_number,
            "branch_name": account.branch_name,
            "account_type": account.account_type,
            "balance": account.balance,
            "credit_limit": account.credit_limit,
        },
        "transactions": [
            {
                "id": t.id,
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "transaction_date": t.transaction_date,
                "reference_number": t.reference_number,
                "counterparty_name": t.counterparty_name,
                "description": t.description,
            }
            for t in transactions
        ],
    }


@router.post("/bank-transactions")
async def create_bank_transaction(data: BankTransactionCreate, db: AsyncSession = Depends(get_db)):
    """ثبت تراکنش بانکی (واریز/برداشت)"""
    # دریافت حساب بانکی
    result = await db.execute(select(BankAccount).where(BankAccount.id == data.bank_account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(404, "حساب بانکی یافت نشد")
    
    # به‌روزرسانی موجودی
    if data.transaction_type == "deposit":
        account.balance += data.amount
    elif data.transaction_type == "withdrawal":
        if account.balance < data.amount:
            raise HTTPException(400, "موجودی کافی نیست")
        account.balance -= data.amount
    
    # ثبت تراکنش
    transaction = BankTransaction(
        bank_account_id=data.bank_account_id,
        transaction_type=data.transaction_type,
        amount=data.amount,
        transaction_date=datetime.fromisoformat(data.transaction_date),
        reference_number=data.reference_number,
        tracking_code=data.tracking_code,
        check_number=data.check_number,
        counterparty_name=data.counterparty_name,
        description=data.description,
        notes=data.notes,
    )
    
    db.add(transaction)
    await db.commit()
    
    return {
        "id": transaction.id,
        "new_balance": account.balance,
        "status": "created"
    }


# =========================================================================
# Chart of Accounts
# =========================================================================
@router.get("/chart-of-accounts")
async def list_chart_of_accounts(account_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """لیست کدینگ حساب‌ها"""
    query = select(ChartOfAccount).where(ChartOfAccount.is_active == True)
    
    if account_type:
        query = query.where(ChartOfAccount.account_type == AccountType(account_type))
    
    result = await db.execute(query.order_by(ChartOfAccount.code))
    accounts = result.scalars().all()
    
    return {
        "accounts": [
            {
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "name_en": a.name_en,
                "account_type": a.account_type.value,
                "level": a.level,
                "balance": a.balance,
                "is_postable": a.is_postable,
            }
            for a in accounts
        ]
    }


@router.post("/chart-of-accounts")
async def create_account(data: dict, db: AsyncSession = Depends(get_db)):
    """ایجاد حساب جدید"""
    account = ChartOfAccount(**data)
    db.add(account)
    await db.commit()
    return {"id": account.id, "code": account.code, "status": "created"}


# =========================================================================
# Journal Entries (اسناد حسابداری)
# =========================================================================
@router.get("/journal-entries")
async def list_journal_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """لیست اسناد حسابداری"""
    query = select(JournalEntry)
    
    if start_date:
        query = query.where(JournalEntry.entry_date >= date.fromisoformat(start_date))
    if end_date:
        query = query.where(JournalEntry.entry_date <= date.fromisoformat(end_date))
    if status:
        query = query.where(JournalEntry.status == status)
    
    result = await db.execute(query.order_by(desc(JournalEntry.entry_date)))
    entries = result.scalars().all()
    
    return {
        "entries": [
            {
                "id": e.id,
                "entry_number": e.entry_number,
                "entry_type": e.entry_type.value,
                "entry_date": e.entry_date,
                "description": e.description,
                "total_debit": e.total_debit,
                "total_credit": e.total_credit,
                "status": e.status,
                "is_posted": e.is_posted,
            }
            for e in entries
        ]
    }


@router.post("/journal-entries")
async def create_journal_entry(data: JournalEntryCreate, db: AsyncSession = Depends(get_db)):
    """ثبت سند حسابداری (دوطرفه)"""
    # تولید شماره سند
    entry_number = f"JE-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    
    # محاسبه جمع بدهکار و بستانکار
    total_debit = sum(line.get("debit", 0) for line in data.lines)
    total_credit = sum(line.get("credit", 0) for line in data.lines)
    
    # بررسی تراز بودن سند
    if abs(total_debit - total_credit) > 0.01:
        raise HTTPException(400, f"سند تراز نیست. بدهکار: {total_debit}, بستانکار: {total_credit}")
    
    # ایجاد سند
    entry = JournalEntry(
        entry_number=entry_number,
        entry_type=JournalEntryType.MANUAL,
        entry_date=date.fromisoformat(data.entry_date),
        description=data.description,
        notes=data.notes,
        total_debit=total_debit,
        total_credit=total_credit,
        status="draft",
    )
    
    db.add(entry)
    await db.flush()
    
    # ایجاد سطرهای سند
    for idx, line_data in enumerate(data.lines, 1):
        line = JournalEntryLine(
            journal_entry_id=entry.id,
            account_id=line_data["account_id"],
            line_number=idx,
            description=line_data.get("description"),
            debit=line_data.get("debit", 0),
            credit=line_data.get("credit", 0),
            cost_center=line_data.get("cost_center"),
            project=line_data.get("project"),
            department=line_data.get("department"),
        )
        db.add(line)
    
    await db.commit()
    
    return {
        "id": entry.id,
        "entry_number": entry_number,
        "total_debit": total_debit,
        "total_credit": total_credit,
        "status": "created"
    }


@router.post("/journal-entries/{entry_id}/post")
async def post_journal_entry(entry_id: int, user_id: int, db: AsyncSession = Depends(get_db)):
    """ثبت قطعی سند و به‌روزرسانی حساب‌ها"""
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(404, "سند یافت نشد")
    
    if entry.is_posted:
        raise HTTPException(400, "سند قبلاً ثبت شده است")
    
    # به‌روزرسانی موجودی حساب‌ها
    for line in entry.lines:
        account_result = await db.execute(select(ChartOfAccount).where(ChartOfAccount.id == line.account_id))
        account = account_result.scalar_one()
        
        account.debit_balance += line.debit
        account.credit_balance += line.credit
        account.balance = account.debit_balance - account.credit_balance
    
    # به‌روزرسانی وضعیت سند
    entry.is_posted = True
    entry.status = "posted"
    entry.posted_at = datetime.now()
    entry.posted_by = user_id
    
    await db.commit()
    
    return {"status": "posted", "entry_id": entry_id}


@router.get("/journal-entries/{entry_id}")
async def get_journal_entry(entry_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت جزئیات سند"""
    result = await db.execute(select(JournalEntry).where(JournalEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    
    if not entry:
        raise HTTPException(404, "سند یافت نشد")
    
    return {
        "entry": {
            "id": entry.id,
            "entry_number": entry.entry_number,
            "entry_type": entry.entry_type.value,
            "entry_date": entry.entry_date,
            "description": entry.description,
            "total_debit": entry.total_debit,
            "total_credit": entry.total_credit,
            "status": entry.status,
            "is_posted": entry.is_posted,
        },
        "lines": [
            {
                "id": l.id,
                "line_number": l.line_number,
                "account_code": l.account.code,
                "account_name": l.account.name,
                "description": l.description,
                "debit": l.debit,
                "credit": l.credit,
                "cost_center": l.cost_center,
                "project": l.project,
            }
            for l in entry.lines
        ],
    }


# =========================================================================
# Assets
# =========================================================================
@router.get("/assets")
async def list_assets(asset_type: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """لیست دارایی‌ها"""
    query = select(Asset)
    
    if asset_type:
        query = query.where(Asset.asset_type == AssetType(asset_type))
    
    result = await db.execute(query)
    assets = result.scalars().all()
    
    return {
        "assets": [
            {
                "id": a.id,
                "asset_code": a.asset_code,
                "name": a.name,
                "asset_type": a.asset_type.value,
                "category": a.category,
                "purchase_date": a.purchase_date,
                "purchase_cost": a.purchase_cost,
                "current_value": a.current_value or a.purchase_cost,
                "accumulated_depreciation": a.accumulated_depreciation,
                "location": a.location,
                "department": a.department,
                "status": a.status,
            }
            for a in assets
        ],
        "total_value": sum(a.purchase_cost for a in assets),
        "total_depreciation": sum(a.accumulated_depreciation for a in assets),
    }


@router.post("/assets")
async def create_asset(data: AssetCreate, db: AsyncSession = Depends(get_db)):
    """ثبت دارایی جدید"""
    asset = Asset(
        **data.dict(),
        purchase_date=date.fromisoformat(data.purchase_date),
        current_value=data.purchase_cost,
    )
    db.add(asset)
    await db.commit()
    
    return {"id": asset.id, "asset_code": asset.asset_code, "status": "created"}


# =========================================================================
# Petty Cash
# =========================================================================
@router.get("/petty-cash")
async def list_petty_cash(db: AsyncSession = Depends(get_db)):
    """لیست تنخواه‌ها"""
    result = await db.execute(select(PettyCash).where(PettyCash.is_active == True))
    funds = result.scalars().all()
    
    return {
        "funds": [
            {
                "id": f.id,
                "fund_name": f.fund_name,
                "custodian_name": f.custodian_name,
                "authorized_amount": f.authorized_amount,
                "current_balance": f.current_balance,
            }
            for f in funds
        ]
    }


@router.post("/petty-cash")
async def create_petty_cash(data: PettyCashCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد تنخواه جدید"""
    fund = PettyCash(**data.dict())
    db.add(fund)
    await db.commit()
    
    return {"id": fund.id, "fund_name": fund.fund_name, "status": "created"}


# =========================================================================
# Reports
# =========================================================================
@router.get("/reports/trial-balance")
async def trial_balance_report(db: AsyncSession = Depends(get_db)):
    """تراز آزمایشی"""
    result = await db.execute(
        select(ChartOfAccount).where(ChartOfAccount.is_active == True).order_by(ChartOfAccount.code)
    )
    accounts = result.scalars().all()
    
    total_debit = sum(a.debit_balance for a in accounts if a.debit_balance > 0)
    total_credit = sum(a.credit_balance for a in accounts if a.credit_balance > 0)
    
    return {
        "accounts": [
            {
                "code": a.code,
                "name": a.name,
                "account_type": a.account_type.value,
                "debit_balance": a.debit_balance,
                "credit_balance": a.credit_balance,
            }
            for a in accounts
        ],
        "total_debit": total_debit,
        "total_credit": total_credit,
        "is_balanced": abs(total_debit - total_credit) < 0.01,
    }


@router.get("/reports/balance-sheet")
async def balance_sheet_report(db: AsyncSession = Depends(get_db)):
    """ترازنامه"""
    result = await db.execute(select(ChartOfAccount).where(ChartOfAccount.is_active == True))
    accounts = result.scalars().all()
    
    assets = sum(a.balance for a in accounts if a.account_type == AccountType.ASSET)
    liabilities = sum(abs(a.balance) for a in accounts if a.account_type == AccountType.LIABILITY)
    equity = sum(abs(a.balance) for a in accounts if a.account_type == AccountType.EQUITY)
    
    return {
        "assets": assets,
        "liabilities": liabilities,
        "equity": equity,
        "total_liabilities_and_equity": liabilities + equity,
        "is_balanced": abs(assets - (liabilities + equity)) < 0.01,
    }


@router.get("/reports/income-statement")
async def income_statement_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """صورت سود و زیان"""
    # محاسبه درآمد و هزینه از سطرهای اسناد ثبت‌شده
    query = select(JournalEntryLine).join(JournalEntry).where(JournalEntry.is_posted == True)
    
    if start_date:
        query = query.where(JournalEntry.entry_date >= date.fromisoformat(start_date))
    if end_date:
        query = query.where(JournalEntry.entry_date <= date.fromisoformat(end_date))
    
    result = await db.execute(query)
    lines = result.scalars().all()
    
    revenue = 0
    expenses = 0
    
    for line in lines:
        if line.account.account_type == AccountType.REVENUE:
            revenue += line.credit - line.debit
        elif line.account.account_type == AccountType.EXPENSE:
            expenses += line.debit - line.credit
    
    net_income = revenue - expenses
    
    return {
        "revenue": revenue,
        "expenses": expenses,
        "net_income": net_income,
        "period": {"start": start_date, "end": end_date},
    }
'''
    
    write_file(API_DIR / "modules" / "accounting" / "router.py", router_content)

    # =========================================================================
    # 3. __init__.py
    # =========================================================================
    print("\n[3] Creating __init__.py...")
    write_file(API_DIR / "modules" / "accounting" / "__init__.py", "from . import models, router\n")

    # =========================================================================
    # 4. Update main.py
    # =========================================================================
    print("\n[4] Updating main.py...")
    main_path = API_DIR / "main.py"
    
    if main_path.exists():
        content = main_path.read_text(encoding="utf-8")
        
        if "accounting_router" not in content:
            lines = content.split('\n')
            import_idx = router_idx = 0
            
            for i, line in enumerate(lines):
                if line.startswith("from api.modules."):
                    import_idx = i
                if "app.include_router(" in line:
                    router_idx = i
            
            lines.insert(import_idx + 1, "from api.modules.accounting.router import router as accounting_router")
            lines.insert(router_idx + 2, 'app.include_router(accounting_router, prefix="/api/v1")')
            
            main_path.write_text('\n'.join(lines), encoding="utf-8")
            print("   + accounting_router added")

    # =========================================================================
    # 5. Frontend - Corporate Accounting Dashboard
    # =========================================================================
    print("\n[5] Creating corporate accounting frontend...")
    
    frontend_content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Building2, Landmark, Wallet, FileText, TrendingUp,
  Plus, Edit, Trash2, Eye, Download, Filter, Search, Calendar,
  AlertTriangle, CheckCircle, Clock, Package, Briefcase,
  FileSignature, PiggyBank, CreditCard, Receipt, Calculator,
  X, Save, ChevronDown, ChevronRight, DollarSign, BarChart3,
  ArrowUpCircle, ArrowDownCircle, BookOpen, Scale, Target
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/accounting";

export default function CorporateAccountingPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [bankAccounts, setBankAccounts] = useState<any[]>([]);
  const [journalEntries, setJournalEntries] = useState<any[]>([]);
  const [assets, setAssets] = useState<any[]>([]);
  const [chartOfAccounts, setChartOfAccounts] = useState<any[]>([]);
  const [showModal, setShowModal] = useState<string | null>(null);
  const [selectedAccount, setSelectedAccount] = useState<any>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [bankRes, journalRes, assetRes, chartRes] = await Promise.all([
        fetch(`${API_BASE}/bank-accounts`),
        fetch(`${API_BASE}/journal-entries`),
        fetch(`${API_BASE}/assets`),
        fetch(`${API_BASE}/chart-of-accounts`),
      ]);
      
      if (bankRes.ok) setBankAccounts((await bankRes.json()).accounts || []);
      if (journalRes.ok) setJournalEntries((await journalRes.json()).entries || []);
      if (assetRes.ok) setAssets((await assetRes.json()).assets || []);
      if (chartRes.ok) setChartOfAccounts((await chartRes.json()).accounts || []);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#3b82f6" },
    { id: "bank", label: "حساب‌های بانکی", icon: Landmark, color: "#10b981" },
    { id: "journal", label: "اسناد حسابداری", icon: FileText, color: "#f59e0b" },
    { id: "chart", label: "کدینگ حساب‌ها", icon: BookOpen, color: "#8b5cf6" },
    { id: "assets", label: "دارایی‌ها", icon: Package, color: "#ec4899" },
    { id: "reports", label: "گزارش‌ها", icon: TrendingUp, color: "#06b6d4" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-2xl">
                <Building2 className="h-10 w-10 text-white" />
              </div>
              <div>
                <p className="text-blue-400 text-sm font-medium mb-1">سیستم حسابداری شرکتی</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">حسابداری یکپارچه</h1>
                <p className="text-lg text-slate-300">مدیریت مالی کامل شرکت با حسابداری دوطرفه</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 rounded-xl font-bold transition-all flex items-center gap-2 text-sm ${
                activeTab === tab.id ? "text-white shadow-lg" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={activeTab === tab.id ? { backgroundColor: tab.color, boxShadow: `0 10px 25px -5px ${tab.color}50` } : {}}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Landmark className="h-6 w-6 mb-2 text-emerald-400" />
                <p className="text-2xl font-black text-white">{bankAccounts.length}</p>
                <p className="text-xs text-slate-400">حساب‌های بانکی</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <FileText className="h-6 w-6 mb-2 text-amber-400" />
                <p className="text-2xl font-black text-white">{journalEntries.length}</p>
                <p className="text-xs text-slate-400">اسناد حسابداری</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Package className="h-6 w-6 mb-2 text-pink-400" />
                <p className="text-2xl font-black text-white">{assets.length}</p>
                <p className="text-xs text-slate-400">دارایی‌ها</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <BookOpen className="h-6 w-6 mb-2 text-purple-400" />
                <p className="text-2xl font-black text-white">{chartOfAccounts.length}</p>
                <p className="text-xs text-slate-400">حساب‌های کل</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Landmark className="h-5 w-5 text-emerald-400" />
                  موجودی حساب‌های بانکی
                </h3>
                <div className="space-y-3">
                  {bankAccounts.slice(0, 5).map(account => (
                    <div key={account.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                      <div>
                        <p className="font-bold text-white">{account.account_name}</p>
                        <p className="text-xs text-slate-400">{account.bank_name} - {account.account_number}</p>
                      </div>
                      <p className="text-lg font-black text-emerald-400">{account.balance.toLocaleString()}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <FileText className="h-5 w-5 text-amber-400" />
                  آخرین اسناد حسابداری
                </h3>
                <div className="space-y-3">
                  {journalEntries.slice(0, 5).map(entry => (
                    <div key={entry.id} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                      <div>
                        <p className="font-bold text-white">{entry.entry_number}</p>
                        <p className="text-xs text-slate-400">{entry.description}</p>
                      </div>
                      <div className="text-left">
                        <p className="text-sm font-bold text-amber-400">{entry.total_debit.toLocaleString()}</p>
                        <p className="text-xs text-slate-500">{entry.entry_date}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Bank Accounts */}
        {activeTab === "bank" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">حساب‌های بانکی</h2>
              <button onClick={() => setShowModal("bank_account")} className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> حساب بانکی جدید
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {bankAccounts.map(account => (
                <motion.div
                  key={account.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6 hover:border-emerald-500/50 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <Landmark className="h-8 w-8 text-emerald-400" />
                    {account.is_primary && (
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs font-bold">اصلی</span>
                    )}
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{account.account_name}</h3>
                  <p className="text-sm text-slate-400 mb-4">{account.bank_name}</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">شماره حساب:</span>
                      <span className="text-white font-mono">{account.account_number}</span>
                    </div>
                    {account.sheba_number && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">شبا:</span>
                        <span className="text-white font-mono text-xs">{account.sheba_number}</span>
                      </div>
                    )}
                  </div>
                  <div className="pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-400 mb-1">موجودی</p>
                    <p className="text-2xl font-black text-emerald-400">{account.balance.toLocaleString()} {account.currency}</p>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <button onClick={() => { setSelectedAccount(account); setShowModal("bank_transaction"); }} className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold">
                      تراکنش جدید
                    </button>
                    <button className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg">
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Journal Entries */}
        {activeTab === "journal" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">اسناد حسابداری</h2>
              <button onClick={() => setShowModal("journal_entry")} className="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> سند جدید
              </button>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">شماره سند</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">تاریخ</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">توضیحات</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">بدهکار</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">بستانکار</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">وضعیت</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {journalEntries.map(entry => (
                    <tr key={entry.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono text-sm">{entry.entry_number}</td>
                      <td className="px-6 py-4 text-slate-300">{entry.entry_date}</td>
                      <td className="px-6 py-4 text-slate-300 text-sm">{entry.description}</td>
                      <td className="px-6 py-4 text-amber-400 font-bold">{entry.total_debit.toLocaleString()}</td>
                      <td className="px-6 py-4 text-emerald-400 font-bold">{entry.total_credit.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          entry.status === "posted" ? "bg-emerald-500/20 text-emerald-300" :
                          entry.status === "draft" ? "bg-amber-500/20 text-amber-300" :
                          "bg-slate-500/20 text-slate-300"
                        }`}>
                          {entry.status === "posted" ? "ثبت شده" : entry.status === "draft" ? "پیش‌نویس" : entry.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg"><Eye className="h-4 w-4" /></button>
                          {!entry.is_posted && (
                            <button className="px-3 py-1 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold">ثبت</button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Chart of Accounts */}
        {activeTab === "chart" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">کدینگ حساب‌ها</h2>
              <button onClick={() => setShowModal("account")} className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> حساب جدید
              </button>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">کد</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نام حساب</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نوع</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">سطح</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">موجودی</th>
                  </tr>
                </thead>
                <tbody>
                  {chartOfAccounts.map(account => (
                    <tr key={account.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono">{account.code}</td>
                      <td className="px-6 py-4 text-white">{account.name}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded text-xs font-bold ${
                          account.account_type === "asset" ? "bg-blue-500/20 text-blue-300" :
                          account.account_type === "liability" ? "bg-red-500/20 text-red-300" :
                          account.account_type === "equity" ? "bg-purple-500/20 text-purple-300" :
                          account.account_type === "revenue" ? "bg-emerald-500/20 text-emerald-300" :
                          "bg-amber-500/20 text-amber-300"
                        }`}>
                          {account.account_type === "asset" ? "دارایی" :
                           account.account_type === "liability" ? "بدهی" :
                           account.account_type === "equity" ? "حقوق" :
                           account.account_type === "revenue" ? "درآمد" : "هزینه"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-300">{account.level}</td>
                      <td className="px-6 py-4 text-white font-bold">{account.balance.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Assets */}
        {activeTab === "assets" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">دارایی‌ها</h2>
              <button onClick={() => setShowModal("asset")} className="px-6 py-3 bg-pink-600 hover:bg-pink-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> دارایی جدید
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {assets.map(asset => (
                <motion.div
                  key={asset.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-pink-500/50 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <Package className="h-8 w-8 text-pink-400" />
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      asset.status === "active" ? "bg-emerald-500/20 text-emerald-300" :
                      "bg-slate-500/20 text-slate-300"
                    }`}>
                      {asset.status === "active" ? "فعال" : asset.status}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{asset.name}</h3>
                  <p className="text-sm text-slate-400 mb-4">{asset.asset_type} - {asset.category}</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">بهای تمام‌شده:</span>
                      <span className="text-white font-bold">{asset.purchase_cost.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">استهلاک انباشته:</span>
                      <span className="text-red-400">{asset.accumulated_depreciation.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">ارزش دفتری:</span>
                      <span className="text-emerald-400 font-bold">{(asset.purchase_cost - asset.accumulated_depreciation).toLocaleString()}</span>
                    </div>
                  </div>
                  {asset.location && (
                    <p className="text-xs text-slate-500 mb-2">موقعیت: {asset.location}</p>
                  )}
                  {asset.department && (
                    <p className="text-xs text-slate-500">واحد: {asset.department}</p>
                  )}
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Reports */}
        {activeTab === "reports" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <Scale className="h-8 w-8 text-cyan-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">تراز آزمایشی</h3>
              <p className="text-sm text-slate-400 mb-4">بررسی تراز بودن حساب‌ها</p>
              <button className="w-full py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded-lg font-bold">مشاهده گزارش</button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <BarChart3 className="h-8 w-8 text-blue-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">ترازنامه</h3>
              <p className="text-sm text-slate-400 mb-4">وضعیت دارایی‌ها، بدهی‌ها و حقوق</p>
              <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold">مشاهده ترازنامه</button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <TrendingUp className="h-8 w-8 text-emerald-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">صورت سود و زیان</h3>
              <p className="text-sm text-slate-400 mb-4">درآمد، هزینه و سود خالص</p>
              <button className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold">مشاهده سود و زیان</button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <DollarSign className="h-8 w-8 text-amber-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">جریان وجوه نقد</h3>
              <p className="text-sm text-slate-400 mb-4">ورودی و خروجی وجه نقد</p>
              <button className="w-full py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">مشاهده جریان نقد</button>
            </div>
          </div>
        )}
      </section>

      {/* Modals */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowModal(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  {showModal === "bank_account" && "حساب بانکی جدید"}
                  {showModal === "bank_transaction" && "تراکنش بانکی"}
                  {showModal === "journal_entry" && "سند حسابداری جدید"}
                  {showModal === "account" && "حساب جدید"}
                  {showModal === "asset" && "دارایی جدید"}
                </h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {showModal === "bank_account" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام حساب *</label>
                      <input type="text" placeholder="مثال: حساب جاری اصلی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام بانک *</label>
                      <input type="text" placeholder="مثال: بانک ملت" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">شماره حساب *</label>
                      <input type="text" placeholder="شماره حساب" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" dir="ltr" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">شماره شبا</label>
                      <input type="text" placeholder="IR..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" dir="ltr" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام شعبه</label>
                      <input type="text" placeholder="شعبه مرکزی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نوع حساب</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="current">جاری</option>
                        <option value="savings">پس‌انداز</option>
                        <option value="deposit">سپرده</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موجودی اولیه</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">سقف اعتبار</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <button className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ایجاد حساب بانکی
                  </button>
                </div>
              )}

              {showModal === "bank_transaction" && selectedAccount && (
                <div className="space-y-4">
                  <div className="bg-slate-800/50 rounded-xl p-4 mb-4">
                    <p className="text-sm text-slate-400">حساب بانکی:</p>
                    <p className="text-lg font-bold text-white">{selectedAccount.account_name}</p>
                    <p className="text-sm text-slate-400">موجودی فعلی: {selectedAccount.balance.toLocaleString()}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نوع تراکنش *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option value="deposit">واریز</option>
                      <option value="withdrawal">برداشت</option>
                      <option value="transfer">انتقال</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مبلغ *</label>
                    <input type="number" placeholder="مبلغ تراکنش" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">تاریخ *</label>
                    <input type="date" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">شماره پیگیری</label>
                    <input type="text" placeholder="شماره referencia" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نام طرف حساب</label>
                    <input type="text" placeholder="نام شخص یا شرکت" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                    <textarea rows={3} placeholder="توضیحات تراکنش..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ثبت تراکنش
                  </button>
                </div>
              )}

              {showModal === "journal_entry" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">تاریخ سند *</label>
                      <input type="date" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نوع سند</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="manual">دستی</option>
                        <option value="auto">خودکار</option>
                        <option value="adjustment">تعدیلی</option>
                      </select>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات *</label>
                    <textarea rows={2} placeholder="توضیحات سند..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  
                  <div className="border-t border-slate-700 pt-4">
                    <h4 className="font-bold text-white mb-3">سطرهای سند (حسابداری دوطرفه)</h4>
                    <div className="space-y-3">
                      <div className="grid grid-cols-12 gap-2 text-xs text-slate-400 font-bold">
                        <div className="col-span-4">حساب</div>
                        <div className="col-span-4">توضیحات</div>
                        <div className="col-span-2">بدهکار</div>
                        <div className="col-span-2">بستانکار</div>
                      </div>
                      {[1, 2].map(i => (
                        <div key={i} className="grid grid-cols-12 gap-2">
                          <select className="col-span-4 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm">
                            <option>انتخاب حساب...</option>
                            {chartOfAccounts.map(acc => (
                              <option key={acc.id} value={acc.id}>{acc.code} - {acc.name}</option>
                            ))}
                          </select>
                          <input type="text" placeholder="توضیحات" className="col-span-4 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                          <input type="number" placeholder="0" className="col-span-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                          <input type="number" placeholder="0" className="col-span-2 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                        </div>
                      ))}
                    </div>
                    <button className="mt-3 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-bold">
                      + افزودن سطر
                    </button>
                  </div>

                  <button className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ایجاد سند
                  </button>
                </div>
              )}

              {showModal === "asset" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">کد دارایی *</label>
                      <input type="text" placeholder="مثال: FA-001" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام دارایی *</label>
                      <input type="text" placeholder="نام دارایی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نوع دارایی *</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option value="fixed">ثابت</option>
                        <option value="current">جاری</option>
                        <option value="intangible">نامشهود</option>
                        <option value="investment">سرمایه‌گذاری</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">دسته‌بندی</label>
                      <input type="text" placeholder="مثال: ساختمان، ماشین‌آلات" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">تاریخ خرید *</label>
                      <input type="date" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">بهای تمام‌شده *</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">ارزش اسقاط</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">عمر مفید (سال)</label>
                      <input type="number" placeholder="5" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موقعیت</label>
                      <input type="text" placeholder="ساختمان اصلی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">واحد مسئول</label>
                      <input type="text" placeholder="مالی" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <button className="w-full py-3 bg-pink-600 hover:bg-pink-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ثبت دارایی
                  </button>
                </div>
              )}
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''
    
    write_file(WEB_DIR / "app" / "accounting" / "page.tsx", frontend_content)

    # =========================================================================
    # 6. Clean cache
    # =========================================================================
    print("\n[6] Cleaning cache...")
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("   + .next removed")
        except Exception as e:
            print(f"   ! {e}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("DONE! Corporate Accounting System created successfully!")
    print("=" * 70)
    print("\nFeatures:")
    print("  + Bank Accounts (manual entry, no real connection needed)")
    print("  + Journal Entries (double-entry bookkeeping)")
    print("  + Chart of Accounts (multi-level)")
    print("  + Assets Management (fixed, current, intangible)")
    print("  + Petty Cash")
    print("  + Accounts Receivable/Payable")
    print("  + Reports (Trial Balance, Balance Sheet, Income Statement)")
    print("\nNext steps:")
    print("  1. uvicorn api.main:app --reload --port 8000")
    print("  2. cd apps\\web && pnpm run dev -- -p 3001")
    print("  3. Visit: http://localhost:3001/accounting")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())
# api/modules/accounting/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.accounting.models import (
    AccountsPayable,
    AccountsReceivable,
    AccountType,
    Asset,
    AssetType,
    BankAccount,
    BankTransaction,
    ChartOfAccount,
    JournalEntry,
    JournalEntryLine,
    JournalEntryType,
    PettyCash,
    PettyCashTransaction,
)



class BalanceSheetResponse(BaseModel):
    """Auto-generated response model for /reports/balance-sheet"""
    total_assets: float = 0.0
    total_liabilities: float = 0.0
    total_equity: float = 0.0
    report_date: str = ""
    assets: List[Any] = []
    liabilities: List[Any] = []


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
@router.get("/bank-accounts", response_model=Dict[str, Any])
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


@router.post("/bank-accounts", response_model=Dict[str, Any])
async def create_bank_account(data: BankAccountCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد حساب بانکی جدید"""
    account = BankAccount(**data.dict())
    db.add(account)
    await db.commit()
    await db.refresh(account)

    return {"id": account.id, "account_number": account.account_number, "status": "created"}


@router.get("/bank-accounts/{account_id}", response_model=IDResponse)
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


@router.post("/bank-transactions", response_model=Dict[str, Any])
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

    return {"id": transaction.id, "new_balance": account.balance, "status": "created"}


# =========================================================================
# Chart of Accounts
# =========================================================================
@router.get("/chart-of-accounts", response_model=IDResponse)
async def list_chart_of_accounts(
    account_type: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
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


@router.post("/chart-of-accounts", response_model=Dict[str, Any])
async def create_account(data: dict, db: AsyncSession = Depends(get_db)):
    """ایجاد حساب جدید"""
    account = ChartOfAccount(**data)
    db.add(account)
    await db.commit()
    return {"id": account.id, "code": account.code, "status": "created"}


# =========================================================================
# Journal Entries (اسناد حسابداری)
# =========================================================================
@router.get("/journal-entries", response_model=IDResponse)
async def list_journal_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
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


@router.post("/journal-entries", response_model=Dict[str, Any])
async def create_journal_entry(data: JournalEntryCreate, db: AsyncSession = Depends(get_db)):
    """ثبت سند حسابداری (دوطرفه)"""
    # تولید شماره سند
    entry_number = (
        f"JE-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    )

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
        "status": "created",
    }


@router.post("/journal-entries/{entry_id}/post", response_model=IDResponse)
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
        account_result = await db.execute(
            select(ChartOfAccount).where(ChartOfAccount.id == line.account_id)
        )
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


@router.get("/journal-entries/{entry_id}", response_model=Dict[str, Any])
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
@router.get("/assets", response_model=Dict[str, Any])
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


@router.post("/assets", response_model=Dict[str, Any])
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
@router.get("/petty-cash", response_model=IDResponse)
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


@router.post("/petty-cash", response_model=Dict[str, Any])
async def create_petty_cash(data: PettyCashCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد تنخواه جدید"""
    fund = PettyCash(**data.dict())
    db.add(fund)
    await db.commit()

    return {"id": fund.id, "fund_name": fund.fund_name, "status": "created"}


# =========================================================================
# Reports
# =========================================================================
@router.get("/reports/trial-balance", response_model=IDResponse)
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


@router.get("/reports/balance-sheet", response_model=BalanceSheetResponse)
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


@router.get("/reports/income-statement", response_model=Dict[str, Any])
async def income_statement_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
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

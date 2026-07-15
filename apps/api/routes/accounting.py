"""ماژول حسابداری Econojin"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

router = APIRouter(prefix="/api/accounting", tags=["accounting"])


class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    ECO_REWARD = "eco_reward"
    CARBON_CREDIT = "carbon_credit"


class Transaction(BaseModel):
    id: Optional[str] = None
    type: TransactionType
    amount: float
    currency: str = "ECO"
    description: str
    category: str
    date: datetime
    status: str = "confirmed"


_sample_tx = [
    {"id": "TX001", "type": "eco_reward", "amount": 45.5, "currency": "ECO",
     "description": "مراقبت روزانه - آمازون", "category": "stewardship",
     "date": "2026-07-14T10:00:00", "status": "confirmed"},
    {"id": "TX002", "type": "carbon_credit", "amount": 1200, "currency": "USD",
     "description": "فروش اعتبار کربن", "category": "carbon_sales",
     "date": "2026-07-13T14:00:00", "status": "confirmed"},
    {"id": "TX003", "type": "expense", "amount": 350, "currency": "USD",
     "description": "هزینه ماهواره", "category": "operations",
     "date": "2026-07-12T09:00:00", "status": "confirmed"},
    {"id": "TX004", "type": "income", "amount": 5000, "currency": "USD",
     "description": "سرمایه‌گذاری ESG", "category": "investment",
     "date": "2026-07-11T16:00:00", "status": "confirmed"},
    {"id": "TX005", "type": "transfer", "amount": 100, "currency": "ECO",
     "description": "انتقال به کیف پول", "category": "transfer",
     "date": "2026-07-10T12:00:00", "status": "confirmed"},
]


@router.get("/transactions")
async def list_transactions(limit: int = 50, offset: int = 0, type: Optional[TransactionType] = None):
    result = _sample_tx
    if type:
        result = [t for t in result if t["type"] == type.value]
    return {"transactions": result[offset:offset+limit], "total": len(result)}


@router.get("/transactions/{tx_id}")
async def get_transaction(tx_id: str):
    for t in _sample_tx:
        if t["id"] == tx_id:
            return t
    raise HTTPException(status_code=404, detail="Not found")


@router.post("/transactions")
async def create_transaction(tx: Transaction):
    tx.id = f"TX{len(_sample_tx)+1:03d}"
    _sample_tx.append(tx.dict())
    return {"status": "created", "transaction": tx}


@router.get("/summary")
async def get_summary():
    return {
        "total_income": 6200.0,
        "total_expense": 350.0,
        "net_profit": 5850.0,
        "eco_rewards_distributed": 45.5,
        "carbon_credits_value": 1200.0,
        "transactions_count": len(_sample_tx),
    }


@router.get("/charts/income-expense")
async def get_income_expense_chart():
    return {
        "labels": ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور"],
        "income": [4500, 5200, 4800, 6200, 5800, 6500],
        "expense": [1200, 1100, 1350, 1400, 980, 1100],
        "profit": [3300, 4100, 3450, 4800, 4820, 5400],
    }


@router.get("/charts/category-distribution")
async def get_category_distribution():
    return [
        {"name": "مراقبت", "value": 35, "color": "#22c55e"},
        {"name": "کربن", "value": 25, "color": "#3b82f6"},
        {"name": "سرمایه‌گذاری", "value": 20, "color": "#a855f7"},
        {"name": "عملیات", "value": 12, "color": "#f59e0b"},
        {"name": "انتقال", "value": 8, "color": "#06b6d4"},
    ]


@router.get("/invoices")
async def list_invoices():
    return {"invoices": [
        {"id": "INV001", "number": "INV-2026-001", "client": "شرکت ESG",
         "amount": 5000, "total": 5750, "status": "paid",
         "issue_date": "2026-07-01", "due_date": "2026-07-15"},
        {"id": "INV002", "number": "INV-2026-002", "client": "سازمان محیط‌زیست",
         "amount": 3200, "total": 3680, "status": "pending",
         "issue_date": "2026-07-05", "due_date": "2026-07-20"},
    ]}


@router.get("/reports/download")
async def download_report(format: str = "json"):
    return {"format": format, "generated_at": datetime.now().isoformat()}


@router.post("/upload/statement")
async def upload_statement(file: UploadFile = File(...)):
    return {"status": "uploaded", "filename": file.filename, "size": file.size}


@router.get("/ledger")
async def get_ledger():
    return {"entries": _sample_tx, "balance": 5850.0}

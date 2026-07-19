"""
Accounting Router | روتر حسابداری
===================================
FastAPI router exposing accounting endpoints.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.api.models.accounting import Account, AccountType, InvoiceStatus, JournalEntry
from apps.api.schemas.accounting import (
    AccountCreate, AccountUpdate, AccountResponse, AccountListResponse,
    JournalEntryCreate, JournalEntryResponse, JournalEntryListResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse,
    PaymentCreate, PaymentResponse, PaymentListResponse,
    BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse,
    DashboardSummaryResponse,
)
from apps.api.services.accounting import (
    AccountService, JournalEntryService, InvoiceService,
    PaymentService, BudgetService
)

router = APIRouter(prefix="/api/accounting", tags=["accounting"])


# ── Accounts ─────────────────────────────────────────────────────
@router.get("/accounts", response_model=AccountListResponse)
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    account_type: Optional[AccountType] = None,
    session: AsyncSession = Depends(get_db_session)
) -> AccountListResponse:
    """List accounts with pagination."""
    service = AccountService(session)
    accounts, total = await service.list(skip, limit, account_type)
    return AccountListResponse(
        items=[AccountResponse.model_validate(acc) for acc in accounts],
        total=total, skip=skip, limit=limit
    )


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    session: AsyncSession = Depends(get_db_session)
) -> AccountResponse:
    """Get a single account by ID."""
    service = AccountService(session)
    try:
        account = await service.get(account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AccountResponse.model_validate(account)


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    session: AsyncSession = Depends(get_db_session)
) -> AccountResponse:
    """Create a new account."""
    service = AccountService(session)
    try:
        account = await service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.commit()
    return AccountResponse.model_validate(account)


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    payload: AccountUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> AccountResponse:
    """Update an existing account."""
    service = AccountService(session)
    try:
        account = await service.update(account_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return AccountResponse.model_validate(account)


# ── Journal Entries ─────────────────────────────────────────────
@router.get("/journal-entries", response_model=JournalEntryListResponse)
async def list_journal_entries(
    skip: int = 0,
    limit: int = 100,
    is_posted: Optional[bool] = None,
    session: AsyncSession = Depends(get_db_session)
) -> JournalEntryListResponse:
    """List journal entries with pagination."""
    service = JournalEntryService(session)
    entries, total = await service.list(skip, limit, is_posted)
    return JournalEntryListResponse(
        items=[JournalEntryResponse.model_validate(entry) for entry in entries],
        total=total, skip=skip, limit=limit
    )


@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload: JournalEntryCreate,
    session: AsyncSession = Depends(get_db_session)
) -> JournalEntryResponse:
    """Create a new journal entry (double-entry)."""
    service = JournalEntryService(session)
    try:
        entry = await service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    await session.commit()
    return JournalEntryResponse.model_validate(entry)


# ── Invoices ─────────────────────────────────────────────────────
@router.get("/invoices", response_model=InvoiceListResponse)
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[InvoiceStatus] = None,
    session: AsyncSession = Depends(get_db_session)
) -> InvoiceListResponse:
    """List invoices with pagination."""
    service = InvoiceService(session)
    invoices, total = await service.list(skip, limit, status_filter)
    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(inv) for inv in invoices],
        total=total, skip=skip, limit=limit
    )


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    session: AsyncSession = Depends(get_db_session)
) -> InvoiceResponse:
    """Create a new invoice."""
    service = InvoiceService(session)
    invoice = await service.create(payload)
    await session.commit()
    return InvoiceResponse.model_validate(invoice)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    session: AsyncSession = Depends(get_db_session)
) -> InvoiceResponse:
    """Update an existing invoice."""
    service = InvoiceService(session)
    try:
        invoice = await service.update(invoice_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    await session.commit()
    return InvoiceResponse.model_validate(invoice)


# ── Payments ─────────────────────────────────────────────────────
@router.get("/payments", response_model=PaymentListResponse)
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
) -> PaymentListResponse:
    """List payments with pagination."""
    service = PaymentService(session)
    payments, total = await service.list(skip, limit)
    return PaymentListResponse(
        items=[PaymentResponse.model_validate(pmt) for pmt in payments],
        total=total, skip=skip, limit=limit
    )


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_db_session)
) -> PaymentResponse:
    """Create a new payment."""
    service = PaymentService(session)
    payment = await service.create(payload)
    await session.commit()
    return PaymentResponse.model_validate(payment)


# ── Budgets ─────────────────────────────────────────────────────
@router.get("/budgets", response_model=BudgetListResponse)
async def list_budgets(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session)
) -> BudgetListResponse:
    """List budgets with pagination."""
    service = BudgetService(session)
    budgets, total = await service.list(skip, limit)
    return BudgetListResponse(
        items=[BudgetResponse.model_validate(budg) for budg in budgets],
        total=total, skip=skip, limit=limit
    )


@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    session: AsyncSession = Depends(get_db_session)
) -> BudgetResponse:
    """Create a new budget."""
    service = BudgetService(session)
    budget = await service.create(payload)
    await session.commit()
    return BudgetResponse.model_validate(budget)


# ── Dashboard Summary ────────────────────────────────────────────
@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    session: AsyncSession = Depends(get_db_session)
) -> DashboardSummaryResponse:
    """Get accounting dashboard summary with real data."""
    from sqlalchemy import select, func
    from apps.api.models.accounting import JournalItem, EntryType
    
    # Calculate income (sum of all credits to income accounts)
    income_result = await session.execute(
        select(func.coalesce(func.sum(JournalItem.amount), 0))
        .join(Account)
        .where(Account.account_type == AccountType.INCOME)
    )
    total_income = Decimal(str(income_result.scalar_one()))
    
    # Calculate expense (sum of all debits from expense accounts)
    expense_result = await session.execute(
        select(func.coalesce(func.sum(JournalItem.amount), 0))
        .join(Account)
        .where(Account.account_type == AccountType.EXPENSE)
    )
    total_expense = Decimal(str(expense_result.scalar_one()))
    
    # Get transaction count
    tx_count_result = await session.execute(
        select(func.count()).select_from(JournalEntry)
    )
    transactions_count = tx_count_result.scalar_one()
    
    return DashboardSummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        net_profit=total_income - total_expense,
        eco_rewards_distributed=Decimal("0.00"),
        carbon_credits_value=Decimal("0.00"),
        transactions_count=transactions_count,
        current_balance=total_income - total_expense
    )
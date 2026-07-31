"""Accounting router."""

from __future__ import annotations

import logging
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.accounting import Account, AccountType, InvoiceStatus, JournalEntry
from apps.api.schemas.accounting import (
    AccountCreate,
    AccountListResponse,
    AccountResponse,
    AccountUpdate,
    BudgetCreate,
    BudgetListResponse,
    BudgetResponse,
    DashboardSummaryResponse,
    InvoiceCreate,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceUpdate,
    JournalEntryCreate,
    JournalEntryListResponse,
    JournalEntryResponse,
    PaymentCreate,
    PaymentListResponse,
    PaymentResponse,
)
from apps.api.services.accounting import (
    AccountService,
    BudgetService,
    InvoiceService,
    JournalEntryService,
    PaymentService,
)
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/accounting", tags=["accounting"])


@router.get("/accounts", response_model=AccountListResponse)
async def list_accounts(
    skip: int = 0,
    limit: int = 100,
    account_type: AccountType | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> AccountListResponse:
    service = AccountService(session)
    accounts, total = await service.list(skip, limit, account_type)
    return AccountListResponse(
        items=[AccountResponse.model_validate(acc) for acc in accounts],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/accounts/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: str,
    session: AsyncSession = Depends(get_db_session),
) -> AccountResponse:
    service = AccountService(session)
    try:
        account = await service.get(account_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AccountResponse.model_validate(account)


@router.post("/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> AccountResponse:
    service = AccountService(session)
    try:
        account = await service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return AccountResponse.model_validate(account)


@router.patch("/accounts/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: str,
    payload: AccountUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> AccountResponse:
    service = AccountService(session)
    try:
        account = await service.update(account_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return AccountResponse.model_validate(account)


@router.get("/journal-entries", response_model=JournalEntryListResponse)
async def list_journal_entries(
    skip: int = 0,
    limit: int = 100,
    is_posted: bool | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> JournalEntryListResponse:
    service = JournalEntryService(session)
    entries, total = await service.list(skip, limit, is_posted)
    return JournalEntryListResponse(
        items=[JournalEntryResponse.model_validate(entry) for entry in entries],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_journal_entry(
    payload: JournalEntryCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> JournalEntryResponse:
    service = JournalEntryService(session)
    try:
        entry = await service.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return JournalEntryResponse.model_validate(entry)


@router.get("/invoices", response_model=InvoiceListResponse)
async def list_invoices(
    skip: int = 0,
    limit: int = 100,
    status_filter: InvoiceStatus | None = None,
    session: AsyncSession = Depends(get_db_session),
) -> InvoiceListResponse:
    service = InvoiceService(session)
    invoices, total = await service.list(skip, limit, status_filter)
    return InvoiceListResponse(
        items=[InvoiceResponse.model_validate(inv) for inv in invoices],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: InvoiceCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> InvoiceResponse:
    service = InvoiceService(session)
    invoice = await service.create(payload)
    return InvoiceResponse.model_validate(invoice)


@router.patch("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    payload: InvoiceUpdate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> InvoiceResponse:
    service = InvoiceService(session)
    try:
        invoice = await service.update(invoice_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return InvoiceResponse.model_validate(invoice)


@router.get("/payments", response_model=PaymentListResponse)
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
) -> PaymentListResponse:
    service = PaymentService(session)
    payments, total = await service.list(skip, limit)
    return PaymentListResponse(
        items=[PaymentResponse.model_validate(pmt) for pmt in payments],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payload: PaymentCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> PaymentResponse:
    service = PaymentService(session)
    payment = await service.create(payload)
    return PaymentResponse.model_validate(payment)


@router.get("/budgets", response_model=BudgetListResponse)
async def list_budgets(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_db_session),
) -> BudgetListResponse:
    service = BudgetService(session)
    budgets, total = await service.list(skip, limit)
    return BudgetListResponse(
        items=[BudgetResponse.model_validate(budg) for budg in budgets],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/budgets", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("accounting:write")),
) -> BudgetResponse:
    service = BudgetService(session)
    budget = await service.create(payload)
    return BudgetResponse.model_validate(budget)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    session: AsyncSession = Depends(get_db_session),
) -> DashboardSummaryResponse:
    try:
        from apps.api.models.accounting import JournalItem

        income_result = await session.execute(
            select(func.coalesce(func.sum(JournalItem.amount), 0))
            .select_from(JournalItem)
            .join(Account)
            .where(Account.account_type == AccountType.INCOME)
        )
        total_income = Decimal(str(income_result.scalar_one()))

        expense_result = await session.execute(
            select(func.coalesce(func.sum(JournalItem.amount), 0))
            .select_from(JournalItem)
            .join(Account)
            .where(Account.account_type == AccountType.EXPENSE)
        )
        total_expense = Decimal(str(expense_result.scalar_one()))

        tx_count_result = await session.execute(select(func.count()).select_from(JournalEntry))
        transactions_count = int(tx_count_result.scalar_one())
    except Exception as e:
        logger.warning("summary fallback zeros: %s", e)
        total_income = Decimal("0")
        total_expense = Decimal("0")
        transactions_count = 0

    return DashboardSummaryResponse(
        total_income=total_income,
        total_expense=total_expense,
        net_profit=total_income - total_expense,
        eco_rewards_distributed=Decimal("0.00"),
        carbon_credits_value=Decimal("0.00"),
        transactions_count=transactions_count,
        current_balance=total_income - total_expense,
    )

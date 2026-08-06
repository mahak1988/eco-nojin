"""
API Schemas Package
===================
Pydantic models for request/response validation.
"""

import logging

logger = logging.getLogger(__name__)
from apps.api.schemas.accounting import (
    AccountType, EntryType, InvoiceStatus, PaymentMethod, TaxType,
    AccountBase, AccountCreate, AccountUpdate, AccountResponse, AccountListResponse,
    JournalItemBase, JournalItemCreate, JournalItemResponse,
    JournalEntryBase, JournalEntryCreate, JournalEntryUpdate, JournalEntryResponse, JournalEntryListResponse,
    InvoiceItemBase, InvoiceItemCreate, InvoiceItemResponse,
    InvoiceBase, InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse,
    PaymentBase, PaymentCreate, PaymentResponse, PaymentListResponse,
    BudgetBase, BudgetCreate, BudgetUpdate, BudgetResponse, BudgetListResponse,
    TaxRateBase, TaxRateCreate, TaxRateUpdate, TaxRateResponse,
    FixedAssetBase, FixedAssetCreate, FixedAssetUpdate, FixedAssetResponse,
    BalanceSheetResponse, IncomeStatementResponse, DashboardSummaryResponse,
)
from apps.api.schemas.agriculture_school import (
    SchoolTypeEnum,
    AgricultureSchoolBase, AgricultureSchoolCreate, AgricultureSchoolUpdate,
    AgricultureSchoolResponse, AgricultureSchoolListResponse, SchoolStats,
)
# Re-export generic Api schemas from schemas.py for backward compatibility
from apps.api.schemas_file import (
    ApiBase, ApiCreate, ApiUpdate, ApiResponse, ApiListResponse,
)

__all__ = [
    # Accounting
    "AccountType", "EntryType", "InvoiceStatus", "PaymentMethod", "TaxType",
    "AccountBase", "AccountCreate", "AccountUpdate", "AccountResponse", "AccountListResponse",
    "JournalItemBase", "JournalItemCreate", "JournalItemResponse",
    "JournalEntryBase", "JournalEntryCreate", "JournalEntryUpdate", "JournalEntryResponse", "JournalEntryListResponse",
    "InvoiceItemBase", "InvoiceItemCreate", "InvoiceItemResponse",
    "InvoiceBase", "InvoiceCreate", "InvoiceUpdate", "InvoiceResponse", "InvoiceListResponse",
    "PaymentBase", "PaymentCreate", "PaymentResponse", "PaymentListResponse",
    "BudgetBase", "BudgetCreate", "BudgetUpdate", "BudgetResponse", "BudgetListResponse",
    "TaxRateBase", "TaxRateCreate", "TaxRateUpdate", "TaxRateResponse",
    "FixedAssetBase", "FixedAssetCreate", "FixedAssetUpdate", "FixedAssetResponse",
    "BalanceSheetResponse", "IncomeStatementResponse", "DashboardSummaryResponse",
    # Agriculture Schools
    "SchoolTypeEnum",
    "AgricultureSchoolBase", "AgricultureSchoolCreate", "AgricultureSchoolUpdate",
    "AgricultureSchoolResponse", "AgricultureSchoolListResponse", "SchoolStats",
    # Generic Api CRUD schemas
    "ApiBase", "ApiCreate", "ApiUpdate", "ApiResponse", "ApiListResponse",
]

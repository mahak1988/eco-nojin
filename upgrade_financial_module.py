#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏦 ارتقاء جامع ماژول مالی اکو نوژین
شامل: حقوق و دستمزد، قراردادها، کیف پول، درگاه پرداخت، مدل‌های پیشرفته
"""
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB_DIR = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


def main():
    print("🏦 ارتقاء جامع ماژول مالی اکو نوژین")
    print("=" * 70)

    # =========================================================================
    # 1. مدل‌های دیتابیس گسترده
    # =========================================================================
    print("\n📝 ایجاد مدل‌های دیتابیس گسترده...")

    models_content = '''# api/modules/financial/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


# =========================================================================
# Enums
# =========================================================================
class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"
    SALARY = "salary"
    TAX = "tax"
    INSURANCE = "insurance"


class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    PARTIAL = "partial"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InventoryMethod(enum.Enum):
    FIFO = "fifo"
    LIFO = "lifo"
    AVERAGE = "average"
    SPECIFIC = "specific"


class ContractStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class ContractType(enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"
    SERVICE = "service"
    EMPLOYMENT = "employment"
    LEASE = "lease"
    PARTNERSHIP = "partnership"


class PaymentMethod(enum.Enum):
    CASH = "cash"
    CARD = "card"
    BANK_TRANSFER = "bank_transfer"
    WALLET = "wallet"
    CHECK = "check"
    CRYPTO = "crypto"


class WalletTransactionType(enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"
    REFUND = "refund"
    FEE = "fee"


class DepreciationMethod(enum.Enum):
    STRAIGHT_LINE = "straight_line"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"
    SUM_OF_YEARS = "sum_of_years"


class EmployeeStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"


# =========================================================================
# Unit of Measurement
# =========================================================================
class Unit(Base):
    """واحدهای اندازه‌گیری"""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    category = Column(String(50))  # weight, volume, length, count, area
    conversion_factor = Column(Float, default=1.0)
    base_unit_id = Column(Integer, ForeignKey("units.id"))

    is_active = Column(Boolean, default=True)


# =========================================================================
# Employee & Payroll
# =========================================================================
class Employee(Base):
    """کارکنان"""
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    national_id = Column(String(20))

    # اطلاعات شغلی
    position = Column(String(200))
    department = Column(String(200))
    employment_date = Column(Date)
    status = Column(SQLEnum(EmployeeStatus), default=EmployeeStatus.ACTIVE)

    # حقوق پایه
    base_salary = Column(Float, default=0.0)
    housing_allowance = Column(Float, default=0.0)
    food_allowance = Column(Float, default=0.0)
    child_allowance = Column(Float, default=0.0)
    other_allowances = Column(Float, default=0.0)

    # اطلاعات بانکی
    bank_name = Column(String(100))
    bank_account = Column(String(50))
    sheba_number = Column(String(50))

    # اطلاعات بیمه
    insurance_number = Column(String(50))
    insurance_rate = Column(Float, default=7.0)  # 7% سهم کارگر

    # مالیات
    tax_exempt_amount = Column(Float, default=0.0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    payroll_records = relationship("PayrollRecord", back_populates="employee")


class PayrollRecord(Base):
    """سوابق حقوق و دستمزد"""
    __tablename__ = "payroll_records"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    # دوره
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)

    # حقوق و مزایا
    base_salary = Column(Float, default=0.0)
    overtime_hours = Column(Float, default=0.0)
    overtime_pay = Column(Float, default=0.0)
    bonuses = Column(Float, default=0.0)
    allowances_total = Column(Float, default=0.0)
    gross_salary = Column(Float, default=0.0)

    # کسورات
    insurance_employee = Column(Float, default=0.0)  # 7%
    insurance_employer = Column(Float, default=0.0)  # 23%
    tax_amount = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)

    # خالص
    net_salary = Column(Float, default=0.0)

    # وضعیت
    status = Column(String(50), default="calculated")  # calculated, approved, paid
    payment_date = Column(DateTime)
    payment_method = Column(SQLEnum(PaymentMethod))

    created_at = Column(DateTime, server_default=func.now())

    employee = relationship("Employee", back_populates="payroll_records")


# =========================================================================
# Contracts
# =========================================================================
class Contract(Base):
    """قراردادها"""
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    contract_number = Column(String(50), unique=True, nullable=False)

    contract_type = Column(SQLEnum(ContractType), nullable=False)
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.DRAFT)

    title = Column(String(300), nullable=False)
    description = Column(Text)

    # طرفین
    party_a_name = Column(String(200))  # طرف اول
    party_b_name = Column(String(200))  # طرف دوم
    party_a_id = Column(Integer, ForeignKey("users.id"))
    party_b_id = Column(Integer, ForeignKey("users.id"))

    # مبالغ
    contract_amount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)

    # تاریخ‌ها
    start_date = Column(Date)
    end_date = Column(Date)
    sign_date = Column(Date)

    # شرایط پرداخت
    payment_terms = Column(JSON)  # {"type": "installment", "count": 12, "interval": "monthly"}

    # شرایط خاص
    terms_and_conditions = Column(Text)
    penalties = Column(JSON)
    guarantees = Column(JSON)

    # فایل‌ها
    contract_file_url = Column(String(500))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    items = relationship("ContractItem", back_populates="contract", cascade="all, delete-orphan")


class ContractItem(Base):
    """آیتم‌های قرارداد"""
    __tablename__ = "contract_items"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)

    description = Column(String(500), nullable=False)
    quantity = Column(Float, default=1.0)
    unit_id = Column(Integer, ForeignKey("units.id"))
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)

    delivery_date = Column(Date)
    delivery_status = Column(String(50), default="pending")

    contract = relationship("Contract", back_populates="items")


# =========================================================================
# Wallet
# =========================================================================
class Wallet(Base):
    """کیف پول"""
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    balance = Column(Float, default=0.0)
    currency = Column(String(10), default="IRR")
    is_frozen = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    transactions = relationship("WalletTransaction", back_populates="wallet")


class WalletTransaction(Base):
    """تراکنش‌های کیف پول"""
    __tablename__ = "wallet_transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=False)

    transaction_type = Column(SQLEnum(WalletTransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    balance_before = Column(Float)
    balance_after = Column(Float)

    description = Column(String(500))
    reference_number = Column(String(100))

    # ارجاعات
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    order_id = Column(Integer)

    status = Column(String(50), default="completed")  # pending, completed, failed, refunded

    created_at = Column(DateTime, server_default=func.now())

    wallet = relationship("Wallet", back_populates="transactions")


# =========================================================================
# Payment Gateway
# =========================================================================
class PaymentGateway(Base):
    """درگاه‌های پرداخت"""
    __tablename__ = "payment_gateways"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), unique=True, nullable=False)

    # تنظیمات
    merchant_id = Column(String(100))
    api_key = Column(String(200))
    callback_url = Column(String(500))

    # وضعیت
    is_active = Column(Boolean, default=True)
    is_test_mode = Column(Boolean, default=True)

    # کارمزد
    fee_rate = Column(Float, default=1.0)  # 1%
    fixed_fee = Column(Float, default=0.0)

    created_at = Column(DateTime, server_default=func.now())


class Payment(Base):
    """پرداخت‌ها"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False)

    gateway_id = Column(Integer, ForeignKey("payment_gateways.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    amount = Column(Float, nullable=False)
    fee_amount = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)

    status = Column(String(50), default="pending")  # pending, success, failed, refunded
    reference_code = Column(String(100))
    tracking_code = Column(String(100))

    # ارجاعات
    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    order_id = Column(Integer)

    description = Column(String(500))

    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)


# =========================================================================
# Financial Accounts & Transactions (حسابداری)
# =========================================================================
class Account(Base):
    """حساب‌های دفتری"""
    __tablename__ = "financial_accounts"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    account_type = Column(String(50))  # asset, liability, equity, revenue, expense
    parent_id = Column(Integer, ForeignKey("financial_accounts.id"))
    balance = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())

    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    """تراکنش‌های مالی"""
    __tablename__ = "financial_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("financial_accounts.id"), nullable=False)

    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text)
    reference_number = Column(String(100))

    transaction_date = Column(DateTime, server_default=func.now())

    invoice_id = Column(Integer, ForeignKey("invoices.id"))
    product_id = Column(Integer, ForeignKey("inventory_products.id"))

    created_at = Column(DateTime, server_default=func.now())

    account = relationship("Account", back_populates="transactions")
    invoice = relationship("Invoice", back_populates="transactions")


class Invoice(Base):
    """فاکتورها"""
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    invoice_number = Column(String(50), unique=True, nullable=False)

    invoice_type = Column(String(20))  # sales, purchase, proforma
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)

    customer_id = Column(Integer, ForeignKey("users.id"))
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    customer_address = Column(Text)
    customer_national_id = Column(String(20))

    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)
    tax_amount = Column(Float, default=0.0)
    discount_rate = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)

    issue_date = Column(DateTime, server_default=func.now())
    due_date = Column(DateTime)
    paid_date = Column(DateTime)

    payment_method = Column(SQLEnum(PaymentMethod))
    notes = Column(Text)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="invoice")


class InvoiceItem(Base):
    """آیتم‌های فاکتور"""
    __tablename__ = "invoice_items"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("inventory_products.id"))

    product_name = Column(String(200), nullable=False)
    description = Column(Text)
    quantity = Column(Float, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.id"))
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)

    total_price = Column(Float, nullable=False)

    invoice = relationship("Invoice", back_populates="items")
    product = relationship("InventoryProduct")


# =========================================================================
# Inventory (انبارداری)
# =========================================================================
class InventoryProduct(Base):
    """محصولات انبار"""
    __tablename__ = "inventory_products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    description = Column(Text)

    category = Column(String(100))
    unit_id = Column(Integer, ForeignKey("units.id"))

    quantity = Column(Float, default=0.0)
    min_quantity = Column(Float, default=0.0)
    max_quantity = Column(Float, default=0.0)
    reorder_point = Column(Float, default=0.0)

    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    wholesale_price = Column(Float, default=0.0)

    valuation_method = Column(SQLEnum(InventoryMethod), default=InventoryMethod.AVERAGE)

    location = Column(String(100))
    shelf = Column(String(50))
    warehouse = Column(String(100))

    # تاریخ انقضا
    expiry_date = Column(Date)
    production_date = Column(Date)
    batch_number = Column(String(50))

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    movements = relationship("InventoryMovement", back_populates="product")


class InventoryMovement(Base):
    """حرکات انبار"""
    __tablename__ = "inventory_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_products.id"), nullable=False)

    movement_type = Column(String(20))  # in, out, transfer, adjustment, return
    quantity = Column(Float, nullable=False)

    quantity_before = Column(Float)
    quantity_after = Column(Float)

    reference_type = Column(String(50))
    reference_id = Column(Integer)

    description = Column(Text)
    notes = Column(Text)

    movement_date = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    product = relationship("InventoryProduct", back_populates="movements")


# =========================================================================
# Budget (بودجه)
# =========================================================================
class Budget(Base):
    """بودجه"""
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer)

    budgeted_amount = Column(Float, nullable=False)
    actual_amount = Column(Float, default=0.0)
    variance = Column(Float, default=0.0)

    category = Column(String(100))
    account_id = Column(Integer, ForeignKey("financial_accounts.id"))

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


# =========================================================================
# Fixed Assets & Depreciation (دارایی ثابت و استهلاک)
# =========================================================================
class FixedAsset(Base):
    """دارایی‌های ثابت"""
    __tablename__ = "fixed_assets"

    id = Column(Integer, primary_key=True, index=True)
    asset_code = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100))

    purchase_date = Column(Date)
    purchase_cost = Column(Float, nullable=False)
    salvage_value = Column(Float, default=0.0)
    useful_life_years = Column(Integer, nullable=False)

    depreciation_method = Column(SQLEnum(DepreciationMethod), default=DepreciationMethod.STRAIGHT_LINE)

    accumulated_depreciation = Column(Float, default=0.0)
    book_value = Column(Float, default=0.0)

    location = Column(String(200))
    status = Column(String(50), default="active")

    created_at = Column(DateTime, server_default=func.now())


# =========================================================================
# Financial Metrics
# =========================================================================
class FinancialMetric(Base):
    """شاخص‌های مالی"""
    __tablename__ = "financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    code = Column(String(50), unique=True, nullable=False)

    category = Column(String(100))
    formula = Column(Text)
    description = Column(Text)

    current_value = Column(Float)
    previous_value = Column(Float)
    target_value = Column(Float)

    calculation_date = Column(DateTime, server_default=func.now())

    created_at = Column(DateTime, server_default=func.now())
'''

    write_file(API_DIR / "modules" / "financial" / "models.py", models_content)

    # =========================================================================
    # 2. موتور محاسبات پیشرفته
    # =========================================================================
    print("\n🧮 ایجاد موتور محاسبات پیشرفته...")

    calculator_content = '''# api/modules/financial/calculator.py
"""
موتور محاسبات مالی پیشرفته
شامل تمام فرمول‌های استاندارد حسابداری، مالی، بانکی و اقتصادی
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta, date
import math


class FinancialCalculator:
    """ماشین حساب مالی پیشرفته"""

    # =========================================================================
    # شاخص‌های سودآوری (Profitability Ratios)
    # =========================================================================

    @staticmethod
    def gross_margin(revenue: float, cogs: float) -> float:
        """حاشیه سود ناخالص"""
        if revenue == 0: return 0
        return ((revenue - cogs) / revenue) * 100

    @staticmethod
    def net_margin(net_income: float, revenue: float) -> float:
        """حاشیه سود خالص"""
        if revenue == 0: return 0
        return (net_income / revenue) * 100

    @staticmethod
    def operating_margin(operating_income: float, revenue: float) -> float:
        """حاشیه سود عملیاتی"""
        if revenue == 0: return 0
        return (operating_income / revenue) * 100

    @staticmethod
    def roa(net_income: float, total_assets: float) -> float:
        """بازگشت دارایی‌ها (ROA)"""
        if total_assets == 0: return 0
        return (net_income / total_assets) * 100

    @staticmethod
    def roe(net_income: float, equity: float) -> float:
        """بازگشت حقوق صاحبان سهام (ROE)"""
        if equity == 0: return 0
        return (net_income / equity) * 100

    @staticmethod
    def roic(nopat: float, invested_capital: float) -> float:
        """بازگشت سرمایه سرمایه‌گذاری‌شده (ROIC)"""
        if invested_capital == 0: return 0
        return (nopat / invested_capital) * 100

    @staticmethod
    def dupont_analysis(net_income: float, revenue: float, total_assets: float, equity: float) -> Dict:
        """تحلیل دوپونت"""
        net_margin = (net_income / revenue * 100) if revenue else 0
        asset_turnover = (revenue / total_assets) if total_assets else 0
        equity_multiplier = (total_assets / equity) if equity else 0
        roe = net_margin * asset_turnover * equity_multiplier / 100

        return {
            "net_margin": round(net_margin, 2),
            "asset_turnover": round(asset_turnover, 2),
            "equity_multiplier": round(equity_multiplier, 2),
            "roe": round(roe, 2),
        }

    # =========================================================================
    # شاخص‌های نقدینگی (Liquidity Ratios)
    # =========================================================================

    @staticmethod
    def current_ratio(current_assets: float, current_liabilities: float) -> float:
        """نسبت جاری"""
        if current_liabilities == 0: return 0
        return current_assets / current_liabilities

    @staticmethod
    def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
        """نسبت آنی"""
        if current_liabilities == 0: return 0
        return (current_assets - inventory) / current_liabilities

    @staticmethod
    def cash_ratio(cash: float, current_liabilities: float) -> float:
        """نسبت وجه نقد"""
        if current_liabilities == 0: return 0
        return cash / current_liabilities

    @staticmethod
    def working_capital(current_assets: float, current_liabilities: float) -> float:
        """سرمایه در گردش"""
        return current_assets - current_liabilities

    # =========================================================================
    # شاخص‌های اهرمی (Leverage Ratios)
    # =========================================================================

    @staticmethod
    def debt_to_equity(total_debt: float, equity: float) -> float:
        """نسبت بدهی به حقوق"""
        if equity == 0: return 0
        return total_debt / equity

    @staticmethod
    def debt_to_assets(total_debt: float, total_assets: float) -> float:
        """نسبت بدهی به دارایی"""
        if total_assets == 0: return 0
        return total_debt / total_assets

    @staticmethod
    def interest_coverage(ebit: float, interest_expense: float) -> float:
        """نسبت پوشش بهره"""
        if interest_expense == 0: return 0
        return ebit / interest_expense

    @staticmethod
    def equity_multiplier(total_assets: float, equity: float) -> float:
        """ضریب فزاینده حقوق"""
        if equity == 0: return 0
        return total_assets / equity

    # =========================================================================
    # شاخص‌های کارایی (Efficiency Ratios)
    # =========================================================================

    @staticmethod
    def inventory_turnover(cogs: float, avg_inventory: float) -> float:
        """گردش موجودی"""
        if avg_inventory == 0: return 0
        return cogs / avg_inventory

    @staticmethod
    def days_sales_outstanding(ar: float, revenue: float, days: int = 365) -> float:
        """دوره وصول مطالبات"""
        if revenue == 0: return 0
        return (ar / revenue) * days

    @staticmethod
    def days_payable_outstanding(ap: float, cogs: float, days: int = 365) -> float:
        """دوره پرداخت بدهی‌ها"""
        if cogs == 0: return 0
        return (ap / cogs) * days

    @staticmethod
    def days_inventory_outstanding(cogs: float, avg_inventory: float, days: int = 365) -> float:
        """دوره گردش موجودی"""
        if cogs == 0: return 0
        return (avg_inventory / cogs) * days

    @staticmethod
    def cash_conversion_cycle(dso: float, dio: float, dpo: float) -> float:
        """چرخه تبدیل وجه نقد"""
        return dso + dio - dpo

    @staticmethod
    def asset_turnover(revenue: float, total_assets: float) -> float:
        """گردش دارایی‌ها"""
        if total_assets == 0: return 0
        return revenue / total_assets

    # =========================================================================
    # شاخص‌های سرمایه‌گذاری (Investment Ratios)
    # =========================================================================

    @staticmethod
    def npv(cash_flows: List[float], discount_rate: float) -> float:
        """ارزش فعلی خالص (NPV)"""
        return sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows))

    @staticmethod
    def irr(cash_flows: List[float], max_iterations: int = 100) -> Optional[float]:
        """نرخ بازگشت داخلی (IRR)"""
        guess = 0.1
        for _ in range(max_iterations):
            npv = sum(cf / ((1 + guess) ** t) for t, cf in enumerate(cash_flows))
            derivative = sum(-t * cf / ((1 + guess) ** (t + 1)) for t, cf in enumerate(cash_flows))
            if abs(derivative) < 1e-10: break
            new_guess = guess - npv / derivative
            if abs(new_guess - guess) < 1e-6: return new_guess
            guess = new_guess
        return None

    @staticmethod
    def payback_period(cash_flows: List[float]) -> Optional[float]:
        """دوره بازگشت سرمایه"""
        cumulative = 0
        for t, cf in enumerate(cash_flows):
            cumulative += cf
            if cumulative >= 0:
                return t + (cumulative - cf) / abs(cf) if cf != 0 else t
        return None

    @staticmethod
    def discounted_payback(cash_flows: List[float], discount_rate: float) -> Optional[float]:
        """دوره بازگشت تنزیل‌شده"""
        discounted = [cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows)]
        return FinancialCalculator.payback_period(discounted)

    @staticmethod
    def roi(net_profit: float, investment: float) -> float:
        """نرخ بازگشت سرمایه"""
        if investment == 0: return 0
        return (net_profit / investment) * 100

    @staticmethod
    def profitability_index(npv: float, initial_investment: float) -> float:
        """شاخص سودآوری"""
        if initial_investment == 0: return 0
        return (npv + initial_investment) / initial_investment

    # =========================================================================
    # مدل‌های بانکی و وام (Banking & Loans)
    # =========================================================================

    @staticmethod
    def loan_payment(principal: float, annual_rate: float, years: int, payments_per_year: int = 12) -> float:
        """قسط وام (فرمول استاندارد)"""
        r = annual_rate / 100 / payments_per_year
        n = years * payments_per_year
        if r == 0: return principal / n
        return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

    @staticmethod
    def loan_amortization_schedule(principal: float, annual_rate: float, years: int) -> List[Dict]:
        """جدول استهلاک وام"""
        schedule = []
        monthly_rate = annual_rate / 100 / 12
        months = years * 12
        payment = FinancialCalculator.loan_payment(principal, annual_rate, years)

        balance = principal
        for month in range(1, months + 1):
            interest = balance * monthly_rate
            principal_paid = payment - interest
            balance -= principal_paid

            schedule.append({
                "month": month,
                "payment": round(payment, 2),
                "principal": round(principal_paid, 2),
                "interest": round(interest, 2),
                "balance": round(max(0, balance), 2),
            })

        return schedule

    @staticmethod
    def effective_annual_rate(nominal_rate: float, compounding_periods: int) -> float:
        """نرخ مؤثر سالانه"""
        return ((1 + nominal_rate / 100 / compounding_periods) ** compounding_periods - 1) * 100

    # =========================================================================
    # استهلاک دارایی ثابت (Depreciation)
    # =========================================================================

    @staticmethod
    def straight_line_depreciation(cost: float, salvage: float, years: int) -> float:
        """استهلاک خط مستقیم"""
        if years == 0: return 0
        return (cost - salvage) / years

    @staticmethod
    def declining_balance_depreciation(cost: float, salvage: float, years: int, rate: float = 2.0) -> List[Dict]:
        """استهلاک نزولی"""
        schedule = []
        book_value = cost
        annual_rate = rate / years

        for year in range(1, years + 1):
            depreciation = book_value * annual_rate
            if book_value - depreciation < salvage:
                depreciation = book_value - salvage
            book_value -= depreciation
            schedule.append({
                "year": year,
                "depreciation": round(depreciation, 2),
                "book_value": round(book_value, 2),
            })

        return schedule

    @staticmethod
    def sum_of_years_depreciation(cost: float, salvage: float, years: int) -> List[Dict]:
        """استهلاک مجموع سنوات"""
        schedule = []
        sum_of_years = years * (years + 1) / 2
        depreciable = cost - salvage

        for year in range(1, years + 1):
            fraction = (years - year + 1) / sum_of_years
            depreciation = depreciable * fraction
            schedule.append({
                "year": year,
                "depreciation": round(depreciation, 2),
                "fraction": round(fraction, 4),
            })

        return schedule

    # =========================================================================
    # حقوق و دستمزد (Payroll)
    # =========================================================================

    @staticmethod
    def calculate_iranian_tax(annual_income: float, year: int = 1403) -> float:
        """محاسبه مالیات بر حقوق ایران (پلکانی)"""
        # نرخ‌های 1403 (تومان)
        brackets = [
            (120_000_000, 0.0),       # معاف
            (168_000_000, 0.10),      # 10%
            (276_000_000, 0.15),      # 15%
            (408_000_000, 0.20),      # 20%
            (float("inf"), 0.30),     # 30%
        ]

        tax = 0
        prev_limit = 0

        for limit, rate in brackets:
            if annual_income <= limit:
                tax += (annual_income - prev_limit) * rate
                break
            else:
                tax += (limit - prev_limit) * rate
                prev_limit = limit

        return tax

    @staticmethod
    def calculate_payroll(
        base_salary: float,
        housing_allowance: float = 0,
        food_allowance: float = 0,
        child_allowance: float = 0,
        overtime_hours: float = 0,
        hourly_rate: float = 0,
        bonuses: float = 0,
        insurance_rate_employee: float = 7.0,
        insurance_rate_employer: float = 23.0,
        year: int = 1403
    ) -> Dict:
        """محاسبه کامل حقوق و دستمزد"""
        # مزایا
        allowances = housing_allowance + food_allowance + child_allowance
        overtime_pay = overtime_hours * hourly_rate
        gross_salary = base_salary + allowances + overtime_pay + bonuses

        # بیمه
        insurance_employee = gross_salary * (insurance_rate_employee / 100)
        insurance_employer = gross_salary * (insurance_rate_employer / 100)

        # مالیات (سالانه / 12)
        annual_income = gross_salary * 12
        annual_tax = FinancialCalculator.calculate_iranian_tax(annual_income, year)
        monthly_tax = annual_tax / 12

        # کسورات
        total_deductions = insurance_employee + monthly_tax
        net_salary = gross_salary - total_deductions

        return {
            "base_salary": round(base_salary, 2),
            "allowances": {
                "housing": round(housing_allowance, 2),
                "food": round(food_allowance, 2),
                "child": round(child_allowance, 2),
                "total": round(allowances, 2),
            },
            "overtime_pay": round(overtime_pay, 2),
            "bonuses": round(bonuses, 2),
            "gross_salary": round(gross_salary, 2),
            "deductions": {
                "insurance_employee": round(insurance_employee, 2),
                "insurance_employer": round(insurance_employer, 2),
                "tax": round(monthly_tax, 2),
                "total": round(total_deductions, 2),
            },
            "net_salary": round(net_salary, 2),
        }

    # =========================================================================
    # انبارداری (Inventory)
    # =========================================================================

    @staticmethod
    def eoq(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
        """مقدار اقتصادی سفارش (EOQ)"""
        if holding_cost == 0: return 0
        return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)

    @staticmethod
    def reorder_point(daily_demand: float, lead_time: float, safety_stock: float = 0) -> float:
        """نقطه سفارش"""
        return (daily_demand * lead_time) + safety_stock

    @staticmethod
    def safety_stock(daily_demand: float, lead_time: float, service_level: float = 0.95) -> float:
        """ذخیره احتیاطی"""
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z = z_scores.get(service_level, 1.65)
        return z * daily_demand * math.sqrt(lead_time)

    @staticmethod
    def inventory_recommendations(
        current_stock: float,
        min_stock: float,
        max_stock: float,
        reorder_point: float,
        daily_demand: float,
        lead_time: float
    ) -> List[Dict]:
        """توصیه‌های هوشمند انبارداری"""
        recommendations = []

        days_of_stock = current_stock / daily_demand if daily_demand > 0 else 0

        if current_stock <= min_stock:
            recommendations.append({
                "level": "critical",
                "title": "موجودی بحرانی",
                "message": f"موجودی به حداقل رسیده. سفارش فوری {reorder_point} واحد توصیه می‌شود.",
                "action": "order_now",
                "quantity": reorder_point,
            })
        elif current_stock <= reorder_point:
            recommendations.append({
                "level": "warning",
                "title": "نقطه سفارش",
                "message": f"موجودی به نقطه سفارش رسیده. زمان سفارش‌گذاری است.",
                "action": "order_soon",
                "quantity": reorder_point,
            })
        elif days_of_stock > 90:
            recommendations.append({
                "level": "info",
                "title": "موجودی بیش از حد",
                "message": f"موجودی برای {days_of_stock:.0f} روز کافی است. کاهش سفارش توصیه می‌شود.",
                "action": "reduce_order",
            })

        if current_stock >= max_stock:
            recommendations.append({
                "level": "warning",
                "title": "تکمیل ظرفیت",
                "message": "انبار در حداکثر ظرفیت. از سفارش جدید خودداری کنید.",
                "action": "stop_order",
            })

        return recommendations

    @staticmethod
    def abc_analysis(products: List[Dict]) -> Dict:
        """تحلیل ABC موجودی"""
        sorted_products = sorted(products, key=lambda x: x.get("annual_value", 0), reverse=True)
        total_value = sum(p.get("annual_value", 0) for p in sorted_products)

        a_items, b_items, c_items = [], [], []
        cumulative = 0

        for product in sorted_products:
            cumulative += product.get("annual_value", 0)
            percentage = (cumulative / total_value * 100) if total_value > 0 else 0

            if percentage <= 80:
                a_items.append(product)
            elif percentage <= 95:
                b_items.append(product)
            else:
                c_items.append(product)

        return {
            "a_items": {"count": len(a_items), "value_percent": 80, "items": a_items},
            "b_items": {"count": len(b_items), "value_percent": 15, "items": b_items},
            "c_items": {"count": len(c_items), "value_percent": 5, "items": c_items},
        }

    # =========================================================================
    # تحلیل هزینه-فایده (CBA)
    # =========================================================================

    @staticmethod
    def cost_benefit_analysis(
        initial_investment: float,
        annual_benefits: List[float],
        annual_costs: List[float],
        discount_rate: float,
        years: int
    ) -> Dict:
        """تحلیل هزینه-فایده"""
        benefits_pv = sum(b / ((1 + discount_rate) ** t) for t, b in enumerate(annual_benefits))
        costs_pv = initial_investment + sum(c / ((1 + discount_rate) ** t) for t, c in enumerate(annual_costs))

        npv = benefits_pv - costs_pv
        bcr = benefits_pv / costs_pv if costs_pv > 0 else 0

        return {
            "npv": round(npv, 2),
            "bcr": round(bcr, 2),
            "benefits_pv": round(benefits_pv, 2),
            "costs_pv": round(costs_pv, 2),
            "recommendation": "پذیرش" if npv > 0 and bcr > 1 else "رد",
        }

    # =========================================================================
    # محاسبات فاکتور
    # =========================================================================

    @staticmethod
    def calculate_invoice(items: List[Dict], tax_rate: float = 9.0, discount_rate: float = 0.0) -> Dict:
        """محاسبه فاکتور"""
        subtotal = sum(item["quantity"] * item["unit_price"] for item in items)
        discount_amount = subtotal * (discount_rate / 100)
        subtotal_after_discount = subtotal - discount_amount
        tax_amount = subtotal_after_discount * (tax_rate / 100)
        total_amount = subtotal_after_discount + tax_amount

        return {
            "subtotal": round(subtotal, 2),
            "discount_rate": discount_rate,
            "discount_amount": round(discount_amount, 2),
            "tax_rate": tax_rate,
            "tax_amount": round(tax_amount, 2),
            "total_amount": round(total_amount, 2),
        }

    # =========================================================================
    # تحلیل نقطه سربه‌سر
    # =========================================================================

    @staticmethod
    def break_even_point(fixed_costs: float, price: float, variable_cost: float) -> Dict:
        """نقطه سربه‌سر"""
        contribution = price - variable_cost
        if contribution == 0:
            return {"units": 0, "revenue": 0, "contribution_margin": 0}

        units = fixed_costs / contribution
        revenue = units * price
        cm_ratio = (contribution / price * 100) if price else 0

        return {
            "units": round(units, 2),
            "revenue": round(revenue, 2),
            "contribution_margin": round(contribution, 2),
            "contribution_margin_ratio": round(cm_ratio, 2),
        }

    # =========================================================================
    # WACC & CAPM
    # =========================================================================

    @staticmethod
    def wacc(
        equity: float, debt: float,
        cost_of_equity: float, cost_of_debt: float,
        tax_rate: float
    ) -> float:
        """میانگین موزون هزینه سرمایه (WACC)"""
        total = equity + debt
        if total == 0: return 0
        we = equity / total
        wd = debt / total
        return (we * cost_of_equity + wd * cost_of_debt * (1 - tax_rate / 100))

    @staticmethod
    def capm(risk_free_rate: float, beta: float, market_return: float) -> float:
        """مدل قیمت‌گذاری دارایی سرمایه‌ای (CAPM)"""
        return risk_free_rate + beta * (market_return - risk_free_rate)

    # =========================================================================
    # شاخص‌های بورسی
    # =========================================================================

    @staticmethod
    def pe_ratio(price: float, eps: float) -> float:
        """نسبت قیمت به سود"""
        if eps == 0: return 0
        return price / eps

    @staticmethod
    def pb_ratio(price: float, book_value_per_share: float) -> float:
        """نسبت قیمت به ارزش دفتری"""
        if book_value_per_share == 0: return 0
        return price / book_value_per_share

    @staticmethod
    def dividend_yield(dividend_per_share: float, price: float) -> float:
        """بازده سود سهام"""
        if price == 0: return 0
        return (dividend_per_share / price) * 100

    @staticmethod
    def eps(net_income: float, preferred_dividends: float, shares_outstanding: float) -> float:
        """سود هر سهم"""
        if shares_outstanding == 0: return 0
        return (net_income - preferred_dividends) / shares_outstanding

    # =========================================================================
    # تحلیل جامع
    # =========================================================================

    @classmethod
    def comprehensive_analysis(cls, data: Dict) -> Dict:
        """تحلیل جامع مالی"""
        results = {}

        if all(k in data for k in ["revenue", "cogs", "net_income"]):
            results["profitability"] = {
                "gross_margin": cls.gross_margin(data["revenue"], data["cogs"]),
                "net_margin": cls.net_margin(data["net_income"], data["revenue"]),
                "roa": cls.roa(data["net_income"], data.get("total_assets", 0)),
                "roe": cls.roe(data["net_income"], data.get("equity", 0)),
            }

        if all(k in data for k in ["current_assets", "current_liabilities"]):
            results["liquidity"] = {
                "current_ratio": cls.current_ratio(data["current_assets"], data["current_liabilities"]),
                "quick_ratio": cls.quick_ratio(data["current_assets"], data.get("inventory", 0), data["current_liabilities"]),
                "working_capital": cls.working_capital(data["current_assets"], data["current_liabilities"]),
            }

        if all(k in data for k in ["total_debt", "equity"]):
            results["leverage"] = {
                "debt_to_equity": cls.debt_to_equity(data["total_debt"], data["equity"]),
                "debt_to_assets": cls.debt_to_assets(data["total_debt"], data.get("total_assets", 0)),
            }

        return results
'''

    write_file(API_DIR / "modules" / "financial" / "calculator.py", calculator_content)

    # =========================================================================
    # 3. Router API گسترده
    # =========================================================================
    print("\n🔌 ایجاد Router API گسترده...")

    router_content = '''# api/modules/financial/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.financial.models import (
    Account, Transaction, Invoice, InvoiceItem,
    InventoryProduct, InventoryMovement, Budget, FinancialMetric,
    Employee, PayrollRecord, Contract, ContractItem,
    Wallet, WalletTransaction, Payment, PaymentGateway, FixedAsset, Unit,
    TransactionType, InvoiceStatus, InventoryMethod,
    ContractStatus, ContractType, PaymentMethod, WalletTransactionType,
    DepreciationMethod, EmployeeStatus
)
from api.modules.financial.calculator import FinancialCalculator

router = APIRouter(prefix="/financial", tags=["Financial Management"])


# =========================================================================
# Pydantic Models
# =========================================================================
class InvoiceCreate(BaseModel):
    invoice_type: str
    customer_name: str
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    items: List[dict]
    tax_rate: float = 9.0
    discount_rate: float = 0.0
    due_date: Optional[str] = None
    notes: Optional[str] = None


class EmployeeCreate(BaseModel):
    employee_code: str
    full_name: str
    national_id: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    employment_date: Optional[str] = None
    base_salary: float = 0.0
    housing_allowance: float = 0.0
    food_allowance: float = 0.0
    child_allowance: float = 0.0
    bank_name: Optional[str] = None
    bank_account: Optional[str] = None
    insurance_number: Optional[str] = None


class ContractCreate(BaseModel):
    contract_type: str
    title: str
    description: Optional[str] = None
    party_a_name: Optional[str] = None
    party_b_name: Optional[str] = None
    contract_amount: float = 0.0
    tax_rate: float = 9.0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    items: List[dict] = []
    terms_and_conditions: Optional[str] = None


class WalletDeposit(BaseModel):
    user_id: int
    amount: float
    description: Optional[str] = None


class InventoryMovementCreate(BaseModel):
    product_id: int
    movement_type: str
    quantity: float
    description: Optional[str] = None
    created_by: Optional[int] = None


class ProductCreate(BaseModel):
    sku: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit_id: Optional[int] = None
    quantity: float = 0.0
    min_quantity: float = 0.0
    max_quantity: float = 0.0
    cost_price: float = 0.0
    selling_price: float = 0.0
    location: Optional[str] = None
    warehouse: Optional[str] = None


class InvoiceItemUpdate(BaseModel):
    product_name: str
    quantity: float
    unit_price: float
    discount: float = 0.0
    tax_rate: float = 9.0


# =========================================================================
# Dashboard
# =========================================================================
@router.get("/dashboard")
async def get_financial_dashboard(db: AsyncSession = Depends(get_db)):
    """داشبورد مالی جامع"""
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)

    revenue_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.INCOME) &
            (Transaction.transaction_date >= current_month_start)
        )
    )
    monthly_revenue = revenue_result.scalar() or 0

    expense_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.EXPENSE) &
            (Transaction.transaction_date >= current_month_start)
        )
    )
    monthly_expenses = expense_result.scalar() or 0

    net_profit = monthly_revenue - monthly_expenses

    overdue_invoices_result = await db.execute(
        select(func.count(Invoice.id)).where(
            (Invoice.status == InvoiceStatus.SENT) &
            (Invoice.due_date < datetime.now())
        )
    )
    overdue_invoices = overdue_invoices_result.scalar() or 0

    low_stock_result = await db.execute(
        select(func.count(InventoryProduct.id)).where(
            InventoryProduct.quantity <= InventoryProduct.min_quantity
        )
    )
    low_stock_products = low_stock_result.scalar() or 0

    inventory_value_result = await db.execute(
        select(func.sum(InventoryProduct.quantity * InventoryProduct.cost_price))
    )
    inventory_value = inventory_value_result.scalar() or 0

    # آمار کیف پول
    wallet_balance_result = await db.execute(
        select(func.sum(Wallet.balance))
    )
    total_wallet_balance = wallet_balance_result.scalar() or 0

    # آمار قراردادها
    active_contracts_result = await db.execute(
        select(func.count(Contract.id)).where(Contract.status == ContractStatus.ACTIVE)
    )
    active_contracts = active_contracts_result.scalar() or 0

    # آمار کارکنان
    active_employees_result = await db.execute(
        select(func.count(Employee.id)).where(Employee.status == EmployeeStatus.ACTIVE)
    )
    active_employees = active_employees_result.scalar() or 0

    # کل حقوق ماه جاری
    monthly_payroll_result = await db.execute(
        select(func.sum(PayrollRecord.net_salary)).where(
            (PayrollRecord.year == datetime.now().year) &
            (PayrollRecord.month == datetime.now().month)
        )
    )
    monthly_payroll = monthly_payroll_result.scalar() or 0

    return {
        "monthly_revenue": monthly_revenue,
        "monthly_expenses": monthly_expenses,
        "net_profit": net_profit,
        "profit_margin": FinancialCalculator.net_margin(net_profit, monthly_revenue) if monthly_revenue > 0 else 0,
        "overdue_invoices": overdue_invoices,
        "low_stock_products": low_stock_products,
        "inventory_value": inventory_value,
        "total_wallet_balance": total_wallet_balance,
        "active_contracts": active_contracts,
        "active_employees": active_employees,
        "monthly_payroll": monthly_payroll,
    }


# =========================================================================
# Units (واحدها)
# =========================================================================
@router.get("/units")
async def list_units(db: AsyncSession = Depends(get_db)):
    """لیست واحدهای اندازه‌گیری"""
    result = await db.execute(select(Unit).where(Unit.is_active == True))
    units = result.scalars().all()
    return {
        "units": [
            {
                "id": u.id, "code": u.code, "name": u.name,
                "category": u.category, "conversion_factor": u.conversion_factor,
            }
            for u in units
        ]
    }


@router.post("/units")
async def create_unit(unit_data: dict, db: AsyncSession = Depends(get_db)):
    """ایجاد واحد جدید"""
    unit = Unit(**unit_data)
    db.add(unit)
    await db.commit()
    return {"id": unit.id, "status": "created"}


@router.put("/units/{unit_id}")
async def update_unit(unit_id: int, unit_data: dict, db: AsyncSession = Depends(get_db)):
    """ویرایش واحد"""
    result = await db.execute(select(Unit).where(Unit.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit: raise HTTPException(404, "واحد یافت نشد")

    for key, value in unit_data.items():
        if hasattr(unit, key):
            setattr(unit, key, value)

    await db.commit()
    return {"status": "updated"}


@router.delete("/units/{unit_id}")
async def delete_unit(unit_id: int, db: AsyncSession = Depends(get_db)):
    """حذف واحد"""
    result = await db.execute(select(Unit).where(Unit.id == unit_id))
    unit = result.scalar_one_or_none()
    if not unit: raise HTTPException(404, "واحد یافت نشد")
    unit.is_active = False
    await db.commit()
    return {"status": "deleted"}


# =========================================================================
# Employees & Payroll
# =========================================================================
@router.get("/employees")
async def list_employees(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """لیست کارکنان"""
    query = select(Employee)
    if status:
        query = query.where(Employee.status == EmployeeStatus(status))
    result = await db.execute(query)
    employees = result.scalars().all()
    return {
        "employees": [
            {
                "id": e.id, "employee_code": e.employee_code, "full_name": e.full_name,
                "position": e.position, "department": e.department,
                "base_salary": e.base_salary, "status": e.status.value,
                "employment_date": e.employment_date,
            }
            for e in employees
        ]
    }


@router.post("/employees")
async def create_employee(data: EmployeeCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد کارمند"""
    employee = Employee(**data.dict())
    db.add(employee)
    await db.commit()
    return {"id": employee.id, "status": "created"}


@router.put("/employees/{employee_id}")
async def update_employee(employee_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """ویرایش کارمند"""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee: raise HTTPException(404, "کارمند یافت نشد")

    for key, value in data.items():
        if hasattr(employee, key):
            setattr(employee, key, value)

    await db.commit()
    return {"status": "updated"}


@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db: AsyncSession = Depends(get_db)):
    """حذف کارمند"""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee: raise HTTPException(404, "کارمند یافت نشد")
    employee.status = EmployeeStatus.TERMINATED
    await db.commit()
    return {"status": "terminated"}


@router.post("/payroll/calculate")
async def calculate_payroll(
    employee_id: int, year: int, month: int,
    overtime_hours: float = 0, bonuses: float = 0,
    db: AsyncSession = Depends(get_db)
):
    """محاسبه حقوق ماهانه"""
    result = await db.execute(select(Employee).where(Employee.id == employee_id))
    employee = result.scalar_one_or_none()
    if not employee: raise HTTPException(404, "کارمند یافت نشد")

    # محاسبه
    calc = FinancialCalculator.calculate_payroll(
        base_salary=employee.base_salary,
        housing_allowance=employee.housing_allowance,
        food_allowance=employee.food_allowance,
        child_allowance=employee.child_allowance,
        overtime_hours=overtime_hours,
        hourly_rate=employee.base_salary / 220 if employee.base_salary else 0,
        bonuses=bonuses,
        year=year,
    )

    # ذخیره
    record = PayrollRecord(
        employee_id=employee_id,
        year=year, month=month,
        base_salary=calc["base_salary"],
        overtime_hours=overtime_hours,
        overtime_pay=calc["overtime_pay"],
        bonuses=bonuses,
        allowances_total=calc["allowances"]["total"],
        gross_salary=calc["gross_salary"],
        insurance_employee=calc["deductions"]["insurance_employee"],
        insurance_employer=calc["deductions"]["insurance_employer"],
        tax_amount=calc["deductions"]["tax"],
        total_deductions=calc["deductions"]["total"],
        net_salary=calc["net_salary"],
    )
    db.add(record)
    await db.commit()

    return {"status": "calculated", "payroll": calc, "record_id": record.id}


@router.get("/payroll/{employee_id}")
async def get_payroll_history(employee_id: int, db: AsyncSession = Depends(get_db)):
    """تاریخچه حقوق کارمند"""
    result = await db.execute(
        select(PayrollRecord)
        .where(PayrollRecord.employee_id == employee_id)
        .order_by(PayrollRecord.year.desc(), PayrollRecord.month.desc())
    )
    records = result.scalars().all()
    return {
        "records": [
            {
                "id": r.id, "year": r.year, "month": r.month,
                "gross_salary": r.gross_salary, "net_salary": r.net_salary,
                "status": r.status,
            }
            for r in records
        ]
    }


# =========================================================================
# Contracts
# =========================================================================
@router.get("/contracts")
async def list_contracts(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """لیست قراردادها"""
    query = select(Contract)
    if status:
        query = query.where(Contract.status == ContractStatus(status))
    result = await db.execute(query.order_by(Contract.created_at.desc()))
    contracts = result.scalars().all()
    return {
        "contracts": [
            {
                "id": c.id, "contract_number": c.contract_number,
                "contract_type": c.contract_type.value, "title": c.title,
                "status": c.status.value, "contract_amount": c.contract_amount,
                "total_amount": c.total_amount, "paid_amount": c.paid_amount,
                "start_date": c.start_date, "end_date": c.end_date,
            }
            for c in contracts
        ]
    }


@router.post("/contracts")
async def create_contract(data: ContractCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد قرارداد"""
    contract_number = f"CON-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    tax_amount = data.contract_amount * (data.tax_rate / 100)
    total_amount = data.contract_amount + tax_amount

    contract = Contract(
        contract_number=contract_number,
        contract_type=ContractType(data.contract_type),
        title=data.title,
        description=data.description,
        party_a_name=data.party_a_name,
        party_b_name=data.party_b_name,
        contract_amount=data.contract_amount,
        tax_rate=data.tax_rate,
        tax_amount=tax_amount,
        total_amount=total_amount,
        remaining_amount=total_amount,
        start_date=date.fromisoformat(data.start_date) if data.start_date else None,
        end_date=date.fromisoformat(data.end_date) if data.end_date else None,
        terms_and_conditions=data.terms_and_conditions,
    )
    db.add(contract)
    await db.flush()

    for item_data in data.items:
        item = ContractItem(
            contract_id=contract.id,
            description=item_data["description"],
            quantity=item_data.get("quantity", 1),
            unit_price=item_data.get("unit_price", 0),
            total_price=item_data.get("quantity", 1) * item_data.get("unit_price", 0),
        )
        db.add(item)

    await db.commit()
    return {"id": contract.id, "contract_number": contract_number, "status": "created"}


@router.put("/contracts/{contract_id}")
async def update_contract(contract_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """ویرایش قرارداد"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract: raise HTTPException(404, "قرارداد یافت نشد")

    for key, value in data.items():
        if hasattr(contract, key):
            setattr(contract, key, value)

    await db.commit()
    return {"status": "updated"}


@router.delete("/contracts/{contract_id}")
async def delete_contract(contract_id: int, db: AsyncSession = Depends(get_db)):
    """حذف قرارداد"""
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract: raise HTTPException(404, "قرارداد یافت نشد")
    contract.status = ContractStatus.TERMINATED
    await db.commit()
    return {"status": "terminated"}


# =========================================================================
# Wallet
# =========================================================================
@router.get("/wallet/{user_id}")
async def get_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت کیف پول"""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        await db.commit()
    return {"user_id": user_id, "balance": wallet.balance, "currency": wallet.currency}


@router.post("/wallet/deposit")
async def deposit_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    """شارژ کیف پول (شبیه‌سازی درگاه)"""
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=data.user_id, balance=0.0)
        db.add(wallet)
        await db.flush()

    balance_before = wallet.balance
    wallet.balance += data.amount

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type=WalletTransactionType.DEPOSIT,
        amount=data.amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        description=data.description or "شارژ کیف پول",
        reference_number=f"DEP-{int(datetime.now().timestamp())}",
    )
    db.add(transaction)
    await db.commit()

    return {
        "status": "success",
        "new_balance": wallet.balance,
        "transaction_id": transaction.id,
        "message": "کیف پول با موفقیت شارژ شد"
    }


@router.post("/wallet/withdraw")
async def withdraw_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    """برداشت از کیف پول"""
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet or wallet.balance < data.amount:
        raise HTTPException(400, "موجودی کافی نیست")

    balance_before = wallet.balance
    wallet.balance -= data.amount

    transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type=WalletTransactionType.WITHDRAWAL,
        amount=data.amount,
        balance_before=balance_before,
        balance_after=wallet.balance,
        description=data.description or "برداشت از کیف پول",
    )
    db.add(transaction)
    await db.commit()

    return {"status": "success", "new_balance": wallet.balance}


@router.get("/wallet/{user_id}/transactions")
async def get_wallet_transactions(user_id: int, db: AsyncSession = Depends(get_db)):
    """تاریخچه تراکنش‌های کیف پول"""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        return {"transactions": []}

    tx_result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.wallet_id == wallet.id)
        .order_by(WalletTransaction.created_at.desc())
    )
    transactions = tx_result.scalars().all()

    return {
        "transactions": [
            {
                "id": t.id, "type": t.transaction_type.value,
                "amount": t.amount, "balance_after": t.balance_after,
                "description": t.description, "created_at": t.created_at,
            }
            for t in transactions
        ]
    }


# =========================================================================
# Payment Gateway
# =========================================================================
@router.post("/payment/initiate")
async def initiate_payment(
    user_id: int, amount: float, description: Optional[str] = None,
    callback_url: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """شروع پرداخت (شبیه‌سازی درگاه)"""
    payment_number = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    payment = Payment(
        payment_number=payment_number,
        user_id=user_id,
        amount=amount,
        description=description,
        status="pending",
    )
    db.add(payment)
    await db.commit()

    # شبیه‌سازی درگاه پرداخت
    payment_url = f"http://localhost:3001/payment/gateway?ref={payment_number}"

    return {
        "status": "initiated",
        "payment_number": payment_number,
        "payment_url": payment_url,
        "amount": amount,
    }


@router.post("/payment/verify")
async def verify_payment(payment_number: str, status: str = "success", db: AsyncSession = Depends(get_db)):
    """تأیید پرداخت (شبیه‌سازی)"""
    result = await db.execute(
        select(Payment).where(Payment.payment_number == payment_number)
    )
    payment = result.scalar_one_or_none()
    if not payment: raise HTTPException(404, "پرداخت یافت نشد")

    if status == "success":
        payment.status = "success"
        payment.completed_at = datetime.now()
        payment.tracking_code = f"TRK-{int(datetime.now().timestamp())}"

        # افزودن به کیف پول
        wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == payment.user_id))
        wallet = wallet_result.scalar_one_or_none()
        if wallet:
            balance_before = wallet.balance
            wallet.balance += payment.amount
            tx = WalletTransaction(
                wallet_id=wallet.id,
                transaction_type=WalletTransactionType.DEPOSIT,
                amount=payment.amount,
                balance_before=balance_before,
                balance_after=wallet.balance,
                description=f"پرداخت از درگاه - {payment.payment_number}",
                reference_number=payment.tracking_code,
            )
            db.add(tx)

    else:
        payment.status = "failed"

    await db.commit()
    return {"status": payment.status, "payment_number": payment_number}


# =========================================================================
# Inventory (CRUD کامل)
# =========================================================================
@router.get("/inventory")
async def list_inventory(
    category: Optional[str] = None, low_stock_only: bool = False,
    search: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """لیست موجودی انبار"""
    query = select(InventoryProduct).where(InventoryProduct.is_active == True)
    if category: query = query.where(InventoryProduct.category == category)
    if low_stock_only: query = query.where(InventoryProduct.quantity <= InventoryProduct.min_quantity)
    if search: query = query.where(InventoryProduct.name.ilike(f"%{search}%"))

    result = await db.execute(query)
    products = result.scalars().all()

    recommendations = []
    for p in products:
        if p.quantity <= p.min_quantity:
            recommendations.append({
                "product_id": p.id, "product_name": p.name,
                "level": "critical", "current": p.quantity, "min": p.min_quantity,
            })

    return {
        "products": [
            {
                "id": p.id, "sku": p.sku, "name": p.name, "category": p.category,
                "quantity": p.quantity, "min_quantity": p.min_quantity,
                "max_quantity": p.max_quantity, "cost_price": p.cost_price,
                "selling_price": p.selling_price,
                "total_value": p.quantity * p.cost_price,
                "is_low_stock": p.quantity <= p.min_quantity,
            }
            for p in products
        ],
        "total_value": sum(p.quantity * p.cost_price for p in products),
        "total_products": len(products),
        "low_stock_count": sum(1 for p in products if p.quantity <= p.min_quantity),
        "recommendations": recommendations,
    }


@router.post("/inventory")
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد محصول جدید"""
    product = InventoryProduct(**data.dict())
    db.add(product)
    await db.commit()
    return {"id": product.id, "status": "created"}


@router.put("/inventory/{product_id}")
async def update_product(product_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """ویرایش محصول"""
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")

    for key, value in data.items():
        if hasattr(product, key):
            setattr(product, key, value)

    await db.commit()
    return {"status": "updated"}


@router.delete("/inventory/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """حذف محصول"""
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")
    product.is_active = False
    await db.commit()
    return {"status": "deleted"}


@router.post("/inventory/movements")
async def create_movement(data: InventoryMovementCreate, db: AsyncSession = Depends(get_db)):
    """ثبت حرکت انبار"""
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == data.product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")

    quantity_before = product.quantity

    if data.movement_type == "in":
        product.quantity += data.quantity
    elif data.movement_type == "out":
        if product.quantity < data.quantity:
            raise HTTPException(400, "موجودی کافی نیست")
        product.quantity -= data.quantity
    elif data.movement_type == "adjustment":
        product.quantity = data.quantity

    movement = InventoryMovement(
        product_id=data.product_id,
        movement_type=data.movement_type,
        quantity=data.quantity,
        quantity_before=quantity_before,
        quantity_after=product.quantity,
        description=data.description,
        created_by=data.created_by,
    )
    db.add(movement)
    await db.commit()

    return {
        "status": "success",
        "quantity_before": quantity_before,
        "quantity_after": product.quantity,
    }


@router.get("/inventory/{product_id}/recommendations")
async def get_inventory_recommendations(product_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت توصیه‌های هوشمند انبارداری"""
    result = await db.execute(select(InventoryProduct).where(InventoryProduct.id == product_id))
    product = result.scalar_one_or_none()
    if not product: raise HTTPException(404, "محصول یافت نشد")

    recommendations = FinancialCalculator.inventory_recommendations(
        current_stock=product.quantity,
        min_stock=product.min_quantity,
        max_stock=product.max_quantity,
        reorder_point=product.reorder_point or product.min_quantity * 2,
        daily_demand=10,  # فرضی
        lead_time=7,  # فرضی
    )

    return {"product": product.name, "recommendations": recommendations}


# =========================================================================
# Invoices (CRUD کامل)
# =========================================================================
@router.get("/invoices")
async def list_invoices(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """لیست فاکتورها"""
    query = select(Invoice)
    if status: query = query.where(Invoice.status == InvoiceStatus(status))
    result = await db.execute(query.order_by(Invoice.issue_date.desc()))
    invoices = result.scalars().all()
    return {
        "invoices": [
            {
                "id": inv.id, "invoice_number": inv.invoice_number,
                "invoice_type": inv.invoice_type, "status": inv.status.value,
                "customer_name": inv.customer_name, "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount, "remaining_amount": inv.remaining_amount,
                "issue_date": inv.issue_date, "due_date": inv.due_date,
            }
            for inv in invoices
        ]
    }


@router.post("/invoices")
async def create_invoice(data: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد فاکتور"""
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    calculation = FinancialCalculator.calculate_invoice(data.items, data.tax_rate, data.discount_rate)

    invoice = Invoice(
        invoice_number=invoice_number,
        invoice_type=data.invoice_type,
        status=InvoiceStatus.DRAFT,
        customer_name=data.customer_name,
        customer_email=data.customer_email,
        customer_phone=data.customer_phone,
        customer_address=data.customer_address,
        subtotal=calculation["subtotal"],
        tax_rate=data.tax_rate,
        tax_amount=calculation["tax_amount"],
        discount_rate=data.discount_rate,
        discount_amount=calculation["discount_amount"],
        total_amount=calculation["total_amount"],
        remaining_amount=calculation["total_amount"],
        due_date=datetime.fromisoformat(data.due_date) if data.due_date else None,
        notes=data.notes,
    )
    db.add(invoice)
    await db.flush()

    for item_data in data.items:
        item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.get("product_id"),
            product_name=item_data["product_name"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            discount=item_data.get("discount", 0),
            tax_rate=item_data.get("tax_rate", data.tax_rate),
            total_price=item_data["quantity"] * item_data["unit_price"],
        )
        db.add(item)

    await db.commit()
    return {"id": invoice.id, "invoice_number": invoice_number, "total_amount": calculation["total_amount"]}


@router.put("/invoices/{invoice_id}")
async def update_invoice(invoice_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """ویرایش فاکتور"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice: raise HTTPException(404, "فاکتور یافت نشد")

    for key, value in data.items():
        if hasattr(invoice, key):
            setattr(invoice, key, value)

    await db.commit()
    return {"status": "updated"}


@router.delete("/invoices/{invoice_id}")
async def delete_invoice(invoice_id: int, db: AsyncSession = Depends(get_db)):
    """حذف فاکتور"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    if not invoice: raise HTTPException(404, "فاکتور یافت نشد")
    invoice.status = InvoiceStatus.CANCELLED
    await db.commit()
    return {"status": "cancelled"}


# =========================================================================
# Financial Calculators
# =========================================================================
@router.post("/calculate/npv")
async def calculate_npv(cash_flows: List[float], discount_rate: float):
    """محاسبه NPV"""
    npv = FinancialCalculator.npv(cash_flows, discount_rate / 100)
    return {"npv": round(npv, 2), "recommendation": "پذیرش" if npv > 0 else "رد"}


@router.post("/calculate/irr")
async def calculate_irr(cash_flows: List[float]):
    """محاسبه IRR"""
    irr = FinancialCalculator.irr(cash_flows)
    return {"irr": round(irr * 100, 2) if irr else None}


@router.post("/calculate/break-even")
async def calculate_break_even(fixed_costs: float, price: float, variable_cost: float):
    """محاسبه نقطه سربه‌سر"""
    return FinancialCalculator.break_even_point(fixed_costs, price, variable_cost)


@router.post("/calculate/eoq")
async def calculate_eoq(annual_demand: float, ordering_cost: float, holding_cost: float):
    """محاسبه EOQ"""
    eoq = FinancialCalculator.eoq(annual_demand, ordering_cost, holding_cost)
    return {"eoq": round(eoq, 2)}


@router.post("/calculate/loan")
async def calculate_loan(principal: float, annual_rate: float, years: int):
    """محاسبه اقساط وام"""
    payment = FinancialCalculator.loan_payment(principal, annual_rate, years)
    schedule = FinancialCalculator.loan_amortization_schedule(principal, annual_rate, years)
    total_payment = payment * years * 12
    total_interest = total_payment - principal

    return {
        "monthly_payment": round(payment, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "schedule": schedule[:12],  # 12 ماه اول
    }


@router.post("/calculate/payroll")
async def calculate_payroll_api(
    base_salary: float, housing: float = 0, food: float = 0,
    child: float = 0, overtime_hours: float = 0, bonuses: float = 0
):
    """محاسبه حقوق"""
    return FinancialCalculator.calculate_payroll(
        base_salary=base_salary,
        housing_allowance=housing,
        food_allowance=food,
        child_allowance=child,
        overtime_hours=overtime_hours,
        hourly_rate=base_salary / 220,
        bonuses=bonuses,
    )


@router.post("/calculate/cba")
async def calculate_cba(
    initial_investment: float, annual_benefits: List[float],
    annual_costs: List[float], discount_rate: float
):
    """تحلیل هزینه-فایده"""
    return FinancialCalculator.cost_benefit_analysis(
        initial_investment, annual_benefits, annual_costs, discount_rate / 100, len(annual_benefits)
    )


@router.post("/calculate/wacc")
async def calculate_wacc(
    equity: float, debt: float, cost_of_equity: float,
    cost_of_debt: float, tax_rate: float
):
    """محاسبه WACC"""
    return {"wacc": round(FinancialCalculator.wacc(equity, debt, cost_of_equity, cost_of_debt, tax_rate), 2)}


@router.post("/calculate/capm")
async def calculate_capm(risk_free_rate: float, beta: float, market_return: float):
    """محاسبه CAPM"""
    return {"expected_return": round(FinancialCalculator.capm(risk_free_rate, beta, market_return), 2)}


@router.post("/calculate/depreciation")
async def calculate_depreciation(
    cost: float, salvage: float, years: int, method: str = "straight_line"
):
    """محاسبه استهلاک"""
    if method == "straight_line":
        annual = FinancialCalculator.straight_line_depreciation(cost, salvage, years)
        return {"method": method, "annual_depreciation": round(annual, 2)}
    elif method == "declining_balance":
        schedule = FinancialCalculator.declining_balance_depreciation(cost, salvage, years)
        return {"method": method, "schedule": schedule}
    elif method == "sum_of_years":
        schedule = FinancialCalculator.sum_of_years_depreciation(cost, salvage, years)
        return {"method": method, "schedule": schedule}
    else:
        raise HTTPException(400, "روش نامعتبر")


@router.post("/calculate/ratios")
async def calculate_ratios(financial_data: dict):
    """محاسبه شاخص‌های مالی"""
    return FinancialCalculator.comprehensive_analysis(financial_data)


# =========================================================================
# Reports
# =========================================================================
@router.get("/reports/profit-loss")
async def profit_loss_report(start_date: str, end_date: str, db: AsyncSession = Depends(get_db)):
    """گزارش سود و زیان"""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    revenue_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.INCOME) &
            (Transaction.transaction_date.between(start, end))
        )
    )
    revenue = revenue_result.scalar() or 0

    expense_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.EXPENSE) &
            (Transaction.transaction_date.between(start, end))
        )
    )
    expenses = expense_result.scalar() or 0

    return {
        "period": {"start": start_date, "end": end_date},
        "revenue": revenue, "expenses": expenses,
        "net_profit": revenue - expenses,
        "profit_margin": FinancialCalculator.net_margin(revenue - expenses, revenue) if revenue > 0 else 0,
    }
'''

    write_file(API_DIR / "modules" / "financial" / "router.py", router_content)

    # =========================================================================
    # 4. __init__.py
    # =========================================================================
    print("\n📦 ایجاد __init__.py...")
    write_file(API_DIR / "modules" / "financial" / "__init__.py", "from . import models, router, calculator\n")

    # =========================================================================
    # 5. فرانت‌اند پیشرفته
    # =========================================================================
    print("\n🎨 ایجاد داشبورد فرانت‌اند پیشرفته...")

    frontend_content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
import {
  ArrowRight, DollarSign, Package, FileText, TrendingUp, TrendingDown,
  Plus, Edit, Trash2, Eye, Download, Filter, Search, Calendar,
  AlertTriangle, CheckCircle, Clock, Wallet, BarChart3,
  ShoppingCart, Users, CreditCard, Receipt, Calculator, Briefcase,
  FileSignature, PiggyBank, Building2, Landmark, Shield, Settings,
  X, Save, ChevronDown, ChevronRight, Percent, Scale, Target
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/financial";

export default function FinancialPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState<any>(null);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [inventory, setInventory] = useState<any>(null);
  const [employees, setEmployees] = useState<any[]>([]);
  const [contracts, setContracts] = useState<any[]>([]);
  const [walletBalance, setWalletBalance] = useState(0);
  const [showModal, setShowModal] = useState<string | null>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [dashRes, invRes, invRes2, empRes, conRes, walRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard`),
        fetch(`${API_BASE}/invoices`),
        fetch(`${API_BASE}/inventory`),
        fetch(`${API_BASE}/employees`),
        fetch(`${API_BASE}/contracts`),
        fetch(`${API_BASE}/wallet/1`),
      ]);
      if (dashRes.ok) setDashboard(await dashRes.json());
      if (invRes.ok) setInvoices((await invRes.json()).invoices || []);
      if (invRes2.ok) setInventory(await invRes2.json());
      if (empRes.ok) setEmployees((await empRes.json()).employees || []);
      if (conRes.ok) setContracts((await conRes.json()).contracts || []);
      if (walRes.ok) setWalletBalance((await walRes.json()).balance || 0);
    } catch (error) { console.error("Error:", error); }
  };

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#3b82f6" },
    { id: "invoices", label: "فاکتورها", icon: FileText, color: "#10b981" },
    { id: "inventory", label: "انبار", icon: Package, color: "#f59e0b" },
    { id: "employees", label: "حقوق و دستمزد", icon: Users, color: "#8b5cf6" },
    { id: "contracts", label: "قراردادها", icon: FileSignature, color: "#ec4899" },
    { id: "wallet", label: "کیف پول", icon: Wallet, color: "#06b6d4" },
    { id: "calculators", label: "ماشین حساب", icon: Calculator, color: "#ef4444" },
    { id: "reports", label: "گزارش‌ها", icon: TrendingUp, color: "#14b8a6" },
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
                <Landmark className="h-10 w-10 text-white" />
              </div>
              <div>
                <p className="text-blue-400 text-sm font-medium mb-1">سیستم مدیریت مالی یکپارچه</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">حسابداری، انبارداری و مالی</h1>
                <p className="text-lg text-slate-300">مدیریت مالی، حقوق، قراردادها، کیف پول و تحلیل‌های پیشرفته اقتصادی</p>
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
        {activeTab === "dashboard" && dashboard && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "درآمد ماه", value: dashboard.monthly_revenue, icon: TrendingUp, color: "#10b981" },
                { label: "هزینه‌ها", value: dashboard.monthly_expenses, icon: TrendingDown, color: "#ef4444" },
                { label: "سود خالص", value: dashboard.net_profit, icon: DollarSign, color: "#3b82f6" },
                { label: "ارزش موجودی", value: dashboard.inventory_value, icon: Package, color: "#f59e0b" },
                { label: "موجودی کیف پول", value: dashboard.total_wallet_balance, icon: Wallet, color: "#06b6d4" },
                { label: "قراردادهای فعال", value: dashboard.active_contracts, icon: FileSignature, color: "#ec4899" },
                { label: "کارکنان", value: dashboard.active_employees, icon: Users, color: "#8b5cf6" },
                { label: "حقوق ماه", value: dashboard.monthly_payroll, icon: Briefcase, color: "#14b8a6" },
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5"
                >
                  <stat.icon className="h-6 w-6 mb-2" style={{ color: stat.color }} />
                  <p className="text-2xl font-black text-white">{typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}</p>
                  <p className="text-xs text-slate-400">{stat.label}</p>
                </motion.div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  هشدارها
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
                    <span className="text-slate-300">فاکتورهای معوق</span>
                    <span className="text-2xl font-black text-red-400">{dashboard.overdue_invoices}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                    <span className="text-slate-300">کم‌موجودی</span>
                    <span className="text-2xl font-black text-amber-400">{dashboard.low_stock_products}</span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4">حاشیه سود</h3>
                <div className="text-center">
                  <p className="text-5xl font-black" style={{ color: dashboard.profit_margin > 0 ? "#10b981" : "#ef4444" }}>
                    {dashboard.profit_margin.toFixed(1)}%
                  </p>
                  <p className="text-sm text-slate-400 mt-2">نسبت سود به درآمد</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Invoices */}
        {activeTab === "invoices" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">فاکتورها</h2>
              <button onClick={() => setShowModal("invoice")} className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> فاکتور جدید
              </button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">شماره</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">مشتری</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">مبلغ</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">وضعیت</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map(inv => (
                    <tr key={inv.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono text-sm">{inv.invoice_number}</td>
                      <td className="px-6 py-4 text-slate-300">{inv.customer_name}</td>
                      <td className="px-6 py-4 text-white font-bold">{inv.total_amount?.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          inv.status === "paid" ? "bg-emerald-500/20 text-emerald-300" :
                          inv.status === "sent" ? "bg-blue-500/20 text-blue-300" :
                          inv.status === "overdue" ? "bg-red-500/20 text-red-300" :
                          "bg-slate-500/20 text-slate-300"
                        }`}>
                          {inv.status === "paid" ? "پرداخت شده" : inv.status === "sent" ? "ارسال شده" : inv.status === "overdue" ? "معوق" : "پیش‌نویس"}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg"><Eye className="h-4 w-4" /></button>
                          <button className="p-2 text-emerald-400 hover:bg-emerald-500/20 rounded-lg"><Edit className="h-4 w-4" /></button>
                          <button className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg"><Trash2 className="h-4 w-4" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Inventory */}
        {activeTab === "inventory" && inventory && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">انبارداری</h2>
              <button onClick={() => setShowModal("product")} className="px-6 py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> محصول جدید
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <p className="text-sm text-slate-400 mb-2">ارزش کل</p>
                <p className="text-3xl font-black text-white">{inventory.total_value?.toLocaleString()}</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <p className="text-sm text-slate-400 mb-2">تعداد محصولات</p>
                <p className="text-3xl font-black text-white">{inventory.total_products}</p>
              </div>
              <div className="bg-slate-900/50 border border-red-500/30 rounded-2xl p-6">
                <p className="text-sm text-red-300 mb-2">کم‌موجودی</p>
                <p className="text-3xl font-black text-red-400">{inventory.low_stock_count}</p>
              </div>
            </div>
            {inventory.recommendations?.length > 0 && (
              <div className="bg-amber-500/10 border border-amber-500/30 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-amber-300 mb-3 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5" /> توصیه‌های هوشمند انبارداری
                </h3>
                <div className="space-y-2">
                  {inventory.recommendations.map((rec: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-xl">
                      <span className="text-slate-300">{rec.product_name}</span>
                      <span className="text-amber-400 font-bold">موجودی: {rec.current} / حداقل: {rec.min}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Employees */}
        {activeTab === "employees" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">حقوق و دستمزد</h2>
              <button onClick={() => setShowModal("employee")} className="px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> کارمند جدید
              </button>
            </div>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">کد</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نام</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">سمت</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">حقوق پایه</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {employees.map(emp => (
                    <tr key={emp.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono">{emp.employee_code}</td>
                      <td className="px-6 py-4 text-white">{emp.full_name}</td>
                      <td className="px-6 py-4 text-slate-300">{emp.position}</td>
                      <td className="px-6 py-4 text-emerald-400 font-bold">{emp.base_salary?.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm">محاسبه حقوق</button>
                          <button className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg"><Edit className="h-4 w-4" /></button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Contracts */}
        {activeTab === "contracts" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">قراردادهای هوشمند</h2>
              <button onClick={() => setShowModal("contract")} className="px-6 py-3 bg-pink-600 hover:bg-pink-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> قرارداد جدید
              </button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {contracts.map(contract => (
                <motion.div
                  key={contract.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-pink-500/50 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs font-mono text-slate-500">{contract.contract_number}</span>
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      contract.status === "active" ? "bg-emerald-500/20 text-emerald-300" :
                      contract.status === "completed" ? "bg-blue-500/20 text-blue-300" :
                      "bg-slate-500/20 text-slate-300"
                    }`}>
                      {contract.status === "active" ? "فعال" : contract.status === "completed" ? "تکمیل" : contract.status}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{contract.title}</h3>
                  <p className="text-sm text-slate-400 mb-4">{contract.contract_type}</p>
                  <div className="space-y-2 mb-4">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">مبلغ کل:</span>
                      <span className="text-white font-bold">{contract.total_amount?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-400">پرداخت شده:</span>
                      <span className="text-emerald-400 font-bold">{contract.paid_amount?.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-pink-500 to-rose-500"
                      style={{ width: `${contract.total_amount ? (contract.paid_amount / contract.total_amount * 100) : 0}%` }}
                    />
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Wallet */}
        {activeTab === "wallet" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 rounded-3xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-cyan-300 text-sm mb-2">موجودی کیف پول</p>
                  <p className="text-5xl font-black text-white">{walletBalance.toLocaleString()} <span className="text-xl">تومان</span></p>
                </div>
                <Wallet className="h-16 w-16 text-cyan-400" />
              </div>
              <div className="flex gap-3">
                <button onClick={() => setShowModal("deposit")} className="flex-1 py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-xl font-bold">
                  شارژ کیف پول
                </button>
                <button onClick={() => setShowModal("withdraw")} className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold">
                  برداشت
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <CreditCard className="h-8 w-8 text-blue-400 mb-3" />
                <h3 className="font-bold text-white mb-2">درگاه پرداخت</h3>
                <p className="text-sm text-slate-400 mb-3">پرداخت آنلاین از طریق درگاه‌های معتبر</p>
                <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm">اتصال به درگاه</button>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <PiggyBank className="h-8 w-8 text-emerald-400 mb-3" />
                <h3 className="font-bold text-white mb-2">انتقال به کیف پول</h3>
                <p className="text-sm text-slate-400 mb-3">انتقال مستقیم از حساب بانکی</p>
                <button className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm">انتقال</button>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <Shield className="h-8 w-8 text-purple-400 mb-3" />
                <h3 className="font-bold text-white mb-2">امنیت</h3>
                <p className="text-sm text-slate-400 mb-3">رمزنگاری پیشرفته و احراز هویت دو مرحله‌ای</p>
                <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm">تنظیمات</button>
              </div>
            </div>
          </div>
        )}

        {/* Calculators */}
        {activeTab === "calculators" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "NPV (ارزش فعلی خالص)", color: "#3b82f6", icon: TrendingUp, fields: ["جریان‌های نقدی", "نرخ تنزیل (%)"] },
              { title: "IRR (نرخ بازگشت داخلی)", color: "#10b981", icon: Percent, fields: ["جریان‌های نقدی"] },
              { title: "نقطه سربه‌سر", color: "#f59e0b", icon: Target, fields: ["هزینه ثابت", "قیمت فروش", "هزینه متغیر"] },
              { title: "EOQ (مقدار اقتصادی سفارش)", color: "#8b5cf6", icon: Package, fields: ["تقاضای سالانه", "هزینه سفارش", "هزینه نگهداری"] },
              { title: "اقساط وام", color: "#ef4444", icon: Landmark, fields: ["مبلغ وام", "نرخ سالانه (%)", "مدت (سال)"] },
              { title: "حقوق و دستمزد", color: "#ec4899", icon: Briefcase, fields: ["حقوق پایه", "مسکن", "خواربار", "اضافه‌کار"] },
              { title: "استهلاک", color: "#14b8a6", icon: Scale, fields: ["قیمت خرید", "ارزش اسقاط", "عمر مفید"] },
              { title: "WACC", color: "#f97316", icon: Building2, fields: ["حقوق", "بدهی", "هزینه حقوق", "هزینه بدهی", "نرخ مالیات"] },
              { title: "CAPM", color: "#06b6d4", icon: BarChart3, fields: ["نرخ بدون ریسک", "Beta", "بازده بازار"] },
              { title: "تحلیل هزینه-فایده", color: "#84cc16", icon: Calculator, fields: ["سرمایه اولیه", "منافع سالانه", "هزینه‌های سالانه", "نرخ تنزیل"] },
              { title: "ROI", color: "#a855f7", icon: TrendingUp, fields: ["سود خالص", "هزینه سرمایه‌گذاری"] },
              { title: "نسبت‌های مالی", color: "#6366f1", icon: BarChart3, fields: ["درآمد", "بهای تمام‌شده", "سود خالص", "دارایی‌ها"] },
            ].map((calc, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-3 rounded-xl" style={{ backgroundColor: calc.color + "20" }}>
                    <calc.icon className="h-6 w-6" style={{ color: calc.color }} />
                  </div>
                  <h3 className="text-lg font-bold text-white">{calc.title}</h3>
                </div>
                <div className="space-y-2">
                  {calc.fields.map((field, i) => (
                    <input key={i} type={field.includes("درصد") ? "number" : "text"} placeholder={field} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm focus:border-blue-500 focus:outline-none" />
                  ))}
                  <button className="w-full py-2 text-white rounded-lg font-bold text-sm" style={{ backgroundColor: calc.color }}>
                    محاسبه
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {/* Reports */}
        {activeTab === "reports" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">گزارش سود و زیان</h3>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <input type="date" className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                  <input type="date" className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                </div>
                <button className="w-full py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-bold">تولید گزارش</button>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">ترازنامه</h3>
                <p className="text-sm text-slate-400 mb-4">وضعیت دارایی‌ها، بدهی‌ها و حقوق صاحبان سهام</p>
                <button className="w-full py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-bold">مشاهده ترازنامه</button>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">جریان وجوه نقد</h3>
                <p className="text-sm text-slate-400 mb-4">تحلیل ورودی و خروجی وجه نقد</p>
                <button className="w-full py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-bold">تحلیل جریان</button>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4">گزارش مالیاتی</h3>
                <p className="text-sm text-slate-400 mb-4">محاسبه و گزارش مالیات‌های فصلی و سالانه</p>
                <button className="w-full py-2 bg-teal-600 hover:bg-teal-700 text-white rounded-lg font-bold">گزارش مالیاتی</button>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Modal */}
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
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  {showModal === "invoice" && "فاکتور جدید"}
                  {showModal === "product" && "محصول جدید"}
                  {showModal === "employee" && "کارمند جدید"}
                  {showModal === "contract" && "قرارداد جدید"}
                  {showModal === "deposit" && "شارژ کیف پول"}
                  {showModal === "withdraw" && "برداشت از کیف پول"}
                </h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="space-y-4">
                {showModal === "deposit" || showModal === "withdraw" ? (
                  <>
                    <input type="number" placeholder="مبلغ (تومان)" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    <input type="text" placeholder="توضیحات" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    <button className="w-full py-3 bg-cyan-600 hover:bg-cyan-700 text-white rounded-xl font-bold">
                      {showModal === "deposit" ? "شارژ" : "برداشت"}
                    </button>
                  </>
                ) : (
                  <>
                    <input type="text" placeholder="عنوان / نام" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    <input type="text" placeholder="توضیحات" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    <input type="number" placeholder="مبلغ" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                      <Save className="h-5 w-5" /> ذخیره
                    </button>
                  </>
                )}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''

    write_file(WEB_DIR / "app" / "financial" / "page.tsx", frontend_content)

    # =========================================================================
    # 6. به‌روزرسانی main.py
    # =========================================================================
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    if main_path.exists():
        content = main_path.read_text(encoding="utf-8")
        if "financial_router" not in content:
            lines = content.split('\n')
            import_idx = router_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from api.modules."): import_idx = i
                if "app.include_router(" in line: router_idx = i
            lines.insert(import_idx + 1, "from api.modules.financial.router import router as financial_router")
            lines.insert(router_idx + 2, 'app.include_router(financial_router, prefix="/api/v1")')
            main_path.write_text('\n'.join(lines), encoding="utf-8")
            print("   ✅ financial_router اضافه شد")

    # =========================================================================
    # 7. پاک‌سازی کش
    # =========================================================================
    print("\n🧹 پاک‌سازی کش...")
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("   ✅ کش Next.js حذف شد")
        except Exception as e:
            print(f"   ⚠️  خطا: {e}")

    # =========================================================================
    # خلاصه
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ ماژول جامع مالی با موفقیت ارتقاء یافت!")
    print("\n🎯 بخش‌های جدید:")
    print("   💼 حقوق و دستمزد (CRUD کامل + محاسبه مالیات ایران)")
    print("   📝 قراردادهای هوشمند (CRUD کامل)")
    print("   💳 کیف پول (شارژ، برداشت، تاریخچه)")
    print("   🏦 درگاه پرداخت (شبیه‌سازی)")
    print("   📏 واحدهای اندازه‌گیری (CRUD)")
    print("   🧠 توصیه‌های هوشمند انبارداری")
    print("   📊 تحلیل هزینه-فایده (CBA)")
    print("   🏛️ محاسبات وام و استهلاک")
    print("   📈 شاخص‌های بورسی (P/E, P/B, CAPM, WACC)")
    print("")
    print("🧮 ۱۲ ماشین حساب مالی:")
    print("   NPV, IRR, Payback, ROI, Break-even, EOQ")
    print("   Loan Amortization, Payroll, Depreciation")
    print("   WACC, CAPM, Financial Ratios")
    print("")
    print("✏️ CRUD کامل برای:")
    print("   • فاکتورها (ایجاد، ویرایش، حذف)")
    print("   • محصولات انبار (ایجاد، ویرایش، حذف)")
    print("   • کارکنان (ایجاد، ویرایش، حذف)")
    print("   • قراردادها (ایجاد، ویرایش، حذف)")
    print("   • واحدها (ایجاد، ویرایش، حذف)")
    print("")
    print("🚀 گام بعدی:")
    print("   1. uvicorn api.main:app --reload --port 8000")
    print("   2. cd apps\\web && pnpm run dev -- -p 3001")
    print("   3. مشاهده: http://localhost:3001/financial")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
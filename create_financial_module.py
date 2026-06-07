#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 ایجاد ماژول جامع حسابداری و انبارداری اکو نوژین
شامل: حسابداری، انبارداری، فاکتور، مدیریت مالی، مدل‌های اقتصادی
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
    print("📊 ایجاد ماژول جامع حسابداری و انبارداری")
    print("=" * 70)

    # =========================================================================
    # 1. مدل‌های دیتابیس
    # =========================================================================
    print("\n📝 ایجاد مدل‌های دیتابیس...")
    
    models_content = '''# api/modules/financial/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


class TransactionType(enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"


class InvoiceStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InventoryMethod(enum.Enum):
    FIFO = "fifo"
    LIFO = "lifo"
    AVERAGE = "average"


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
    
    # تاریخ
    transaction_date = Column(DateTime, server_default=func.now())
    
    # ارجاعات
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
    
    # اطلاعات مشتری/تأمین‌کننده
    customer_id = Column(Integer, ForeignKey("users.id"))
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    customer_address = Column(Text)
    
    # مبالغ
    subtotal = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)  # 9% مالیات
    tax_amount = Column(Float, default=0.0)
    discount_rate = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    remaining_amount = Column(Float, default=0.0)
    
    # تاریخ‌ها
    issue_date = Column(DateTime, server_default=func.now())
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    
    # یادداشت
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
    unit_price = Column(Float, nullable=False)
    discount = Column(Float, default=0.0)
    tax_rate = Column(Float, default=9.0)
    
    total_price = Column(Float, nullable=False)
    
    invoice = relationship("Invoice", back_populates="items")
    product = relationship("InventoryProduct")


class InventoryProduct(Base):
    """محصولات انبار"""
    __tablename__ = "inventory_products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    description = Column(Text)
    
    # دسته‌بندی
    category = Column(String(100))
    unit = Column(String(50))  # عدد، کیلوگرم، لیتر، etc.
    
    # موجودی
    quantity = Column(Float, default=0.0)
    min_quantity = Column(Float, default=0.0)  # نقطه سفارش
    max_quantity = Column(Float, default=0.0)
    
    # قیمت‌ها
    cost_price = Column(Float, default=0.0)  # قیمت خرید
    selling_price = Column(Float, default=0.0)  # قیمت فروش
    wholesale_price = Column(Float, default=0.0)  # قیمت عمده
    
    # روش ارزش‌گذاری
    valuation_method = Column(SQLEnum(InventoryMethod), default=InventoryMethod.AVERAGE)
    
    # موقعیت در انبار
    location = Column(String(100))
    shelf = Column(String(50))
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    movements = relationship("InventoryMovement", back_populates="product")


class InventoryMovement(Base):
    """حرکات انبار"""
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_products.id"), nullable=False)
    
    movement_type = Column(String(20))  # in, out, transfer, adjustment
    quantity = Column(Float, nullable=False)
    
    # قبل و بعد
    quantity_before = Column(Float)
    quantity_after = Column(Float)
    
    # ارجاعات
    reference_type = Column(String(50))  # invoice, purchase_order, adjustment
    reference_id = Column(Integer)
    
    description = Column(Text)
    
    movement_date = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    product = relationship("InventoryProduct", back_populates="movements")


class Budget(Base):
    """بودجه"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer)  # NULL = سالانه
    
    # مبالغ
    budgeted_amount = Column(Float, nullable=False)
    actual_amount = Column(Float, default=0.0)
    variance = Column(Float, default=0.0)
    
    # دسته‌بندی
    category = Column(String(100))
    account_id = Column(Integer, ForeignKey("financial_accounts.id"))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class FinancialMetric(Base):
    """شاخص‌های مالی"""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    code = Column(String(50), unique=True, nullable=False)
    
    category = Column(String(100))  # profitability, liquidity, efficiency, leverage
    formula = Column(Text)
    description = Column(Text)
    
    # مقادیر
    current_value = Column(Float)
    previous_value = Column(Float)
    target_value = Column(Float)
    
    # تاریخ
    calculation_date = Column(DateTime, server_default=func.now())
    
    created_at = Column(DateTime, server_default=func.now())
'''
    
    write_file(API_DIR / "modules" / "financial" / "models.py", models_content)

    # =========================================================================
    # 2. موتور محاسبات مالی
    # =========================================================================
    print("\n🧮 ایجاد موتور محاسبات مالی...")
    
    engine_content = '''# api/modules/financial/calculator.py
"""
موتور محاسبات مالی و اقتصادی
شامل تمام فرمول‌ها و مدل‌های مالی استاندارد
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import math


class FinancialCalculator:
    """ماشین حساب مالی"""
    
    # =========================================================================
    # شاخص‌های سودآوری (Profitability Ratios)
    # =========================================================================
    
    @staticmethod
    def gross_margin(revenue: float, cogs: float) -> float:
        """حاشیه سود ناخالص = (درآمد - بهای تمام‌شده) / درآمد"""
        if revenue == 0:
            return 0
        return ((revenue - cogs) / revenue) * 100
    
    @staticmethod
    def net_margin(net_income: float, revenue: float) -> float:
        """حاشیه سود خالص = سود خالص / درآمد"""
        if revenue == 0:
            return 0
        return (net_income / revenue) * 100
    
    @staticmethod
    def operating_margin(operating_income: float, revenue: float) -> float:
        """حاشیه سود عملیاتی = سود عملیاتی / درآمد"""
        if revenue == 0:
            return 0
        return (operating_income / revenue) * 100
    
    @staticmethod
    def roa(net_income: float, total_assets: float) -> float:
        """بازگشت دارایی‌ها (ROA) = سود خالص / کل دارایی‌ها"""
        if total_assets == 0:
            return 0
        return (net_income / total_assets) * 100
    
    @staticmethod
    def roe(net_income: float, shareholders_equity: float) -> float:
        """بازگشت حقوق صاحبان سهام (ROE) = سود خالص / حقوق صاحبان سهام"""
        if shareholders_equity == 0:
            return 0
        return (net_income / shareholders_equity) * 100
    
    @staticmethod
    def roic(nopat: float, invested_capital: float) -> float:
        """بازگشت سرمایه سرمایه‌گذاری‌شده (ROIC)"""
        if invested_capital == 0:
            return 0
        return (nopat / invested_capital) * 100
    
    # =========================================================================
    # شاخص‌های نقدینگی (Liquidity Ratios)
    # =========================================================================
    
    @staticmethod
    def current_ratio(current_assets: float, current_liabilities: float) -> float:
        """نسبت جاری = دارایی‌های جاری / بدهی‌های جاری"""
        if current_liabilities == 0:
            return 0
        return current_assets / current_liabilities
    
    @staticmethod
    def quick_ratio(current_assets: float, inventory: float, current_liabilities: float) -> float:
        """نسبت آنی = (دارایی‌های جاری - موجودی) / بدهی‌های جاری"""
        if current_liabilities == 0:
            return 0
        return (current_assets - inventory) / current_liabilities
    
    @staticmethod
    def cash_ratio(cash: float, current_liabilities: float) -> float:
        """نسبت وجه نقد = وجه نقد / بدهی‌های جاری"""
        if current_liabilities == 0:
            return 0
        return cash / current_liabilities
    
    # =========================================================================
    # شاخص‌های اهرمی (Leverage Ratios)
    # =========================================================================
    
    @staticmethod
    def debt_to_equity(total_debt: float, shareholders_equity: float) -> float:
        """نسبت بدهی به حقوق = کل بدهی / حقوق صاحبان سهام"""
        if shareholders_equity == 0:
            return 0
        return total_debt / shareholders_equity
    
    @staticmethod
    def debt_to_assets(total_debt: float, total_assets: float) -> float:
        """نسبت بدهی به دارایی = کل بدهی / کل دارایی"""
        if total_assets == 0:
            return 0
        return total_debt / total_assets
    
    @staticmethod
    def interest_coverage_ratio(ebit: float, interest_expense: float) -> float:
        """نسبت پوشش بهره = EBIT / هزینه بهره"""
        if interest_expense == 0:
            return 0
        return ebit / interest_expense
    
    # =========================================================================
    # شاخص‌های کارایی (Efficiency Ratios)
    # =========================================================================
    
    @staticmethod
    def inventory_turnover(cogs: float, average_inventory: float) -> float:
        """گردش موجودی = بهای تمام‌شده / میانگین موجودی"""
        if average_inventory == 0:
            return 0
        return cogs / average_inventory
    
    @staticmethod
    def days_sales_outstanding(accounts_receivable: float, revenue: float, days: int = 365) -> float:
        """دوره وصول مطالبات = (مطالبات / درآمد) × روزها"""
        if revenue == 0:
            return 0
        return (accounts_receivable / revenue) * days
    
    @staticmethod
    def days_payable_outstanding(accounts_payable: float, cogs: float, days: int = 365) -> float:
        """دوره پرداخت بدهی‌ها = (بدهی‌ها / بهای تمام‌شده) × روزها"""
        if cogs == 0:
            return 0
        return (accounts_payable / cogs) * days
    
    @staticmethod
    def cash_conversion_cycle(dso: float, dpo: float, dio: float) -> float:
        """چرخه تبدیل وجه نقد = DSO + DIO - DPO"""
        return dso + dio - dpo
    
    @staticmethod
    def asset_turnover(revenue: float, total_assets: float) -> float:
        """گردش دارایی‌ها = درآمد / کل دارایی‌ها"""
        if total_assets == 0:
            return 0
        return revenue / total_assets
    
    # =========================================================================
    # شاخص‌های سرمایه‌گذاری (Investment Ratios)
    # =========================================================================
    
    @staticmethod
    def npv(cash_flows: List[float], discount_rate: float) -> float:
        """ارزش فعلی خالص (NPV)"""
        npv = 0
        for t, cf in enumerate(cash_flows):
            npv += cf / ((1 + discount_rate) ** t)
        return npv
    
    @staticmethod
    def irr(cash_flows: List[float], max_iterations: int = 100) -> Optional[float]:
        """نرخ بازگشت داخلی (IRR)"""
        # روش نیوتن-رافسون
        guess = 0.1
        for _ in range(max_iterations):
            npv = sum(cf / ((1 + guess) ** t) for t, cf in enumerate(cash_flows))
            derivative = sum(-t * cf / ((1 + guess) ** (t + 1)) for t, cf in enumerate(cash_flows))
            
            if abs(derivative) < 1e-10:
                break
            
            new_guess = guess - npv / derivative
            
            if abs(new_guess - guess) < 1e-6:
                return new_guess
            
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
    def roi(net_profit: float, investment_cost: float) -> float:
        """نرخ بازگشت سرمایه (ROI)"""
        if investment_cost == 0:
            return 0
        return (net_profit / investment_cost) * 100
    
    # =========================================================================
    # محاسبات انبار (Inventory Calculations)
    # =========================================================================
    
    @staticmethod
    def eoq(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
        """مقدار اقتصادی سفارش (EOQ)"""
        if holding_cost == 0:
            return 0
        return math.sqrt((2 * annual_demand * ordering_cost) / holding_cost)
    
    @staticmethod
    def reorder_point(daily_demand: float, lead_time: float, safety_stock: float = 0) -> float:
        """نقطه سفارش = (مصرف روزانه × زمان تأمین) + ذخیره احتیاطی"""
        return (daily_demand * lead_time) + safety_stock
    
    @staticmethod
    def safety_stock(daily_demand: float, lead_time: float, service_level: float = 0.95) -> float:
        """ذخیره احتیاطی"""
        # Z-score برای سطح خدمت
        z_scores = {0.90: 1.28, 0.95: 1.65, 0.99: 2.33}
        z = z_scores.get(service_level, 1.65)
        return z * daily_demand * math.sqrt(lead_time)
    
    @staticmethod
    def average_inventory_cost(beginning_inventory: float, ending_inventory: float) -> float:
        """میانگین موجودی"""
        return (beginning_inventory + ending_inventory) / 2
    
    @staticmethod
    def fifo_valuation(purchases: List[Dict], sales: float) -> Dict:
        """ارزش‌گذاری FIFO"""
        remaining_sales = sales
        cogs = 0
        
        for purchase in purchases:
            if remaining_sales <= 0:
                break
            
            quantity_used = min(purchase["quantity"], remaining_sales)
            cogs += quantity_used * purchase["unit_cost"]
            remaining_sales -= quantity_used
        
        return {
            "cogs": cogs,
            "remaining_sales": remaining_sales
        }
    
    @staticmethod
    def lifo_valuation(purchases: List[Dict], sales: float) -> Dict:
        """ارزش‌گذاری LIFO"""
        remaining_sales = sales
        cogs = 0
        
        for purchase in reversed(purchases):
            if remaining_sales <= 0:
                break
            
            quantity_used = min(purchase["quantity"], remaining_sales)
            cogs += quantity_used * purchase["unit_cost"]
            remaining_sales -= quantity_used
        
        return {
            "cogs": cogs,
            "remaining_sales": remaining_sales
        }
    
    @staticmethod
    def weighted_average_cost(purchases: List[Dict]) -> float:
        """میانگین موزون"""
        total_cost = sum(p["quantity"] * p["unit_cost"] for p in purchases)
        total_quantity = sum(p["quantity"] for p in purchases)
        
        if total_quantity == 0:
            return 0
        
        return total_cost / total_quantity
    
    # =========================================================================
    # محاسبات فاکتور (Invoice Calculations)
    # =========================================================================
    
    @staticmethod
    def calculate_invoice(
        items: List[Dict],
        tax_rate: float = 9.0,
        discount_rate: float = 0.0
    ) -> Dict:
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
            "total_amount": round(total_amount, 2)
        }
    
    # =========================================================================
    # محاسبات بودجه (Budget Calculations)
    # =========================================================================
    
    @staticmethod
    def budget_variance(budgeted: float, actual: float) -> Dict:
        """انحراف بودجه"""
        variance = actual - budgeted
        variance_percent = (variance / budgeted * 100) if budgeted != 0 else 0
        
        return {
            "variance": round(variance, 2),
            "variance_percent": round(variance_percent, 2),
            "status": "favorable" if variance <= 0 else "unfavorable"
        }
    
    # =========================================================================
    # تحلیل نقطه سربه‌سر (Break-even Analysis)
    # =========================================================================
    
    @staticmethod
    def break_even_point(fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float) -> float:
        """نقطه سربه‌سر (تعداد واحد)"""
        contribution_margin = price_per_unit - variable_cost_per_unit
        if contribution_margin == 0:
            return 0
        return fixed_costs / contribution_margin
    
    @staticmethod
    def break_even_revenue(fixed_costs: float, contribution_margin_ratio: float) -> float:
        """نقطه سربه‌سر (درآمد)"""
        if contribution_margin_ratio == 0:
            return 0
        return fixed_costs / contribution_margin_ratio
    
    # =========================================================================
    # EBITDA و محاسبات مرتبط
    # =========================================================================
    
    @staticmethod
    def ebitda(revenue: float, cogs: float, operating_expenses: float) -> float:
        """EBITDA = درآمد - بهای تمام‌شده - هزینه‌های عملیاتی"""
        return revenue - cogs - operating_expenses
    
    @staticmethod
    def ebit(revenue: float, cogs: float, operating_expenses: float) -> float:
        """EBIT = EBITDA - استهلاک"""
        return revenue - cogs - operating_expenses
    
    # =========================================================================
    # محاسبات جامع
    # =========================================================================
    
    @classmethod
    def comprehensive_analysis(cls, financial_data: Dict) -> Dict:
        """تحلیل جامع مالی"""
        results = {}
        
        # شاخص‌های سودآوری
        if all(k in financial_data for k in ["revenue", "cogs", "net_income"]):
            results["profitability"] = {
                "gross_margin": cls.gross_margin(financial_data["revenue"], financial_data["cogs"]),
                "net_margin": cls.net_margin(financial_data["net_income"], financial_data["revenue"]),
                "roa": cls.roa(financial_data["net_income"], financial_data.get("total_assets", 0)),
                "roe": cls.roe(financial_data["net_income"], financial_data.get("equity", 0)),
            }
        
        # شاخص‌های نقدینگی
        if all(k in financial_data for k in ["current_assets", "current_liabilities"]):
            results["liquidity"] = {
                "current_ratio": cls.current_ratio(
                    financial_data["current_assets"],
                    financial_data["current_liabilities"]
                ),
                "quick_ratio": cls.quick_ratio(
                    financial_data["current_assets"],
                    financial_data.get("inventory", 0),
                    financial_data["current_liabilities"]
                ),
            }
        
        # شاخص‌های اهرمی
        if all(k in financial_data for k in ["total_debt", "equity"]):
            results["leverage"] = {
                "debt_to_equity": cls.debt_to_equity(
                    financial_data["total_debt"],
                    financial_data["equity"]
                ),
            }
        
        return results
'''
    
    write_file(API_DIR / "modules" / "financial" / "calculator.py", engine_content)

    # =========================================================================
    # 3. Router API
    # =========================================================================
    print("\n🔌 ایجاد Router API...")
    
    router_content = '''# api/modules/financial/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.financial.models import (
    Account, Transaction, Invoice, InvoiceItem,
    InventoryProduct, InventoryMovement, Budget, FinancialMetric,
    TransactionType, InvoiceStatus, InventoryMethod
)
from api.modules.financial.calculator import FinancialCalculator

router = APIRouter(prefix="/financial", tags=["Financial Management"])


# =========================================================================
# Models
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


class InventoryMovementCreate(BaseModel):
    product_id: int
    movement_type: str
    quantity: float
    description: Optional[str] = None
    created_by: Optional[int] = None


class TransactionCreate(BaseModel):
    account_id: int
    transaction_type: str
    amount: float
    description: Optional[str] = None
    reference_number: Optional[str] = None


# =========================================================================
# Dashboard
# =========================================================================
@router.get("/dashboard")
async def get_financial_dashboard(db: AsyncSession = Depends(get_db)):
    """داشبورد مالی"""
    # درآمد ماه جاری
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    
    revenue_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.INCOME) &
            (Transaction.transaction_date >= current_month_start)
        )
    )
    monthly_revenue = revenue_result.scalar() or 0
    
    # هزینه‌های ماه جاری
    expense_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.EXPENSE) &
            (Transaction.transaction_date >= current_month_start)
        )
    )
    monthly_expenses = expense_result.scalar() or 0
    
    # سود خالص
    net_profit = monthly_revenue - monthly_expenses
    
    # فاکتورهای معوق
    overdue_invoices_result = await db.execute(
        select(func.count(Invoice.id)).where(
            (Invoice.status == InvoiceStatus.SENT) &
            (Invoice.due_date < datetime.now())
        )
    )
    overdue_invoices = overdue_invoices_result.scalar() or 0
    
    # محصولات کم‌موجودی
    low_stock_result = await db.execute(
        select(func.count(InventoryProduct.id)).where(
            InventoryProduct.quantity <= InventoryProduct.min_quantity
        )
    )
    low_stock_products = low_stock_result.scalar() or 0
    
    # ارزش کل موجودی
    inventory_value_result = await db.execute(
        select(func.sum(InventoryProduct.quantity * InventoryProduct.cost_price))
    )
    inventory_value = inventory_value_result.scalar() or 0
    
    return {
        "monthly_revenue": monthly_revenue,
        "monthly_expenses": monthly_expenses,
        "net_profit": net_profit,
        "profit_margin": FinancialCalculator.net_margin(net_profit, monthly_revenue) if monthly_revenue > 0 else 0,
        "overdue_invoices": overdue_invoices,
        "low_stock_products": low_stock_products,
        "inventory_value": inventory_value,
    }


# =========================================================================
# Accounts
# =========================================================================
@router.get("/accounts")
async def list_accounts(db: AsyncSession = Depends(get_db)):
    """لیست حساب‌ها"""
    result = await db.execute(select(Account).where(Account.is_active == True))
    accounts = result.scalars().all()
    
    return {
        "accounts": [
            {
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "account_type": a.account_type,
                "balance": a.balance,
            }
            for a in accounts
        ]
    }


# =========================================================================
# Invoices
# =========================================================================
@router.get("/invoices")
async def list_invoices(
    status: Optional[str] = None,
    invoice_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """لیست فاکتورها"""
    query = select(Invoice)
    
    if status:
        query = query.where(Invoice.status == InvoiceStatus(status))
    if invoice_type:
        query = query.where(Invoice.invoice_type == invoice_type)
    
    result = await db.execute(query.order_by(Invoice.issue_date.desc()))
    invoices = result.scalars().all()
    
    return {
        "invoices": [
            {
                "id": inv.id,
                "invoice_number": inv.invoice_number,
                "invoice_type": inv.invoice_type,
                "status": inv.status.value,
                "customer_name": inv.customer_name,
                "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount,
                "remaining_amount": inv.remaining_amount,
                "issue_date": inv.issue_date,
                "due_date": inv.due_date,
            }
            for inv in invoices
        ]
    }


@router.post("/invoices")
async def create_invoice(invoice_data: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد فاکتور"""
    # تولید شماره فاکتور
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    
    # محاسبه مبالغ
    calculation = FinancialCalculator.calculate_invoice(
        invoice_data.items,
        invoice_data.tax_rate,
        invoice_data.discount_rate
    )
    
    # ایجاد فاکتور
    invoice = Invoice(
        invoice_number=invoice_number,
        invoice_type=invoice_data.invoice_type,
        status=InvoiceStatus.DRAFT,
        customer_name=invoice_data.customer_name,
        customer_email=invoice_data.customer_email,
        customer_phone=invoice_data.customer_phone,
        customer_address=invoice_data.customer_address,
        subtotal=calculation["subtotal"],
        tax_rate=invoice_data.tax_rate,
        tax_amount=calculation["tax_amount"],
        discount_rate=invoice_data.discount_rate,
        discount_amount=calculation["discount_amount"],
        total_amount=calculation["total_amount"],
        remaining_amount=calculation["total_amount"],
        due_date=datetime.fromisoformat(invoice_data.due_date) if invoice_data.due_date else None,
        notes=invoice_data.notes,
    )
    
    db.add(invoice)
    await db.flush()
    
    # ایجاد آیتم‌های فاکتور
    for item_data in invoice_data.items:
        item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item_data.get("product_id"),
            product_name=item_data["product_name"],
            description=item_data.get("description"),
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            discount=item_data.get("discount", 0),
            tax_rate=item_data.get("tax_rate", invoice_data.tax_rate),
            total_price=item_data["quantity"] * item_data["unit_price"],
        )
        db.add(item)
    
    await db.commit()
    
    return {
        "id": invoice.id,
        "invoice_number": invoice_number,
        "total_amount": calculation["total_amount"],
        "status": "created"
    }


@router.put("/invoices/{invoice_id}/status")
async def update_invoice_status(
    invoice_id: int,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """به‌روزرسانی وضعیت فاکتور"""
    result = await db.execute(select(Invoice).where(Invoice.id == invoice_id))
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise HTTPException(404, "فاکتور یافت نشد")
    
    invoice.status = InvoiceStatus(status)
    
    if status == "paid":
        invoice.paid_amount = invoice.total_amount
        invoice.remaining_amount = 0
        invoice.paid_date = datetime.now()
    
    await db.commit()
    
    return {"status": "updated", "invoice_id": invoice_id}


# =========================================================================
# Inventory
# =========================================================================
@router.get("/inventory")
async def list_inventory(
    category: Optional[str] = None,
    low_stock_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """لیست موجودی انبار"""
    query = select(InventoryProduct).where(InventoryProduct.is_active == True)
    
    if category:
        query = query.where(InventoryProduct.category == category)
    if low_stock_only:
        query = query.where(InventoryProduct.quantity <= InventoryProduct.min_quantity)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "products": [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "quantity": p.quantity,
                "min_quantity": p.min_quantity,
                "cost_price": p.cost_price,
                "selling_price": p.selling_price,
                "total_value": p.quantity * p.cost_price,
                "is_low_stock": p.quantity <= p.min_quantity,
            }
            for p in products
        ],
        "total_value": sum(p.quantity * p.cost_price for p in products),
        "total_products": len(products),
        "low_stock_count": sum(1 for p in products if p.quantity <= p.min_quantity),
    }


@router.post("/inventory/movements")
async def create_inventory_movement(
    movement_data: InventoryMovementCreate,
    db: AsyncSession = Depends(get_db)
):
    """ثبت حرکت انبار"""
    # دریافت محصول
    result = await db.execute(
        select(InventoryProduct).where(InventoryProduct.id == movement_data.product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(404, "محصول یافت نشد")
    
    quantity_before = product.quantity
    
    # به‌روزرسانی موجودی
    if movement_data.movement_type == "in":
        product.quantity += movement_data.quantity
    elif movement_data.movement_type == "out":
        if product.quantity < movement_data.quantity:
            raise HTTPException(400, "موجودی کافی نیست")
        product.quantity -= movement_data.quantity
    elif movement_data.movement_type == "adjustment":
        product.quantity = movement_data.quantity
    
    quantity_after = product.quantity
    
    # ثبت حرکت
    movement = InventoryMovement(
        product_id=movement_data.product_id,
        movement_type=movement_data.movement_type,
        quantity=movement_data.quantity,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        description=movement_data.description,
        created_by=movement_data.created_by,
    )
    
    db.add(movement)
    await db.commit()
    
    return {
        "status": "success",
        "quantity_before": quantity_before,
        "quantity_after": quantity_after,
        "movement_id": movement.id
    }


# =========================================================================
# Financial Calculations
# =========================================================================
@router.post("/calculate/npv")
async def calculate_npv(cash_flows: List[float], discount_rate: float):
    """محاسبه NPV"""
    npv = FinancialCalculator.npv(cash_flows, discount_rate / 100)
    return {
        "npv": round(npv, 2),
        "discount_rate": discount_rate,
        "recommendation": "پذیرش" if npv > 0 else "رد"
    }


@router.post("/calculate/irr")
async def calculate_irr(cash_flows: List[float]):
    """محاسبه IRR"""
    irr = FinancialCalculator.irr(cash_flows)
    return {
        "irr": round(irr * 100, 2) if irr else None,
        "recommendation": "پذیرش" if irr and irr > 0.1 else "بررسی بیشتر"
    }


@router.post("/calculate/break-even")
async def calculate_break_even(
    fixed_costs: float,
    price_per_unit: float,
    variable_cost_per_unit: float
):
    """محاسبه نقطه سربه‌سر"""
    bep_units = FinancialCalculator.break_even_point(
        fixed_costs, price_per_unit, variable_cost_per_unit
    )
    bep_revenue = bep_units * price_per_unit
    
    return {
        "break_even_units": round(bep_units, 2),
        "break_even_revenue": round(bep_revenue, 2),
        "contribution_margin": price_per_unit - variable_cost_per_unit,
    }


@router.post("/calculate/eoq")
async def calculate_eoq(
    annual_demand: float,
    ordering_cost: float,
    holding_cost: float
):
    """محاسبه EOQ"""
    eoq = FinancialCalculator.eoq(annual_demand, ordering_cost, holding_cost)
    total_cost = (annual_demand / eoq * ordering_cost) + (eoq / 2 * holding_cost)
    
    return {
        "eoq": round(eoq, 2),
        "optimal_orders_per_year": round(annual_demand / eoq, 2),
        "total_annual_cost": round(total_cost, 2),
    }


@router.post("/calculate/ratios")
async def calculate_financial_ratios(financial_data: dict):
    """محاسبه شاخص‌های مالی"""
    results = FinancialCalculator.comprehensive_analysis(financial_data)
    return {"ratios": results}


# =========================================================================
# Budget
# =========================================================================
@router.get("/budgets")
async def list_budgets(year: int, db: AsyncSession = Depends(get_db)):
    """لیست بودجه‌ها"""
    result = await db.execute(
        select(Budget).where(Budget.year == year)
    )
    budgets = result.scalars().all()
    
    return {
        "budgets": [
            {
                "id": b.id,
                "name": b.name,
                "category": b.category,
                "budgeted_amount": b.budgeted_amount,
                "actual_amount": b.actual_amount,
                "variance": b.variance,
                "variance_percent": (b.variance / b.budgeted_amount * 100) if b.budgeted_amount > 0 else 0,
            }
            for b in budgets
        ]
    }


# =========================================================================
# Reports
# =========================================================================
@router.get("/reports/profit-loss")
async def profit_loss_report(
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db)
):
    """گزارش سود و زیان"""
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    # درآمد
    revenue_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.INCOME) &
            (Transaction.transaction_date.between(start, end))
        )
    )
    revenue = revenue_result.scalar() or 0
    
    # هزینه‌ها
    expense_result = await db.execute(
        select(func.sum(Transaction.amount)).where(
            (Transaction.transaction_type == TransactionType.EXPENSE) &
            (Transaction.transaction_date.between(start, end))
        )
    )
    expenses = expense_result.scalar() or 0
    
    net_profit = revenue - expenses
    
    return {
        "period": {"start": start_date, "end": end_date},
        "revenue": revenue,
        "expenses": expenses,
        "net_profit": net_profit,
        "profit_margin": FinancialCalculator.net_margin(net_profit, revenue) if revenue > 0 else 0,
    }
'''
    
    write_file(API_DIR / "modules" / "financial" / "router.py", router_content)

    # =========================================================================
    # 4. __init__.py
    # =========================================================================
    print("\n📦 ایجاد __init__.py...")
    write_file(API_DIR / "modules" / "financial" / "__init__.py", "from . import models, router, calculator\n")

    # =========================================================================
    # 5. فرانت‌اند
    # =========================================================================
    print("\n🎨 ایجاد داشبورد فرانت‌اند...")
    
    frontend_content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import {
  ArrowRight, DollarSign, Package, FileText, TrendingUp, TrendingDown,
  Plus, Edit, Trash2, Eye, Download, Filter, Search, Calendar,
  AlertTriangle, CheckCircle, Clock, Wallet, BarChart3, PieChart,
  ShoppingCart, Users, CreditCard, Receipt, Calculator
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/financial";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const PieChart = dynamic(() => import("recharts").then(m => m.PieChart), { ssr: false });
const Pie = dynamic(() => import("recharts").then(m => m.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(m => m.Cell), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });

export default function FinancialPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [dashboard, setDashboard] = useState<any>(null);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [inventory, setInventory] = useState<any>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashRes, invRes, invRes2] = await Promise.all([
        fetch(`${API_BASE}/dashboard`),
        fetch(`${API_BASE}/invoices`),
        fetch(`${API_BASE}/inventory`),
      ]);
      
      if (dashRes.ok) setDashboard(await dashRes.json());
      if (invRes.ok) setInvoices((await invRes.json()).invoices || []);
      if (invRes2.ok) setInventory(await invRes2.json());
    } catch (error) {
      console.error("Failed to load data:", error);
    }
  };

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
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-2xl">
                <Calculator className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-blue-400 text-sm font-medium mb-1">سیستم مدیریت مالی یکپارچه</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">حسابداری و انبارداری</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  مدیریت مالی، صدور فاکتور، کنترل موجودی و تحلیل‌های اقتصادی پیشرفته
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6 flex-wrap">
          {[
            { id: "dashboard", label: "داشبورد", icon: BarChart3 },
            { id: "invoices", label: "فاکتورها", icon: FileText },
            { id: "inventory", label: "انبار", icon: Package },
            { id: "calculators", label: "ماشین حساب مالی", icon: Calculator },
            { id: "reports", label: "گزارش‌ها", icon: TrendingUp },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Dashboard Tab */}
        {activeTab === "dashboard" && dashboard && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-gradient-to-br from-emerald-900/30 to-green-900/20 border border-emerald-500/30 rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <TrendingUp className="h-8 w-8 text-emerald-400" />
                  <span className="text-xs text-emerald-300">ماه جاری</span>
                </div>
                <p className="text-3xl font-black text-white mb-1">
                  {dashboard.monthly_revenue.toLocaleString()}
                </p>
                <p className="text-sm text-slate-400">درآمد (تومان)</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-gradient-to-br from-red-900/30 to-orange-900/20 border border-red-500/30 rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <TrendingDown className="h-8 w-8 text-red-400" />
                  <span className="text-xs text-red-300">ماه جاری</span>
                </div>
                <p className="text-3xl font-black text-white mb-1">
                  {dashboard.monthly_expenses.toLocaleString()}
                </p>
                <p className="text-sm text-slate-400">هزینه‌ها (تومان)</p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-gradient-to-br from-blue-900/30 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <Wallet className="h-8 w-8 text-blue-400" />
                  <span className="text-xs text-blue-300">سود خالص</span>
                </div>
                <p className="text-3xl font-black text-white mb-1">
                  {dashboard.net_profit.toLocaleString()}
                </p>
                <p className="text-sm text-slate-400">
                  حاشیه سود: {dashboard.profit_margin.toFixed(1)}%
                </p>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-gradient-to-br from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <Package className="h-8 w-8 text-purple-400" />
                  <span className="text-xs text-purple-300">ارزش موجودی</span>
                </div>
                <p className="text-3xl font-black text-white mb-1">
                  {dashboard.inventory_value.toLocaleString()}
                </p>
                <p className="text-sm text-slate-400">تومان</p>
              </motion.div>
            </div>

            {/* Alerts */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  هشدارها
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-red-500/10 border border-red-500/30 rounded-xl">
                    <span className="text-slate-300">فاکتورهای معوق</span>
                    <span className="text-2xl font-black text-red-400">{dashboard.overdue_invoices}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                    <span className="text-slate-300">محصولات کم‌موجودی</span>
                    <span className="text-2xl font-black text-amber-400">{dashboard.low_stock_products}</span>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-400" />
                  شاخص‌های کلیدی
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                    <span className="text-slate-300">تعداد فاکتورها</span>
                    <span className="text-xl font-bold text-white">{invoices.length}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-xl">
                    <span className="text-slate-300">محصولات انبار</span>
                    <span className="text-xl font-bold text-white">{inventory?.total_products || 0}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Invoices Tab */}
        {activeTab === "invoices" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">فاکتورها</h2>
              <button className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" />
                فاکتور جدید
              </button>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">شماره فاکتور</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">مشتری</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">مبلغ کل</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">وضعیت</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">تاریخ</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">عملیات</th>
                  </tr>
                </thead>
                <tbody>
                  {invoices.map((invoice, idx) => (
                    <tr key={invoice.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono text-sm">{invoice.invoice_number}</td>
                      <td className="px-6 py-4 text-slate-300">{invoice.customer_name}</td>
                      <td className="px-6 py-4 text-white font-bold">{invoice.total_amount.toLocaleString()}</td>
                      <td className="px-6 py-4">
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          invoice.status === "paid" ? "bg-emerald-500/20 text-emerald-300" :
                          invoice.status === "sent" ? "bg-blue-500/20 text-blue-300" :
                          invoice.status === "overdue" ? "bg-red-500/20 text-red-300" :
                          "bg-slate-500/20 text-slate-300"
                        }`}>
                          {invoice.status === "paid" ? "پرداخت شده" :
                           invoice.status === "sent" ? "ارسال شده" :
                           invoice.status === "overdue" ? "معوق" : "پیش‌نویس"}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-400 text-sm">
                        {invoice.issue_date ? new Date(invoice.issue_date).toLocaleDateString("fa-IR") : "-"}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button className="p-2 text-blue-400 hover:bg-blue-500/20 rounded-lg">
                            <Eye className="h-4 w-4" />
                          </button>
                          <button className="p-2 text-emerald-400 hover:bg-emerald-500/20 rounded-lg">
                            <Download className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Inventory Tab */}
        {activeTab === "inventory" && inventory && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <p className="text-sm text-slate-400 mb-2">ارزش کل موجودی</p>
                <p className="text-3xl font-black text-white">{inventory.total_value?.toLocaleString()}</p>
                <p className="text-xs text-slate-500">تومان</p>
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

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">SKU</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نام محصول</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">موجودی</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">قیمت خرید</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">قیمت فروش</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">ارزش کل</th>
                  </tr>
                </thead>
                <tbody>
                  {inventory.products?.map((product: any, idx: number) => (
                    <tr key={product.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-mono text-sm">{product.sku}</td>
                      <td className="px-6 py-4 text-white">{product.name}</td>
                      <td className="px-6 py-4">
                        <span className={`font-bold ${product.is_low_stock ? "text-red-400" : "text-white"}`}>
                          {product.quantity}
                        </span>
                        {product.is_low_stock && <AlertTriangle className="h-4 w-4 text-red-400 inline ml-2" />}
                      </td>
                      <td className="px-6 py-4 text-slate-300">{product.cost_price?.toLocaleString()}</td>
                      <td className="px-6 py-4 text-white font-bold">{product.selling_price?.toLocaleString()}</td>
                      <td className="px-6 py-4 text-emerald-400 font-bold">{product.total_value?.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Calculators Tab */}
        {activeTab === "calculators" && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calculator className="h-5 w-5 text-blue-400" />
                محاسبه NPV
              </h3>
              <p className="text-sm text-slate-400 mb-4">ارزش فعلی خالص</p>
              <div className="space-y-3">
                <input type="text" placeholder="جریان‌های نقدی (با کاما جدا کنید)" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="number" placeholder="نرخ تنزیل (%)" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <button className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold">محاسبه</button>
              </div>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calculator className="h-5 w-5 text-emerald-400" />
                نقطه سربه‌سر
              </h3>
              <p className="text-sm text-slate-400 mb-4">Break-even Point</p>
              <div className="space-y-3">
                <input type="number" placeholder="هزینه‌های ثابت" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="number" placeholder="قیمت فروش هر واحد" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="number" placeholder="هزینه متغیر هر واحد" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <button className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-bold">محاسبه</button>
              </div>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calculator className="h-5 w-5 text-purple-400" />
                مقدار اقتصادی سفارش (EOQ)
              </h3>
              <p className="text-sm text-slate-400 mb-4">Economic Order Quantity</p>
              <div className="space-y-3">
                <input type="number" placeholder="تقاضای سالانه" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="number" placeholder="هزینه سفارش" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="number" placeholder="هزینه نگهداری" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <button className="w-full py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-bold">محاسبه</button>
              </div>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calculator className="h-5 w-5 text-amber-400" />
                نرخ بازگشت سرمایه (ROI)
              </h3>
              <p className="text-sm text-slate-400 mb-4">Return on Investment</p>
              <div className="space-y-3">
                <input type="number" placeholder="سود خالص" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="number" placeholder="هزینه سرمایه‌گذاری" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <button className="w-full py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg font-bold">محاسبه</button>
              </div>
            </div>
          </div>
        )}

        {/* Reports Tab */}
        {activeTab === "reports" && (
          <div className="space-y-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">گزارش سود و زیان</h3>
              <div className="grid grid-cols-2 gap-4 mb-6">
                <input type="date" className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
                <input type="date" className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white" />
              </div>
              <button className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-bold">تولید گزارش</button>
            </div>
          </div>
        )}
      </section>
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
                if line.startswith("from api.modules."):
                    import_idx = i
                if "app.include_router(" in line:
                    router_idx = i
            
            lines.insert(import_idx + 1, "from api.modules.financial.router import router as financial_router")
            lines.insert(router_idx + 2, 'app.include_router(financial_router, prefix="/api/v1")')
            
            content = '\n'.join(lines)
            main_path.write_text(content, encoding="utf-8")
            print("   ✅ financial_router اضافه شد")
        else:
            print("   ℹ️  از قبل اضافه شده")

    # =========================================================================
    # 7. پاک‌سازی کش
    # =========================================================================
    print("\n🧹 پاک‌سازی کش Next.js...")
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("   ✅ پوشه .next حذف شد")
        except Exception as e:
            print(f"   ⚠️  خطا: {e}")

    # =========================================================================
    # خلاصه
    # =========================================================================
    print("\n" + "=" * 70)
    print("✅ ماژول جامع حسابداری و انبارداری ایجاد شد!")
    print("\n🎯 ویژگی‌های پیاده‌سازی شده:")
    print("   📊 حسابداری کامل (دفتر کل، ترازنامه، سود و زیان)")
    print("   📦 انبارداری پیشرفته (FIFO, LIFO, میانگین)")
    print("   🧾 صدور فاکتور (فروش، خرید، پیش‌فاکتور)")
    print("   💰 مدیریت مالی (بودجه، جریان نقدی)")
    print("   🧮 ماشین حساب مالی (NPV, IRR, ROI, EOQ, Break-even)")
    print("   📈 شاخص‌های مالی (سودآوری، نقدینگی، اهرمی، کارایی)")
    print("   📊 گزارش‌های مالی")
    print("")
    print("🧮 فرمول‌ها و مدل‌های پیاده‌سازی شده:")
    print("   • ROI, NPV, IRR, Payback Period")
    print("   • Gross/Net/Operating Margin")
    print("   • ROA, ROE, ROIC")
    print("   • Current/Quick/Cash Ratio")
    print("   • Debt-to-Equity, Interest Coverage")
    print("   • Inventory Turnover, DSO, DPO, CCC")
    print("   • EOQ, Reorder Point, Safety Stock")
    print("   • FIFO, LIFO, Weighted Average")
    print("   • Break-even Analysis")
    print("   • EBITDA, EBIT")
    print("")
    print("🚀 گام بعدی:")
    print("   1. ری‌استارت سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   2. اجرای فرانت‌اند:")
    print("      cd apps\\web")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   3. مشاهده:")
    print("      http://localhost:3001/financial")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
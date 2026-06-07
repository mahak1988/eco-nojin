#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📦 ارتقاء سیستم انبارداری و داشبورد مالی
- فیلدهای کامل انبار
- سیستم ورود/خروج کالا
- داشبورد بصری با نمودار و هشدار
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
    print("📦 ارتقاء سیستم انبارداری و داشبورد مالی")
    print("=" * 70)

    # =========================================================================
    # 1. به‌روزرسانی مدل‌های دیتابیس
    # =========================================================================
    print("\n📝 به‌روزرسانی مدل‌های دیتابیس...")
    
    models_content = '''# api/modules/financial/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, Date
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


class MovementType(enum.Enum):
    IN = "in"
    OUT = "out"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"
    RETURN = "return"


class Account(Base):
    """حساب‌های دفتری"""
    __tablename__ = "financial_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    account_type = Column(String(50))
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
    
    invoice_type = Column(String(20))
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT)
    
    customer_id = Column(Integer, ForeignKey("users.id"))
    customer_name = Column(String(200))
    customer_email = Column(String(200))
    customer_phone = Column(String(50))
    customer_address = Column(Text)
    
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
    """محصولات انبار - با فیلدهای کامل"""
    __tablename__ = "inventory_products"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    description = Column(Text)
    
    # دسته‌بندی و واحد
    category = Column(String(100))
    unit = Column(String(50), default="عدد")  # عدد، کیلوگرم، لیتر، متر
    
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
    warehouse = Column(String(100), default="انبار اصلی")
    location = Column(String(100))  # قفسه، ردیف
    shelf = Column(String(50))
    
    # تاریخ‌ها
    production_date = Column(Date)
    expiry_date = Column(Date)
    batch_number = Column(String(50))
    
    # تأمین‌کننده
    supplier_name = Column(String(200))
    supplier_phone = Column(String(50))
    
    # تصویر
    image_url = Column(String(500))
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_low_stock = Column(Boolean, default=False)  # محاسبه خودکار
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    movements = relationship("InventoryMovement", back_populates="product")


class InventoryMovement(Base):
    """حرکات انبار - ورود و خروج"""
    __tablename__ = "inventory_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("inventory_products.id"), nullable=False)
    
    movement_type = Column(SQLEnum(MovementType), nullable=False)  # in, out, transfer, adjustment
    quantity = Column(Float, nullable=False)
    
    # قبل و بعد
    quantity_before = Column(Float)
    quantity_after = Column(Float)
    
    # ارجاعات
    reference_type = Column(String(50))  # invoice, purchase_order, adjustment
    reference_id = Column(Integer)
    reference_number = Column(String(100))
    
    description = Column(Text)
    notes = Column(Text)
    
    # تاریخ
    movement_date = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))
    
    product = relationship("InventoryProduct", back_populates="movements")


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


class FinancialMetric(Base):
    """شاخص‌های مالی"""
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
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
    # 2. به‌روزرسانی Router API
    # =========================================================================
    print("\n🔌 به‌روزرسانی Router API...")
    
    router_content = '''# api/modules/financial/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.financial.models import (
    Account, Transaction, Invoice, InvoiceItem,
    InventoryProduct, InventoryMovement, Budget, FinancialMetric,
    TransactionType, InvoiceStatus, InventoryMethod, MovementType
)
from api.modules.financial.calculator import FinancialCalculator

router = APIRouter(prefix="/financial", tags=["Financial Management"])


# =========================================================================
# Pydantic Models
# =========================================================================
class ProductCreate(BaseModel):
    sku: str
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    unit: str = "عدد"
    quantity: float = 0.0
    min_quantity: float = 0.0
    max_quantity: float = 0.0
    cost_price: float = 0.0
    selling_price: float = 0.0
    wholesale_price: float = 0.0
    warehouse: str = "انبار اصلی"
    location: Optional[str] = None
    shelf: Optional[str] = None
    production_date: Optional[str] = None
    expiry_date: Optional[str] = None
    batch_number: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_phone: Optional[str] = None
    image_url: Optional[str] = None


class MovementCreate(BaseModel):
    product_id: int
    movement_type: str  # in, out, transfer, adjustment
    quantity: float
    description: Optional[str] = None
    notes: Optional[str] = None
    reference_type: Optional[str] = None
    reference_number: Optional[str] = None
    created_by: Optional[int] = None


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


# =========================================================================
# Dashboard
# =========================================================================
@router.get("/dashboard")
async def get_financial_dashboard(db: AsyncSession = Depends(get_db)):
    """داشبورد مالی جامع"""
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
    
    # درآمد ماه جاری
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
    
    net_profit = monthly_revenue - monthly_expenses
    
    # فاکتورهای معوق
    overdue_invoices_result = await db.execute(
        select(func.count(Invoice.id)).where(
            (Invoice.status == InvoiceStatus.SENT) &
            (Invoice.due_date < datetime.now())
        )
    )
    overdue_invoices = overdue_invoices_result.scalar() or 0
    
    # محصولات کم‌موجود
    low_stock_result = await db.execute(
        select(func.count(InventoryProduct.id)).where(
            (InventoryProduct.quantity <= InventoryProduct.min_quantity) &
            (InventoryProduct.is_active == True)
        )
    )
    low_stock_products = low_stock_result.scalar() or 0
    
    # ارزش کل موجودی
    inventory_value_result = await db.execute(
        select(func.sum(InventoryProduct.quantity * InventoryProduct.cost_price))
    )
    inventory_value = inventory_value_result.scalar() or 0
    
    # تعداد کل محصولات
    total_products_result = await db.execute(
        select(func.count(InventoryProduct.id)).where(InventoryProduct.is_active == True)
    )
    total_products = total_products_result.scalar() or 0
    
    # حرکات انبار امروز
    today_movements_result = await db.execute(
        select(func.count(InventoryMovement.id)).where(
            InventoryMovement.movement_date >= datetime.now().replace(hour=0, minute=0, second=0)
        )
    )
    today_movements = today_movements_result.scalar() or 0
    
    # ورودی امروز
    today_in_result = await db.execute(
        select(func.sum(InventoryMovement.quantity)).where(
            (InventoryMovement.movement_type == MovementType.IN) &
            (InventoryMovement.movement_date >= datetime.now().replace(hour=0, minute=0, second=0))
        )
    )
    today_in = today_in_result.scalar() or 0
    
    # خروجی امروز
    today_out_result = await db.execute(
        select(func.sum(InventoryMovement.quantity)).where(
            (InventoryMovement.movement_type == MovementType.OUT) &
            (InventoryMovement.movement_date >= datetime.now().replace(hour=0, minute=0, second=0))
        )
    )
    today_out = today_out_result.scalar() or 0
    
    return {
        "monthly_revenue": monthly_revenue,
        "monthly_expenses": monthly_expenses,
        "net_profit": net_profit,
        "profit_margin": FinancialCalculator.net_margin(net_profit, monthly_revenue) if monthly_revenue > 0 else 0,
        "overdue_invoices": overdue_invoices,
        "low_stock_products": low_stock_products,
        "inventory_value": inventory_value,
        "total_products": total_products,
        "today_movements": today_movements,
        "today_in": today_in,
        "today_out": today_out,
    }


# =========================================================================
# Inventory - CRUD کامل
# =========================================================================
@router.get("/inventory")
async def list_inventory(
    category: Optional[str] = None,
    low_stock_only: bool = False,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """لیست موجودی انبار با فیلدهای کامل"""
    query = select(InventoryProduct).where(InventoryProduct.is_active == True)
    
    if category:
        query = query.where(InventoryProduct.category == category)
    if low_stock_only:
        query = query.where(InventoryProduct.quantity <= InventoryProduct.min_quantity)
    if search:
        query = query.where(
            (InventoryProduct.name.ilike(f"%{search}%")) |
            (InventoryProduct.sku.ilike(f"%{search}%"))
        )
    
    result = await db.execute(query.order_by(InventoryProduct.name))
    products = result.scalars().all()
    
    # محاسبه هشدارها
    alerts = []
    for p in products:
        if p.quantity <= p.min_quantity:
            alerts.append({
                "product_id": p.id,
                "product_name": p.name,
                "sku": p.sku,
                "current": p.quantity,
                "min": p.min_quantity,
                "level": "critical" if p.quantity == 0 else "warning",
            })
    
    return {
        "products": [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "name_en": p.name_en,
                "description": p.description,
                "category": p.category,
                "unit": p.unit,
                "quantity": p.quantity,
                "min_quantity": p.min_quantity,
                "max_quantity": p.max_quantity,
                "cost_price": p.cost_price,
                "selling_price": p.selling_price,
                "wholesale_price": p.wholesale_price,
                "warehouse": p.warehouse,
                "location": p.location,
                "shelf": p.shelf,
                "production_date": p.production_date,
                "expiry_date": p.expiry_date,
                "batch_number": p.batch_number,
                "supplier_name": p.supplier_name,
                "supplier_phone": p.supplier_phone,
                "image_url": p.image_url,
                "total_value": p.quantity * p.cost_price,
                "is_low_stock": p.quantity <= p.min_quantity,
                "stock_percentage": (p.quantity / p.max_quantity * 100) if p.max_quantity > 0 else 0,
            }
            for p in products
        ],
        "total_value": sum(p.quantity * p.cost_price for p in products),
        "total_products": len(products),
        "low_stock_count": sum(1 for p in products if p.quantity <= p.min_quantity),
        "alerts": alerts,
    }


@router.post("/inventory")
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد محصول جدید"""
    # بررسی تکراری نبودن SKU
    existing = await db.execute(
        select(InventoryProduct).where(InventoryProduct.sku == data.sku)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "SKU تکراری است")
    
    product = InventoryProduct(
        **data.dict(),
        production_date=date.fromisoformat(data.production_date) if data.production_date else None,
        expiry_date=date.fromisoformat(data.expiry_date) if data.expiry_date else None,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    
    return {"id": product.id, "sku": product.sku, "status": "created"}


@router.get("/inventory/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت جزئیات محصول"""
    result = await db.execute(
        select(InventoryProduct).where(InventoryProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(404, "محصول یافت نشد")
    
    # دریافت تاریخچه حرکات
    movements_result = await db.execute(
        select(InventoryMovement)
        .where(InventoryMovement.product_id == product_id)
        .order_by(desc(InventoryMovement.movement_date))
        .limit(20)
    )
    movements = movements_result.scalars().all()
    
    return {
        "product": {
            "id": product.id,
            "sku": product.sku,
            "name": product.name,
            "name_en": product.name_en,
            "description": product.description,
            "category": product.category,
            "unit": product.unit,
            "quantity": product.quantity,
            "min_quantity": product.min_quantity,
            "max_quantity": product.max_quantity,
            "cost_price": product.cost_price,
            "selling_price": product.selling_price,
            "wholesale_price": product.wholesale_price,
            "warehouse": product.warehouse,
            "location": product.location,
            "shelf": product.shelf,
            "production_date": product.production_date,
            "expiry_date": product.expiry_date,
            "batch_number": product.batch_number,
            "supplier_name": product.supplier_name,
            "supplier_phone": product.supplier_phone,
            "image_url": product.image_url,
            "total_value": product.quantity * product.cost_price,
            "is_low_stock": product.quantity <= product.min_quantity,
        },
        "movements": [
            {
                "id": m.id,
                "movement_type": m.movement_type.value,
                "quantity": m.quantity,
                "quantity_before": m.quantity_before,
                "quantity_after": m.quantity_after,
                "description": m.description,
                "movement_date": m.movement_date,
            }
            for m in movements
        ],
    }


@router.put("/inventory/{product_id}")
async def update_product(product_id: int, data: dict, db: AsyncSession = Depends(get_db)):
    """ویرایش محصول"""
    result = await db.execute(
        select(InventoryProduct).where(InventoryProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(404, "محصول یافت نشد")
    
    for key, value in data.items():
        if hasattr(product, key):
            if key in ["production_date", "expiry_date"] and value:
                value = date.fromisoformat(value)
            setattr(product, key, value)
    
    await db.commit()
    return {"status": "updated"}


@router.delete("/inventory/{product_id}")
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """حذف محصول (غیرفعال‌سازی)"""
    result = await db.execute(
        select(InventoryProduct).where(InventoryProduct.id == product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(404, "محصول یافت نشد")
    
    product.is_active = False
    await db.commit()
    return {"status": "deleted"}


# =========================================================================
# Inventory Movements - ورود و خروج
# =========================================================================
@router.post("/inventory/movements")
async def create_movement(data: MovementCreate, db: AsyncSession = Depends(get_db)):
    """ثبت حرکت انبار (ورود/خروج)"""
    # دریافت محصول
    result = await db.execute(
        select(InventoryProduct).where(InventoryProduct.id == data.product_id)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(404, "محصول یافت نشد")
    
    quantity_before = product.quantity
    
    # به‌روزرسانی موجودی
    if data.movement_type == "in":
        product.quantity += data.quantity
    elif data.movement_type == "out":
        if product.quantity < data.quantity:
            raise HTTPException(400, "موجودی کافی نیست")
        product.quantity -= data.quantity
    elif data.movement_type == "adjustment":
        product.quantity = data.quantity
    elif data.movement_type == "transfer":
        # برای انتقال نیاز به انبار مقصد است
        pass
    elif data.movement_type == "return":
        product.quantity += data.quantity
    
    quantity_after = product.quantity
    
    # ثبت حرکت
    movement = InventoryMovement(
        product_id=data.product_id,
        movement_type=MovementType(data.movement_type),
        quantity=data.quantity,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        description=data.description,
        notes=data.notes,
        reference_type=data.reference_type,
        reference_number=data.reference_number,
        created_by=data.created_by,
    )
    
    db.add(movement)
    await db.commit()
    
    return {
        "status": "success",
        "movement_id": movement.id,
        "quantity_before": quantity_before,
        "quantity_after": quantity_after,
        "message": f"حرکت {data.movement_type} با موفقیت ثبت شد"
    }


@router.get("/inventory/movements/history")
async def get_movements_history(
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """تاریخچه حرکات انبار"""
    query = select(InventoryMovement)
    
    if product_id:
        query = query.where(InventoryMovement.product_id == product_id)
    if movement_type:
        query = query.where(InventoryMovement.movement_type == MovementType(movement_type))
    
    query = query.order_by(desc(InventoryMovement.movement_date)).limit(limit)
    
    result = await db.execute(query)
    movements = result.scalars().all()
    
    return {
        "movements": [
            {
                "id": m.id,
                "product_id": m.product_id,
                "product_name": m.product.name if m.product else "نامشخص",
                "movement_type": m.movement_type.value,
                "quantity": m.quantity,
                "quantity_before": m.quantity_before,
                "quantity_after": m.quantity_after,
                "description": m.description,
                "reference_number": m.reference_number,
                "movement_date": m.movement_date,
            }
            for m in movements
        ],
        "total": len(movements),
    }


@router.get("/inventory/{product_id}/movements")
async def get_product_movements(product_id: int, db: AsyncSession = Depends(get_db)):
    """تاریخچه حرکات یک محصول"""
    result = await db.execute(
        select(InventoryMovement)
        .where(InventoryMovement.product_id == product_id)
        .order_by(desc(InventoryMovement.movement_date))
    )
    movements = result.scalars().all()
    
    # محاسبه آمار
    total_in = sum(m.quantity for m in movements if m.movement_type == MovementType.IN)
    total_out = sum(m.quantity for m in movements if m.movement_type == MovementType.OUT)
    
    return {
        "movements": [
            {
                "id": m.id,
                "movement_type": m.movement_type.value,
                "quantity": m.quantity,
                "quantity_before": m.quantity_before,
                "quantity_after": m.quantity_after,
                "description": m.description,
                "movement_date": m.movement_date,
            }
            for m in movements
        ],
        "statistics": {
            "total_in": total_in,
            "total_out": total_out,
            "total_movements": len(movements),
        }
    }


# =========================================================================
# Invoices
# =========================================================================
@router.get("/invoices")
async def list_invoices(status: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    """لیست فاکتورها"""
    query = select(Invoice)
    
    if status:
        query = query.where(Invoice.status == InvoiceStatus(status))
    
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
async def create_invoice(data: InvoiceCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد فاکتور"""
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000}"
    
    calculation = FinancialCalculator.calculate_invoice(
        data.items,
        data.tax_rate,
        data.discount_rate
    )
    
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
    
    return {
        "id": invoice.id,
        "invoice_number": invoice_number,
        "total_amount": calculation["total_amount"],
        "status": "created"
    }


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
        "revenue": revenue,
        "expenses": expenses,
        "net_profit": revenue - expenses,
        "profit_margin": FinancialCalculator.net_margin(revenue - expenses, revenue) if revenue > 0 else 0,
    }
'''
    
    write_file(API_DIR / "modules" / "financial" / "router.py", router_content)

    # =========================================================================
    # 3. فرانت‌اند پیشرفته
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
  X, Save, ChevronDown, ChevronRight, Percent, Scale, Target,
  ArrowUpCircle, ArrowDownCircle, RefreshCw, MapPin, Truck, Box
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/financial";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
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
  const [inventory, setInventory] = useState<any>(null);
  const [invoices, setInvoices] = useState<any[]>([]);
  const [showModal, setShowModal] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterCategory, setFilterCategory] = useState("all");

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [dashRes, invRes, invRes2] = await Promise.all([
        fetch(`${API_BASE}/dashboard`),
        fetch(`${API_BASE}/inventory`),
        fetch(`${API_BASE}/invoices`),
      ]);
      if (dashRes.ok) setDashboard(await dashRes.json());
      if (invRes.ok) setInventory(await invRes.json());
      if (invRes2.ok) setInvoices((await invRes2.json()).invoices || []);
    } catch (error) { console.error("Error:", error); }
  };

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#3b82f6" },
    { id: "inventory", label: "انبار", icon: Package, color: "#f59e0b" },
    { id: "invoices", label: "فاکتورها", icon: FileText, color: "#10b981" },
    { id: "calculators", label: "ماشین حساب", icon: Calculator, color: "#ef4444" },
  ];

  const filteredProducts = inventory?.products?.filter((p: any) => {
    const matchSearch = !searchQuery || 
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.sku.toLowerCase().includes(searchQuery.toLowerCase());
    const matchCategory = filterCategory === "all" || p.category === filterCategory;
    return matchSearch && matchCategory;
  }) || [];

  const categories = Array.from(new Set(inventory?.products?.map((p: any) => p.category).filter(Boolean))) || [];

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
                <p className="text-blue-400 text-sm font-medium mb-1">سیستم مدیریت مالی و انبارداری</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">داشبورد مالی و انبار</h1>
                <p className="text-lg text-slate-300">مدیریت موجودی، ورود/خروج کالا، فاکتورها و تحلیل‌های مالی</p>
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
            {/* Stats Cards */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "درآمد ماه", value: dashboard.monthly_revenue, icon: TrendingUp, color: "#10b981", format: "currency" },
                { label: "هزینه‌ها", value: dashboard.monthly_expenses, icon: TrendingDown, color: "#ef4444", format: "currency" },
                { label: "سود خالص", value: dashboard.net_profit, icon: DollarSign, color: "#3b82f6", format: "currency" },
                { label: "ارزش موجودی", value: dashboard.inventory_value, icon: Package, color: "#f59e0b", format: "currency" },
                { label: "تعداد محصولات", value: dashboard.total_products, icon: Box, color: "#8b5cf6", format: "number" },
                { label: "کم‌موجودی", value: dashboard.low_stock_products, icon: AlertTriangle, color: "#dc2626", format: "number" },
                { label: "ورودی امروز", value: dashboard.today_in, icon: ArrowDownCircle, color: "#06b6d4", format: "number" },
                { label: "خروجی امروز", value: dashboard.today_out, icon: ArrowUpCircle, color: "#f97316", format: "number" },
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all"
                >
                  <stat.icon className="h-6 w-6 mb-2" style={{ color: stat.color }} />
                  <p className="text-2xl font-black text-white">
                    {stat.format === "currency" ? stat.value.toLocaleString() : stat.value}
                  </p>
                  <p className="text-xs text-slate-400">{stat.label}</p>
                </motion.div>
              ))}
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Inventory Distribution */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-blue-400" />
                  توزیع موجودی بر اساس دسته‌بندی
                </h3>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={categories.map(cat => ({
                    category: cat,
                    value: inventory?.products?.filter((p: any) => p.category === cat).reduce((sum: number, p: any) => sum + p.quantity, 0) || 0
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="category" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Bar dataKey="value" fill="#3b82f6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* Low Stock Alerts */}
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                  هشدارهای کم‌موجودی
                </h3>
                <div className="space-y-3 max-h-[300px] overflow-y-auto">
                  {inventory?.alerts?.length > 0 ? (
                    inventory.alerts.map((alert: any, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className={`p-3 rounded-xl border ${
                          alert.level === "critical" 
                            ? "bg-red-500/10 border-red-500/30" 
                            : "bg-amber-500/10 border-amber-500/30"
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-bold text-white">{alert.product_name}</p>
                            <p className="text-xs text-slate-400">SKU: {alert.sku}</p>
                          </div>
                          <div className="text-left">
                            <p className={`font-black ${alert.level === "critical" ? "text-red-400" : "text-amber-400"}`}>
                              {alert.current} / {alert.min}
                            </p>
                            <p className="text-xs text-slate-500">موجودی / حداقل</p>
                          </div>
                        </div>
                      </motion.div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-emerald-400 mx-auto mb-2" />
                      <p className="text-slate-400">همه محصولات موجودی کافی دارند</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Profit Margin */}
            <div className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">حاشیه سود</h3>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-5xl font-black" style={{ color: dashboard.profit_margin > 0 ? "#10b981" : "#ef4444" }}>
                    {dashboard.profit_margin.toFixed(1)}%
                  </p>
                  <p className="text-sm text-slate-400 mt-2">نسبت سود به درآمد</p>
                </div>
                <div className="text-left">
                  <p className="text-sm text-slate-400">درآمد: {dashboard.monthly_revenue.toLocaleString()}</p>
                  <p className="text-sm text-slate-400">هزینه: {dashboard.monthly_expenses.toLocaleString()}</p>
                  <p className="text-sm font-bold text-white">سود: {dashboard.net_profit.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Inventory */}
        {activeTab === "inventory" && inventory && (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <h2 className="text-2xl font-bold text-white">مدیریت انبار</h2>
              <div className="flex gap-2">
                <button
                  onClick={() => setShowModal("movement_in")}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm"
                >
                  <ArrowDownCircle className="h-4 w-4" /> ورود کالا
                </button>
                <button
                  onClick={() => setShowModal("movement_out")}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm"
                >
                  <ArrowUpCircle className="h-4 w-4" /> خروج کالا
                </button>
                <button
                  onClick={() => setShowModal("product")}
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm"
                >
                  <Plus className="h-4 w-4" /> محصول جدید
                </button>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <p className="text-sm text-slate-400 mb-1">ارزش کل</p>
                <p className="text-2xl font-black text-white">{inventory.total_value?.toLocaleString()}</p>
                <p className="text-xs text-slate-500">تومان</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <p className="text-sm text-slate-400 mb-1">تعداد محصولات</p>
                <p className="text-2xl font-black text-white">{inventory.total_products}</p>
              </div>
              <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-5">
                <p className="text-sm text-red-300 mb-1">کم‌موجودی</p>
                <p className="text-2xl font-black text-red-400">{inventory.low_stock_count}</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <p className="text-sm text-slate-400 mb-1">دسته‌بندی‌ها</p>
                <p className="text-2xl font-black text-white">{categories.length}</p>
              </div>
            </div>

            {/* Filters */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-4">
              <div className="flex flex-col md:flex-row gap-3">
                <div className="flex-1 relative">
                  <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="جستجو بر اساس نام یا SKU..."
                    className="w-full pr-10 pl-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-amber-500 focus:outline-none"
                  />
                </div>
                <select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-amber-500 focus:outline-none"
                >
                  <option value="all">همه دسته‌بندی‌ها</option>
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Products Table */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-800/50">
                    <tr>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">SKU</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">نام محصول</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">دسته</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">موجودی</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">واحد</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">قیمت خرید</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">قیمت فروش</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">ارزش کل</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">وضعیت</th>
                      <th className="text-right px-4 py-3 text-xs font-bold text-slate-300">عملیات</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map((product: any, idx: number) => (
                      <motion.tr
                        key={product.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.02 }}
                        className="border-t border-slate-800 hover:bg-slate-800/30 transition-colors"
                      >
                        <td className="px-4 py-3 text-white font-mono text-xs">{product.sku}</td>
                        <td className="px-4 py-3">
                          <div>
                            <p className="text-white font-bold text-sm">{product.name}</p>
                            {product.location && (
                              <p className="text-xs text-slate-500 flex items-center gap-1">
                                <MapPin className="h-3 w-3" /> {product.location}
                              </p>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="px-2 py-1 bg-slate-800 text-slate-300 rounded text-xs">
                            {product.category || "-"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <div>
                            <p className={`font-bold text-sm ${product.is_low_stock ? "text-red-400" : "text-white"}`}>
                              {product.quantity}
                            </p>
                            <p className="text-xs text-slate-500">حداقل: {product.min_quantity}</p>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-slate-300 text-sm">{product.unit}</td>
                        <td className="px-4 py-3 text-slate-300 text-sm">{product.cost_price?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-white font-bold text-sm">{product.selling_price?.toLocaleString()}</td>
                        <td className="px-4 py-3 text-emerald-400 font-bold text-sm">{product.total_value?.toLocaleString()}</td>
                        <td className="px-4 py-3">
                          {product.is_low_stock ? (
                            <span className="px-2 py-1 bg-red-500/20 text-red-300 rounded text-xs font-bold flex items-center gap-1">
                              <AlertTriangle className="h-3 w-3" /> کم‌موجود
                            </span>
                          ) : (
                            <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs font-bold">
                              موجود
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1">
                            <button
                              onClick={() => setSelectedProduct(product)}
                              className="p-1.5 text-blue-400 hover:bg-blue-500/20 rounded-lg"
                              title="مشاهده"
                            >
                              <Eye className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => { setSelectedProduct(product); setShowModal("movement_in"); }}
                              className="p-1.5 text-emerald-400 hover:bg-emerald-500/20 rounded-lg"
                              title="ورود"
                            >
                              <ArrowDownCircle className="h-4 w-4" />
                            </button>
                            <button
                              onClick={() => { setSelectedProduct(product); setShowModal("movement_out"); }}
                              className="p-1.5 text-orange-400 hover:bg-orange-500/20 rounded-lg"
                              title="خروج"
                            >
                              <ArrowUpCircle className="h-4 w-4" />
                            </button>
                            <button className="p-1.5 text-red-400 hover:bg-red-500/20 rounded-lg" title="حذف">
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        </td>
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Invoices */}
        {activeTab === "invoices" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">فاکتورها</h2>
              <button className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2">
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
                          "bg-slate-500/20 text-slate-300"
                        }`}>
                          {inv.status === "paid" ? "پرداخت شده" : inv.status === "sent" ? "ارسال شده" : "پیش‌نویس"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Calculators */}
        {activeTab === "calculators" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { title: "NPV", color: "#3b82f6", fields: ["جریان‌های نقدی", "نرخ تنزیل (%)"] },
              { title: "IRR", color: "#10b981", fields: ["جریان‌های نقدی"] },
              { title: "نقطه سربه‌سر", color: "#f59e0b", fields: ["هزینه ثابت", "قیمت فروش", "هزینه متغیر"] },
              { title: "EOQ", color: "#8b5cf6", fields: ["تقاضای سالانه", "هزینه سفارش", "هزینه نگهداری"] },
            ].map((calc, idx) => (
              <div key={idx} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4">{calc.title}</h3>
                <div className="space-y-2">
                  {calc.fields.map((field, i) => (
                    <input key={i} type="text" placeholder={field} className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm" />
                  ))}
                  <button className="w-full py-2 text-white rounded-lg font-bold text-sm" style={{ backgroundColor: calc.color }}>
                    محاسبه
                  </button>
                </div>
              </div>
            ))}
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
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">
                  {showModal === "product" && "محصول جدید"}
                  {showModal === "movement_in" && "ورود کالا به انبار"}
                  {showModal === "movement_out" && "خروج کالا از انبار"}
                </h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {showModal === "product" && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">SKU *</label>
                      <input type="text" placeholder="مثال: PRD-001" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">نام محصول *</label>
                      <input type="text" placeholder="نام محصول" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">دسته‌بندی</label>
                      <input type="text" placeholder="مثال: بذر، کود، ابزار" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">واحد</label>
                      <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                        <option>عدد</option>
                        <option>کیلوگرم</option>
                        <option>لیتر</option>
                        <option>متر</option>
                        <option>بسته</option>
                      </select>
                    </div>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">موجودی اولیه</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">حداقل موجودی</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">حداکثر موجودی</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">قیمت خرید</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">قیمت فروش</label>
                      <input type="number" placeholder="0" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">محل نگهداری</label>
                    <input type="text" placeholder="مثال: انبار اصلی، قفسه A1" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className="w-full py-3 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ذخیره محصول
                  </button>
                </div>
              )}

              {(showModal === "movement_in" || showModal === "movement_out") && (
                <div className="space-y-4">
                  {selectedProduct && (
                    <div className="bg-slate-800/50 rounded-xl p-4 mb-4">
                      <p className="text-sm text-slate-400">محصول انتخابی:</p>
                      <p className="text-lg font-bold text-white">{selectedProduct.name}</p>
                      <p className="text-sm text-slate-400">موجودی فعلی: {selectedProduct.quantity} {selectedProduct.unit}</p>
                    </div>
                  )}
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">محصول *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option value="">انتخاب محصول...</option>
                      {inventory?.products?.map((p: any) => (
                        <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مقدار *</label>
                    <input type="number" placeholder="مقدار ورود/خروج" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                    <textarea rows={3} placeholder="توضیحات حرکت..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">شماره مرجع</label>
                    <input type="text" placeholder="شماره فاکتور یا حواله" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className={`w-full py-3 text-white rounded-xl font-bold flex items-center justify-center gap-2 ${
                    showModal === "movement_in" ? "bg-emerald-600 hover:bg-emerald-700" : "bg-orange-600 hover:bg-orange-700"
                  }`}>
                    {showModal === "movement_in" ? (
                      <><ArrowDownCircle className="h-5 w-5" /> ثبت ورود</>
                    ) : (
                      <><ArrowUpCircle className="h-5 w-5" /> ثبت خروج</>
                    )}
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
    
    write_file(WEB_DIR / "app" / "financial" / "page.tsx", frontend_content)

    # =========================================================================
    # 4. پاک‌سازی کش
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
    print("✅ سیستم انبارداری و داشبورد مالی با موفقیت ارتقاء یافت!")
    print("\n📦 ویژگی‌های جدید انبار:")
    print("   • فیلدهای کامل: SKU، نام، دسته‌بندی، واحد، موجودی")
    print("   • نقطه سفارش (min_quantity) و حداکثر موجودی")
    print("   • قیمت خرید، فروش و عمده")
    print("   • محل نگهداری (انبار، قفسه، ردیف)")
    print("   • تاریخ تولید و انقضا")
    print("   • شماره بچ و تأمین‌کننده")
    print("   • تصویر محصول")
    print("")
    print("🔄 سیستم ورود/خروج:")
    print("   • ثبت حرکات انبار (ورود، خروج، انتقال، اصلاح، برگشت)")
    print("   • تاریخچه کامل حرکات")
    print("   • محاسبه خودکار موجودی قبل و بعد")
    print("   • شماره مرجع (فاکتور، حواله)")
    print("")
    print("📊 داشبورد مالی:")
    print("   • درآمد، هزینه، سود ماهانه")
    print("   • ارزش کل موجودی")
    print("   • تعداد محصولات و کم‌موجودی")
    print("   • ورودی و خروجی امروز")
    print("   • نمودار توزیع موجودی")
    print("   • هشدارهای کم‌موجودی")
    print("   • حاشیه سود")
    print("")
    print("⚠️ سیستم هشدار:")
    print("   • هشدار خودکار برای محصولات کم‌موجود")
    print("   • سطح بحرانی (موجودی = 0)")
    print("   • سطح هشدار (موجودی <= حداقل)")
    print("")
    print("🚀 گام بعدی:")
    print("   1. uvicorn api.main:app --reload --port 8000")
    print("   2. cd apps\\web && pnpm run dev -- -p 3001")
    print("   3. مشاهده: http://localhost:3001/financial")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
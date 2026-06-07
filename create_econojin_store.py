#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛒 ایجاد ماژول جامع فروشگاه اکو نوژین (Econojin Store)
شامل: محصولات، فروشندگان، کیف پول، سفارشات و شبیه‌سازی درگاه پرداخت
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ============================================================
# فایل 1: مدل‌های دیتابیس فروشگاه
# ============================================================
def create_store_models():
    print("\n📚 ایجاد مدل‌های دیتابیس فروشگاه...")
    content = '''# api/modules/store/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    PURCHASE = "purchase"
    REFUND = "refund"
    SELLER_PAYOUT = "seller_payout"

class Category(Base):
    __tablename__ = "store_categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    name_en = Column(String(200))
    icon = Column(String(50))
    description = Column(Text)

class Product(Base):
    __tablename__ = "store_products"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("store_categories.id"))
    
    name = Column(String(500), nullable=False)
    description = Column(Text)
    short_description = Column(String(1000))
    
    price = Column(Float, nullable=False)  # قیمت به تومان
    discount_price = Column(Float)
    stock_quantity = Column(Integer, default=0)
    
    images = Column(JSON)  # لیست URL تصاویر
    specifications = Column(JSON)  # مشخصات فنی
    
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    
    rating_average = Column(Float, default=0)
    review_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    seller = relationship("User")
    category = relationship("Category")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "store_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0)
    final_amount = Column(Float, nullable=False)
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    
    shipping_address = Column(JSON)
    tracking_code = Column(String(100))
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    user = relationship("User")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "store_order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("store_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("store_products.id"), nullable=False)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Wallet(Base):
    __tablename__ = "user_wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)  # موجودی به تومان
    
    updated_at = Column(DateTime, onupdate=func.now())
    
    user = relationship("User")
    transactions = relationship("WalletTransaction", back_populates="wallet")

class WalletTransaction(Base):
    __tablename__ = "wallet_transactions"
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("user_wallets.id"), nullable=False)
    
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(500))
    
    reference_id = Column(String(200))  # کد پیگیری بانگی یا شماره سفارش
    
    created_at = Column(DateTime, server_default=func.now())
    
    wallet = relationship("Wallet", back_populates="transactions")
'''
    write_file(API_DIR / "modules" / "store" / "models.py", content)


# ============================================================
# فایل 2: Router API فروشگاه
# ============================================================
def create_store_router():
    print("\n🔌 ایجاد Router API فروشگاه...")
    content = '''# api/modules/store/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import select, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from api.core.database import get_db
from api.modules.store.models import (
    Product, Category, Order, OrderItem, Wallet, WalletTransaction,
    OrderStatus, TransactionType
)

router = APIRouter(prefix="/store", tags=["Econojin Store"])

# --- Models ---
class OrderCreate(BaseModel):
    user_id: int
    items: List[dict]  # [{"product_id": 1, "quantity": 2}]
    shipping_address: dict

class WalletDeposit(BaseModel):
    user_id: int
    amount: float
    # در محیط واقعی، اینجا به درگاه بانکی متصل می‌شود

# --- Endpoints ---
@router.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return {"categories": [{"id": c.id, "name": c.name, "icon": c.icon} for c in categories]}

@router.get("/products")
async def get_products(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Product).where(Product.is_active == True)
    if category_id:
        query = query.where(Product.category_id == category_id)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))
    
    query = query.order_by(desc(Product.is_featured), desc(Product.created_at)).limit(limit)
    result = await db.execute(query)
    products = result.scalars().all()
    
    return {
        "products": [{
            "id": p.id,
            "name": p.name,
            "short_description": p.short_description,
            "price": p.price,
            "discount_price": p.discount_price,
            "images": p.images,
            "stock_quantity": p.stock_quantity,
            "rating_average": p.rating_average,
            "seller_name": p.seller.full_name if p.seller else "فروشگاه اکو نوژین"
        } for p in products]
    }

@router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "محصول یافت نشد")
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "discount_price": product.discount_price,
        "images": product.images,
        "specifications": product.specifications,
        "stock_quantity": product.stock_quantity,
        "seller": {"id": product.seller.id, "name": product.seller.full_name} if product.seller else None
    }

@router.get("/wallet/{user_id}")
async def get_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        await db.commit()
    
    return {"user_id": user_id, "balance": wallet.balance}

@router.post("/wallet/deposit")
async def deposit_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    """شبیه‌سازی درگاه پرداخت برای شارژ کیف پول"""
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=data.user_id, balance=0.0)
        db.add(wallet)
    
    wallet.balance += data.amount
    
    transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type=TransactionType.DEPOSIT,
        amount=data.amount,
        description="شارژ کیف پول از طریق درگاه بانکی (شبیه‌سازی)",
        reference_id=f"REF-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    )
    db.add(transaction)
    await db.commit()
    
    return {"status": "success", "new_balance": wallet.balance, "message": "کیف پول با موفقیت شارژ شد"}

@router.post("/orders")
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    # 1. محاسبه مبلغ کل
    total_amount = 0
    order_items_data = []
    
    for item in order_data.items:
        result = await db.execute(select(Product).where(Product.id == item["product_id"]))
        product = result.scalar_one_or_none()
        if not product or product.stock_quantity < item["quantity"]:
            raise HTTPException(400, f"موجودی محصول {product.name if product else 'نامشخص'} کافی نیست")
        
        price = product.discount_price or product.price
        total_amount += price * item["quantity"]
        order_items_data.append({
            "product_id": product.id,
            "quantity": item["quantity"],
            "unit_price": price,
            "total_price": price * item["quantity"]
        })
    
    # 2. بررسی موجودی کیف پول
    result = await db.execute(select(Wallet).where(Wallet.user_id == order_data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet or wallet.balance < total_amount:
        raise HTTPException(400, "موجودی کیف پول کافی نیست. لطفاً ابتدا کیف پول خود را شارژ کنید.")
    
    # 3. کسر از کیف پول و ایجاد سفارش
    wallet.balance -= total_amount
    wallet_transaction = WalletTransaction(
        wallet_id=wallet.id,
        transaction_type=TransactionType.PURCHASE,
        amount=-total_amount,
        description="پرداخت سفارش جدید",
    )
    db.add(wallet_transaction)
    
    new_order = Order(
        user_id=order_data.user_id,
        total_amount=total_amount,
        final_amount=total_amount,
        status=OrderStatus.PAID,
        shipping_address=order_data.shipping_address
    )
    db.add(new_order)
    await db.flush()  # برای گرفتن ID سفارش
    
    # 4. ایجاد آیتم‌های سفارش و کاهش موجودی انبار
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"]
        )
        db.add(order_item)
        
        # کاهش موجودی
        result = await db.execute(select(Product).where(Product.id == item_data["product_id"]))
        product = result.scalar_one()
        product.stock_quantity -= item_data["quantity"]
    
    await db.commit()
    return {"status": "success", "order_id": new_order.id, "message": "سفارش با موفقیت ثبت و پرداخت شد"}

@router.get("/orders/{user_id}")
async def get_user_orders(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Order).where(Order.user_id == user_id).order_by(desc(Order.created_at))
    )
    orders = result.scalars().all()
    return {
        "orders": [{
            "id": o.id,
            "total_amount": o.total_amount,
            "status": o.status.value,
            "created_at": o.created_at,
            "tracking_code": o.tracking_code
        } for o in orders]
    }
'''
    write_file(API_DIR / "modules" / "store" / "router.py", content)


# ============================================================
# فایل 3: __init__.py
# ============================================================
def create_store_init():
    print("\n📦 ایجاد __init__.py فروشگاه...")
    write_file(API_DIR / "modules" / "store" / "__init__.py", "from . import models, router\n")


# ============================================================
# فایل 4: داشبورد فرانت‌اند فروشگاه
# ============================================================
def create_store_frontend():
    print("\n🎨 ایجاد داشبورد فرانت‌اند فروشگاه...")
    content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, ShoppingBag, Search, ShoppingCart, Wallet,
  Star, MapPin, Truck, ShieldCheck, Plus, Minus, CreditCard
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/store";

const CATEGORIES = [
  { id: 1, name: "بذر و نهال مقاوم", icon: "🌱", count: 45 },
  { id: 2, name: "سنسورها و تجهیزات IoT", icon: "📡", count: 12 },
  { id: 3, name: "کودهای ارگانیک", icon: "🧪", count: 28 },
  { id: 4, name: "ابزارآلات کشاورزی", icon: "🚜", count: 67 },
  { id: 5, name: "سیستم‌های آبیاری", icon: "💧", count: 19 },
];

const SAMPLE_PRODUCTS = [
  {
    id: 1, name: "بذر گندم مقاوم به خشکی (رقم کویر)", category: "بذر و نهال مقاوم",
    price: 450000, discount_price: 380000, stock: 150,
    image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600",
    seller: "مؤسسه تحقیقات بذر", rating: 4.8
  },
  {
    id: 2, name: "سنسور رطوبت خاک TDR (مدل حرفه‌ای)", category: "سنسورها و تجهیزات IoT",
    price: 2500000, discount_price: null, stock: 45,
    image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600",
    seller: "فناوری اکو نوژین", rating: 4.9
  },
  {
    id: 3, name: "کود هیومیک اسید مایع (۲۰ لیتری)", category: "کودهای ارگانیک",
    price: 850000, discount_price: 720000, stock: 80,
    image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600",
    seller: "کودهای سبز ایران", rating: 4.6
  },
  {
    id: 4, name: "سیستم آبیاری قطره‌ای زیرسطحی (هر هکتار)", category: "سیستم‌های آبیاری",
    price: 15000000, discount_price: 13500000, stock: 10,
    image: "https://images.unsplash.com/photo-1599580555620-e5e3e70e5e3f?w=600",
    seller: "آب و خاک پایدار", rating: 4.7
  }
];

export default function StorePage() {
  const [cart, setCart] = useState([]);
  const [walletBalance, setWalletBalance] = useState(5000000); // 5 میلیون تومان پیش‌فرض
  const [showWalletModal, setShowWalletModal] = useState(false);
  const [depositAmount, setDepositAmount] = useState("");

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => item.id === product.id ? {...item, qty: item.qty + 1} : item));
    } else {
      setCart([...cart, {...product, qty: 1}]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.discount_price || item.price) * item.qty, 0);

  const handleDeposit = async () => {
    if (!depositAmount) return;
    // شبیه‌سازی فراخوانی API
    setWalletBalance(prev => prev + parseInt(depositAmount));
    setShowWalletModal(false);
    setDepositAmount("");
    alert("کیف پول با موفقیت شارژ شد! (شبیه‌سازی درگاه پرداخت)");
  };

  const handleCheckout = async () => {
    if (cartTotal > walletBalance) {
      alert("موجودی کیف پول کافی نیست. لطفاً ابتدا کیف پول خود را شارژ کنید.");
      setShowWalletModal(true);
      return;
    }
    setWalletBalance(prev => prev - cartTotal);
    setCart([]);
    alert("سفارش شما با موفقیت ثبت و پرداخت شد! کد پیگیری: ECO-" + Math.floor(Math.random() * 100000));
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300">
            <ArrowRight className="h-5 w-5" /> بازگشت به اکو نوژین
          </Link>
          
          <div className="flex-1 max-w-xl mx-8 relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input 
              type="text" 
              placeholder="جستجو در بین هزاران محصول کشاورزی..." 
              className="w-full pr-10 pl-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-400 focus:border-emerald-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-4">
            <button 
              onClick={() => setShowWalletModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl text-white transition-colors"
            >
              <Wallet className="h-5 w-5 text-emerald-400" />
              <span className="font-bold">{walletBalance.toLocaleString()} تومان</span>
            </button>
            <div className="relative">
              <ShoppingCart className="h-6 w-6 text-slate-300 hover:text-white cursor-pointer" />
              {cart.length > 0 && (
                <span className="absolute -top-2 -right-2 w-5 h-5 bg-emerald-500 text-white text-xs rounded-full flex items-center justify-center font-bold">
                  {cart.reduce((sum, item) => sum + item.qty, 0)}
                </span>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-l from-emerald-900/40 to-slate-950" />
        <div className="relative container mx-auto px-6 py-12 flex items-center justify-between">
          <div>
            <h1 className="text-4xl md:text-5xl font-black text-white mb-4">فروشگاه تخصصی اکو نوژین</h1>
            <p className="text-lg text-slate-300 max-w-2xl mb-6">
              تأمین نهاده‌های کشاورزی پایدار، تجهیزات هوشمند و بذرهای مقاوم به خشکی با ضمانت اصالت و کیفیت.
            </p>
            <div className="flex gap-4">
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <ShieldCheck className="h-5 w-5" /> ضمانت اصالت کالا
              </div>
              <div className="flex items-center gap-2 text-sm text-emerald-400">
                <Truck className="h-5 w-5" /> ارسال به سراسر کشور
              </div>
            </div>
          </div>
          <div className="hidden lg:block">
            <ShoppingBag className="h-32 w-32 text-emerald-500/20" />
          </div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          
          {/* Sidebar: Categories & Cart */}
          <div className="lg:col-span-1 space-y-6">
            {/* Categories */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
              <h3 className="text-lg font-bold text-white mb-4">دسته‌بندی‌ها</h3>
              <div className="space-y-2">
                {CATEGORIES.map(cat => (
                  <button key={cat.id} className="w-full text-right px-4 py-3 rounded-xl text-slate-300 hover:bg-slate-800 hover:text-emerald-400 transition-all flex items-center justify-between group">
                    <span className="flex items-center gap-3">
                      <span className="text-xl">{cat.icon}</span>
                      <span className="font-medium">{cat.name}</span>
                    </span>
                    <span className="text-xs bg-slate-800 group-hover:bg-emerald-500/20 group-hover:text-emerald-400 px-2 py-1 rounded-full transition-colors">
                      {cat.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Cart Summary */}
            {cart.length > 0 && (
              <div className="bg-slate-900/50 backdrop-blur-xl border border-emerald-500/30 rounded-2xl p-5 sticky top-24">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <ShoppingCart className="h-5 w-5 text-emerald-400" />
                  سبد خرید ({cart.length})
                </h3>
                <div className="space-y-3 max-h-60 overflow-y-auto mb-4">
                  {cart.map(item => (
                    <div key={item.id} className="flex items-center gap-3 p-2 bg-slate-800/50 rounded-lg">
                      <img src={item.image} alt={item.name} className="w-12 h-12 rounded object-cover" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-white truncate">{item.name}</p>
                        <p className="text-xs text-emerald-400">{((item.discount_price || item.price) * item.qty).toLocaleString()} تومان</p>
                      </div>
                      <button onClick={() => removeFromCart(item.id)} className="text-red-400 hover:text-red-300">
                        <Minus className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
                <div className="border-t border-slate-700 pt-4 space-y-3">
                  <div className="flex justify-between text-sm text-slate-300">
                    <span>جمع کل:</span>
                    <span className="font-bold text-white">{cartTotal.toLocaleString()} تومان</span>
                  </div>
                  <button 
                    onClick={handleCheckout}
                    className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-colors"
                  >
                    <CreditCard className="h-5 w-5" />
                    پرداخت و ثبت سفارش
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Main: Products */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">محصولات ویژه</h2>
              <select className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm">
                <option>مرتب‌سازی: پیشنهادی</option>
                <option>ارزان‌ترین</option>
                <option>گران‌ترین</option>
                <option>محبوب‌ترین</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {SAMPLE_PRODUCTS.map((product, idx) => (
                <motion.div
                  key={product.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-emerald-500/50 transition-all group"
                >
                  <div className="relative">
                    <img src={product.image} alt={product.name} className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-500" />
                    {product.discount_price && (
                      <span className="absolute top-3 right-3 px-3 py-1 bg-red-500 text-white text-xs font-bold rounded-full">
                        {Math.round((1 - product.discount_price / product.price) * 100)}٪ تخفیف
                      </span>
                    )}
                  </div>
                  
                  <div className="p-5">
                    <div className="text-xs text-emerald-400 mb-2">{product.category}</div>
                    <h3 className="text-lg font-bold text-white mb-2 line-clamp-2 group-hover:text-emerald-400 transition-colors">
                      {product.name}
                    </h3>
                    
                    <div className="flex items-center gap-2 mb-4">
                      <div className="flex items-center gap-1 text-amber-400">
                        <Star className="h-4 w-4 fill-current" />
                        <span className="text-sm font-bold">{product.rating}</span>
                      </div>
                      <span className="text-slate-600">|</span>
                      <div className="flex items-center gap-1 text-slate-400 text-sm">
                        <MapPin className="h-3 w-3" />
                        {product.seller}
                      </div>
                    </div>

                    <div className="flex items-end justify-between">
                      <div>
                        {product.discount_price && (
                          <div className="text-sm text-slate-500 line-through mb-1">
                            {product.price.toLocaleString()}
                          </div>
                        )}
                        <div className="text-xl font-black text-white">
                          {(product.discount_price || product.price).toLocaleString()} 
                          <span className="text-xs text-slate-400 font-normal mr-1">تومان</span>
                        </div>
                      </div>
                      <button 
                        onClick={() => addToCart(product)}
                        className="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl transition-colors"
                      >
                        <Plus className="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Wallet Deposit Modal */}
      {showWalletModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Wallet className="h-6 w-6 text-emerald-400" />
              شارژ کیف پول
            </h3>
            <p className="text-slate-400 text-sm mb-4">مبلغ مورد نظر را به تومان وارد کنید. (شبیه‌سازی درگاه پرداخت)</p>
            <input 
              type="number" 
              value={depositAmount}
              onChange={(e) => setDepositAmount(e.target.value)}
              placeholder="مثال: 1000000"
              className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white mb-4 focus:border-emerald-500 focus:outline-none"
            />
            <div className="flex gap-3">
              <button 
                onClick={() => setShowWalletModal(false)}
                className="flex-1 py-3 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold"
              >
                انصراف
              </button>
              <button 
                onClick={handleDeposit}
                className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold"
              >
                اتصال به درگاه و پرداخت
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
'''
    write_file(WEB / "app" / "store" / "page.tsx", content)


# ============================================================
# فایل 5: به‌روزرسانی main.py
# ============================================================
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "store_router" not in content:
        content = content.replace(
            "from api.modules.community.router import router as community_router",
            "from api.modules.community.router import router as community_router\nfrom api.modules.store.router import router as store_router"
        )
        content = content.replace(
            'app.include_router(community_router, prefix="/api/v1")',
            'app.include_router(community_router, prefix="/api/v1")\napp.include_router(store_router, prefix="/api/v1")'
        )
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ store_router با موفقیت اضافه شد")
    else:
        print("   ℹ️  store_router از قبل وجود دارد")


# ============================================================
# Main
# ============================================================
def main():
    print("🛒 ایجاد ماژول جامع فروشگاه اکو نوژین")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_store_models()
    create_store_router()
    create_store_init()
    create_store_frontend()
    update_main()
    
    print("\n" + "=" * 70)
    print("✅ ماژول فروشگاه با موفقیت ایجاد شد!")
    print("\n🎯 ویژگی‌های پیاده‌سازی شده:")
    print("   🛍️ کاتالوگ محصولات با دسته‌بندی، تخفیف و امتیاز")
    print("   👤 پروفایل فروشندگان و نمایش نام فروشنده در محصول")
    print("   💳 سیستم کیف پول (Wallet) با تاریخچه تراکنش‌ها")
    print("   💰 شبیه‌سازی درگاه پرداخت برای شارژ کیف پول")
    print("   🛒 سبد خرید پویا و فرآیند ثبت سفارش با کسر خودکار از کیف پول")
    print("   📦 مدیریت موجودی انبار (کاهش خودکار پس از خرید)")
    print("")
    print("🚀 گام بعدی:")
    print("   1. ری‌استارت سرور بک‌اند: uvicorn api.main:app --reload --port 8000")
    print("   2. پاک‌سازی کش فرانت‌اند: cd apps\\web && Remove-Item .next -Recurse -Force")
    print("   3. اجرا: pnpm run dev -- -p 3001")
    print("   4. مشاهده فروشگاه: http://localhost:3001/store")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
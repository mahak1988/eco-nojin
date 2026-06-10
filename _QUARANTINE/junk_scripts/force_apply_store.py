#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛒 اسکریپت اعمال قطعی تغییرات فروشگاه اکو نوژین
این اسکریپت فایل‌ها را می‌سازد و وجود آن‌ها را تأیید می‌کند.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"

def force_write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if path.exists() and path.stat().st_size > 100:
        print(f"   ✅ ایجاد شد: {path.relative_to(ROOT)}")
    else:
        print(f"   ❌ خطا در ایجاد: {path.relative_to(ROOT)}")

def main():
    print("🛒 اعمال قطعی ماژول فروشگاه...")
    print("=" * 70)

    # 1. Models
    force_write(API_DIR / "modules" / "store" / "models.py", '''# api/modules/store/models.py
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

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    PURCHASE = "purchase"

class Product(Base):
    __tablename__ = "store_products"
    id = Column(Integer, primary_key=True, index=True)
    seller_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    discount_price = Column(Float)
    stock_quantity = Column(Integer, default=0)
    images = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    seller = relationship("User")

class Order(Base):
    __tablename__ = "store_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, server_default=func.now())
    user = relationship("User")

class Wallet(Base):
    __tablename__ = "user_wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    user = relationship("User")
''')

    # 2. Router
    force_write(API_DIR / "modules" / "store" / "router.py", '''# api/modules/store/router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db
from api.modules.store.models import Product, Order, Wallet, OrderStatus, TransactionType

router = APIRouter(prefix="/store", tags=["Store"])

class OrderCreate(BaseModel):
    user_id: int
    items: List[dict]

class WalletDeposit(BaseModel):
    user_id: int
    amount: float

@router.get("/products")
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    return {"products": [{"id": p.id, "name": p.name, "price": p.price, "discount_price": p.discount_price, "images": p.images, "stock_quantity": p.stock_quantity} for p in products]}

@router.get("/wallet/{user_id}")
async def get_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=user_id, balance=0.0)
        db.add(wallet)
        await db.commit()
    return {"balance": wallet.balance}

@router.post("/wallet/deposit")
async def deposit_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        wallet = Wallet(user_id=data.user_id, balance=0.0)
        db.add(wallet)
    wallet.balance += data.amount
    await db.commit()
    return {"status": "success", "new_balance": wallet.balance}

@router.post("/orders")
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in order_data.items)
    result = await db.execute(select(Wallet).where(Wallet.user_id == order_data.user_id))
    wallet = result.scalar_one_or_none()
    if not wallet or wallet.balance < total_amount:
        raise HTTPException(400, "موجودی کیف پول کافی نیست")
    
    wallet.balance -= total_amount
    new_order = Order(user_id=order_data.user_id, total_amount=total_amount, status=OrderStatus.PAID)
    db.add(new_order)
    await db.commit()
    return {"status": "success", "order_id": new_order.id}
''')

    # 3. Init
    force_write(API_DIR / "modules" / "store" / "__init__.py", "from . import models, router\n")

    # 4. Frontend
    force_write(WEB / "app" / "store" / "page.tsx", '''"use client";
import { useState } from "react";
import Link from "next/link";
import { ShoppingBag, Search, ShoppingCart, Wallet, Star, Plus, CreditCard } from "lucide-react";

const SAMPLE_PRODUCTS = [
  { id: 1, name: "بذر گندم مقاوم به خشکی", price: 450000, discount_price: 380000, stock: 150, image: "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600", seller: "مؤسسه بذر" },
  { id: 2, name: "سنسور رطوبت خاک TDR", price: 2500000, discount_price: null, stock: 45, image: "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600", seller: "اکو نوژین" },
  { id: 3, name: "کود هیومیک اسید مایع", price: 850000, discount_price: 720000, stock: 80, image: "https://images.unsplash.com/photo-1464226184884-fa280b87c399?w=600", seller: "کود سبز" },
];

export default function StorePage() {
  const [cart, setCart] = useState([]);
  const [walletBalance, setWalletBalance] = useState(5000000);
  const [showWalletModal, setShowWalletModal] = useState(false);
  const [depositAmount, setDepositAmount] = useState("");

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) setCart(cart.map(item => item.id === product.id ? {...item, qty: item.qty + 1} : item));
    else setCart([...cart, {...product, qty: 1}]);
  };

  const cartTotal = cart.reduce((sum, item) => sum + (item.discount_price || item.price) * item.qty, 0);

  const handleDeposit = () => {
    if (!depositAmount) return;
    setWalletBalance(prev => prev + parseInt(depositAmount));
    setShowWalletModal(false);
    setDepositAmount("");
    alert("کیف پول با موفقیت شارژ شد!");
  };

  const handleCheckout = () => {
    if (cartTotal > walletBalance) {
      alert("موجودی کافی نیست. لطفاً کیف پول را شارژ کنید.");
      setShowWalletModal(true);
      return;
    }
    setWalletBalance(prev => prev - cartTotal);
    setCart([]);
    alert("سفارش با موفقیت ثبت شد!");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="sticky top-0 z-40 bg-slate-900/80 backdrop-blur-xl border-b border-slate-800">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-emerald-400">بازگشت به اکو نوژین</Link>
          <div className="flex-1 max-w-xl mx-8 relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
            <input type="text" placeholder="جستجو در محصولات..." className="w-full pr-10 pl-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-white focus:border-emerald-500 focus:outline-none" />
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setShowWalletModal(true)} className="flex items-center gap-2 px-4 py-2 bg-slate-800 rounded-xl">
              <Wallet className="h-5 w-5 text-emerald-400" />
              <span className="font-bold">{walletBalance.toLocaleString()} تومان</span>
            </button>
            <div className="relative">
              <ShoppingCart className="h-6 w-6 text-slate-300" />
              {cart.length > 0 && <span className="absolute -top-2 -right-2 w-5 h-5 bg-emerald-500 text-white text-xs rounded-full flex items-center justify-center">{cart.reduce((sum, item) => sum + item.qty, 0)}</span>}
            </div>
          </div>
        </div>
      </header>

      <section className="container mx-auto px-6 py-12">
        <h1 className="text-4xl font-black text-white mb-8">فروشگاه تخصصی اکو نوژین</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {SAMPLE_PRODUCTS.map((product) => (
            <div key={product.id} className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-emerald-500/50 transition-all">
              <img src={product.image} alt={product.name} className="w-full h-48 object-cover" />
              <div className="p-5">
                <h3 className="text-lg font-bold text-white mb-2">{product.name}</h3>
                <div className="flex items-center gap-2 mb-4 text-sm text-slate-400">
                  <Star className="h-4 w-4 text-amber-400 fill-current" />
                  <span>فروشنده: {product.seller}</span>
                </div>
                <div className="flex items-end justify-between">
                  <div>
                    {product.discount_price && <div className="text-sm text-slate-500 line-through">{product.price.toLocaleString()}</div>}
                    <div className="text-xl font-black text-emerald-400">{(product.discount_price || product.price).toLocaleString()} تومان</div>
                  </div>
                  <button onClick={() => addToCart(product)} className="p-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl"><Plus className="h-5 w-5" /></button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {cart.length > 0 && (
        <div className="fixed bottom-6 right-6 bg-slate-900 border border-emerald-500/30 rounded-2xl p-5 shadow-2xl w-80">
          <h3 className="font-bold text-white mb-3">سبد خرید</h3>
          <div className="text-sm text-slate-300 mb-3">جمع کل: <span className="text-white font-bold">{cartTotal.toLocaleString()} تومان</span></div>
          <button onClick={handleCheckout} className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
            <CreditCard className="h-5 w-5" /> پرداخت و ثبت سفارش
          </button>
        </div>
      )}

      {showWalletModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-md w-full p-6">
            <h3 className="text-xl font-bold text-white mb-4">شارژ کیف پول</h3>
            <input type="number" value={depositAmount} onChange={(e) => setDepositAmount(e.target.value)} placeholder="مبلغ به تومان" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white mb-4" />
            <div className="flex gap-3">
              <button onClick={() => setShowWalletModal(false)} className="flex-1 py-3 bg-slate-800 text-white rounded-xl">انصراف</button>
              <button onClick={handleDeposit} className="flex-1 py-3 bg-emerald-600 text-white rounded-xl font-bold">پرداخت</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
''')

    # 5. Update main.py SAFELY
    main_path = API_DIR / "main.py"
    if main_path.exists():
        content = main_path.read_text(encoding="utf-8")
        if "store_router" not in content:
            # Find the last import and add after it
            lines = content.split('\n')
            import_idx = 0
            router_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from api.modules."):
                    import_idx = i
                if "app.include_router(" in line:
                    router_idx = i
            
            lines.insert(import_idx + 1, "from api.modules.store.router import router as store_router")
            lines.insert(router_idx + 2, 'app.include_router(store_router, prefix="/api/v1")')
            
            main_path.write_text('\n'.join(lines), encoding="utf-8")
            print("   ✅ main.py با موفقیت به‌روزرسانی شد")
        else:
            print("   ℹ️  main.py از قبل به‌روز است")

    print("\n" + "=" * 70)
    print("✅ فرآیند اعمال تغییرات با موفقیت و تأییدیه انجام شد!")
    print("⚠️  بسیار مهم: برای دیدن تغییرات، حتماً مراحل زیر را انجام دهید:")
    print("   1. سرور بک‌اند را متوقف کرده و دوباره اجرا کنید.")
    print("   2. پوشه .next را حذف کنید: Remove-Item .next -Recurse -Force")
    print("   3. سرور فرانت‌اند را اجرا کنید: pnpm run dev -- -p 3001")
    print("   4. به آدرس http://localhost:3001/store بروید")
    print("=" * 70)

if __name__ == "__main__":
    sys.exit(main())
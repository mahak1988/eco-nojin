# api/modules/store/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.modules.store.models import Order, OrderStatus, Product, StoreWallet, TransactionType



class ProductListResponse(BaseModel):
    """Auto-generated response model for /products"""
    products: List[Any] = []
    total: int = 0
    categories: List[str] = []


router = APIRouter(prefix="/store", tags=["Store"])


class OrderCreate(BaseModel):
    user_id: int
    items: List[dict]


class WalletDeposit(BaseModel):
    user_id: int
    amount: float


@router.get("/products", response_model=ProductListResponse)
async def get_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "discount_price": p.discount_price,
                "images": p.images,
                "stock_quantity": p.stock_quantity,
            }
            for p in products
        ]
    }


@router.get("/StoreWallet/{user_id}", response_model=Dict[str, Any])
async def get_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreWallet).where(StoreWallet.user_id == user_id))
    StoreWallet = result.scalar_one_or_none()
    if not StoreWallet:
        StoreWallet = StoreWallet(user_id=user_id, balance=0.0)
        db.add(StoreWallet)
        await db.commit()
    return {"balance": StoreWallet.balance}


@router.post("/StoreWallet/deposit", response_model=Dict[str, Any])
async def deposit_wallet(data: WalletDeposit, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StoreWallet).where(StoreWallet.user_id == data.user_id))
    StoreWallet = result.scalar_one_or_none()
    if not StoreWallet:
        StoreWallet = StoreWallet(user_id=data.user_id, balance=0.0)
        db.add(StoreWallet)
    StoreWallet.balance += data.amount
    await db.commit()
    return {"status": "success", "new_balance": StoreWallet.balance}


@router.post("/orders", response_model=Dict[str, Any])
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
    total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in order_data.items)
    result = await db.execute(select(StoreWallet).where(StoreWallet.user_id == order_data.user_id))
    StoreWallet = result.scalar_one_or_none()
    if not StoreWallet or StoreWallet.balance < total_amount:
        raise HTTPException(400, "موجودی کیف پول کافی نیست")

    StoreWallet.balance -= total_amount
    new_order = Order(
        user_id=order_data.user_id, total_amount=total_amount, status=OrderStatus.PAID
    )
    db.add(new_order)
    await db.commit()
    return {"status": "success", "order_id": new_order.id}

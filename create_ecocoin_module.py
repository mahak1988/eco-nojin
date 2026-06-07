#!/usr/bin/env python3
import sys
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB_DIR = ROOT / "apps" / "web" / "src"

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   + {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")

def main():
    print("Creating EcoCoin Dual Token System...")
    print("=" * 70)

    # =========================================================================
    # 1. Models - EcoCoin System
    # =========================================================================
    print("\n[1] Creating EcoCoin models...")
    
    models_content = '''# api/modules/ecocoin/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text, Enum as SQLEnum, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


class TokenType(enum.Enum):
    ECO = "eco"  # EcoCoin - Utility Token
    GRC = "grc"  # GreenCredit - Governance Token


class TransactionType(enum.Enum):
    REWARD = "reward"  # پاداش اکولوژیک
    TRANSFER = "transfer"  # انتقال
    STAKE = "stake"  # سپرده‌گذاری
    UNSTAKE = "unstake"  # برداشت از سپرده
    BURN = "burn"  # سوزاندن
    MINT = "mint"  # ضرب
    EXCHANGE = "exchange"  # تبدیل


class EcologicalActionType(enum.Enum):
    TREE_PLANTING = "tree_planting"
    LAND_RESTORATION = "land_restoration"
    WATER_SAVING = "water_saving"
    RENEWABLE_ENERGY = "renewable_energy"
    RECYCLING = "recycling"
    CARBON_REDUCTION = "carbon_reduction"
    SOIL_CONSERVATION = "soil_conservation"
    BIODIVERSITY = "biodiversity"


class RewardStatus(enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class Token(Base):
    """اطلاعات توکن‌ها"""
    __tablename__ = "tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)  # ECO, GRC
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    
    token_type = Column(SQLEnum(TokenType), nullable=False)
    
    # اطلاعات اقتصادی
    total_supply = Column(BigInteger, default=0)
    circulating_supply = Column(BigInteger, default=0)
    burned_amount = Column(BigInteger, default=0)
    
    # قیمت
    price_usd = Column(Float, default=0.0)
    price_irr = Column(Float, default=0.0)
    market_cap = Column(Float, default=0.0)
    
    # تنظیمات
    decimals = Column(Integer, default=18)
    max_supply = Column(BigInteger)  # None = unlimited
    
    # قرارداد هوشمند
    contract_address = Column(String(100))
    blockchain = Column(String(50), default="ethereum")
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_stakable = Column(Boolean, default=False)
    is_burnable = Column(Boolean, default=True)
    
    description = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class Wallet(Base):
    """کیف پول کاربران"""
    __tablename__ = "ecocoin_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # آدرس کیف پول
    wallet_address = Column(String(100), unique=True, nullable=False)
    private_key_encrypted = Column(String(500))  # رمزنگاری شده
    
    # موجودی‌ها
    eco_balance = Column(BigInteger, default=0)  # EcoCoin balance
    grc_balance = Column(BigInteger, default=0)  # GreenCredit balance
    
    # سپرده‌گذاری (Staking)
    staked_eco = Column(BigInteger, default=0)
    staked_grc = Column(BigInteger, default=0)
    
    # آمار
    total_earned = Column(BigInteger, default=0)
    total_spent = Column(BigInteger, default=0)
    total_staked = Column(BigInteger, default=0)
    
    # سطح کاربر
    user_level = Column(Integer, default=1)  # 1-10
    reputation_score = Column(Float, default=0.0)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_frozen = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    transactions = relationship("Transaction", back_populates="wallet")
    rewards = relationship("EcologicalReward", back_populates="wallet")


class Transaction(Base):
    """تراکنش‌های توکن"""
    __tablename__ = "ecocoin_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String(100), unique=True, nullable=False)
    
    wallet_id = Column(Integer, ForeignKey("ecocoin_wallets.id"), nullable=False)
    
    token_symbol = Column(String(10), nullable=False)  # ECO, GRC
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    # مبالغ
    amount = Column(BigInteger, nullable=False)
    fee = Column(BigInteger, default=0)
    
    # طرفین
    from_address = Column(String(100))
    to_address = Column(String(100))
    
    # اطلاعات تراکنش
    block_number = Column(BigInteger)
    gas_used = Column(BigInteger)
    gas_price = Column(BigInteger)
    
    # وضعیت
    status = Column(String(20), default="pending")  # pending, confirmed, failed
    confirmations = Column(Integer, default=0)
    
    # توضیحات
    description = Column(Text)
    metadata = Column(JSON)  # اطلاعات اضافی
    
    created_at = Column(DateTime, server_default=func.now())
    confirmed_at = Column(DateTime)
    
    wallet = relationship("Wallet", back_populates="transactions")


class EcologicalAction(Base):
    """اقدامات اکولوژیک"""
    __tablename__ = "ecological_actions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(SQLEnum(EcologicalActionType), nullable=False)
    
    # اطلاعات اقدام
    title = Column(String(300), nullable=False)
    description = Column(Text)
    
    # مقادیر
    quantity = Column(Float, nullable=False)  # تعداد درخت، هکتار، لیتر، etc.
    unit = Column(String(50), nullable=False)  # tree, hectare, liter, kWh, kg, ton
    
    # موقعیت
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(300))
    
    # مستندات
    evidence_urls = Column(JSON)  # تصاویر، ویدئوها، مدارک
    verification_method = Column(String(100))  # manual, ai, iot, satellite
    
    # وضعیت
    status = Column(SQLEnum(RewardStatus), default=RewardStatus.PENDING)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    
    # پاداش
    eco_reward = Column(BigInteger, default=0)  # پاداش ECO
    grc_reward = Column(BigInteger, default=0)  # پاداش GRC
    
    # تأثیر اکولوژیک
    carbon_sequestered = Column(Float)  # تن CO2
    water_saved = Column(Float)  # لیتر
    energy_generated = Column(Float)  # kWh
    land_restored = Column(Float)  # هکتار
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    rewards = relationship("EcologicalReward", back_populates="action")


class EcologicalReward(Base):
    """پاداش‌های اکولوژیک"""
    __tablename__ = "ecological_rewards"
    
    id = Column(Integer, primary_key=True, index=True)
    
    action_id = Column(Integer, ForeignKey("ecological_actions.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("ecocoin_wallets.id"), nullable=False)
    
    # پاداش‌ها
    eco_amount = Column(BigInteger, nullable=False)
    grc_amount = Column(BigInteger, default=0)
    
    # محاسبات
    base_reward = Column(BigInteger, nullable=False)
    bonus_multiplier = Column(Float, default=1.0)
    total_reward = Column(BigInteger, nullable=False)
    
    # وضعیت
    status = Column(String(20), default="pending")  # pending, paid, failed
    transaction_id = Column(Integer, ForeignKey("ecocoin_transactions.id"))
    
    paid_at = Column(DateTime)
    
    created_at = Column(DateTime, server_default=func.now())
    
    action = relationship("EcologicalAction", back_populates="rewards")
    wallet = relationship("Wallet", back_populates="rewards")


class Staking(Base):
    """سپرده‌گذاری توکن‌ها"""
    __tablename__ = "ecocoin_staking"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("ecocoin_wallets.id"), nullable=False)
    
    token_symbol = Column(String(10), nullable=False)
    amount = Column(BigInteger, nullable=False)
    
    # مدت سپرده‌گذاری
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime)
    lock_period_days = Column(Integer, default=30)
    
    # نرخ پاداش
    apy = Column(Float, default=10.0)  # Annual Percentage Yield
    accumulated_rewards = Column(BigInteger, default=0)
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    is_unlocked = Column(Boolean, default=False)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class RewardRate(Base):
    """نرخ‌های پاداش اکولوژیک"""
    __tablename__ = "reward_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    action_type = Column(SQLEnum(EcologicalActionType), unique=True, nullable=False)
    
    # نرخ‌های پاداش
    eco_per_unit = Column(BigInteger, nullable=False)  # ECO به ازای هر واحد
    grc_per_unit = Column(BigInteger, default=0)  # GRC به ازای هر واحد
    
    # ضرایب
    minimum_quantity = Column(Float, default=1.0)
    maximum_quantity = Column(Float, default=1000000.0)
    
    # ضریب_bonus
    bonus_multiplier = Column(Float, default=1.0)
    
    # تأثیر اکولوژیک به ازای هر واحد
    carbon_per_unit = Column(Float, default=0.0)  # تن CO2
    water_per_unit = Column(Float, default=0.0)  # لیتر
    energy_per_unit = Column(Float, default=0.0)  # kWh
    
    # وضعیت
    is_active = Column(Boolean, default=True)
    
    description = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class ExchangeRate(Base):
    """نرخ تبدیل توکن‌ها"""
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    from_token = Column(String(10), nullable=False)
    to_token = Column(String(10), nullable=False)
    
    rate = Column(Float, nullable=False)
    
    # محدودیت‌ها
    min_amount = Column(BigInteger, default=0)
    max_amount = Column(BigInteger, default=1000000)
    fee_percent = Column(Float, default=1.0)
    
    is_active = Column(Boolean, default=True)
    
    updated_at = Column(DateTime, server_default=func.now())
'''
    
    write_file(API_DIR / "modules" / "ecocoin" / "models.py", models_content)

    # =========================================================================
    # 2. Router - EcoCoin API
    # =========================================================================
    print("\n[2] Creating EcoCoin router...")
    
    router_content = '''# api/modules/ecocoin/router.py
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
import secrets
import hashlib

from api.core.database import get_db
from api.modules.ecocoin.models import (
    Token, Wallet, Transaction, EcologicalAction, EcologicalReward,
    Staking, RewardRate, ExchangeRate,
    TokenType, TransactionType, EcologicalActionType, RewardStatus
)

router = APIRouter(prefix="/ecocoin", tags=["EcoCoin System"])


# =========================================================================
# Pydantic Models
# =========================================================================
class WalletCreate(BaseModel):
    user_id: int


class TransferRequest(BaseModel):
    from_wallet_id: int
    to_address: str
    token_symbol: str
    amount: int
    description: Optional[str] = None


class EcologicalActionCreate(BaseModel):
    user_id: int
    action_type: str
    title: str
    description: Optional[str] = None
    quantity: float
    unit: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: Optional[str] = None
    evidence_urls: Optional[List[str]] = []


class StakeRequest(BaseModel):
    wallet_id: int
    token_symbol: str
    amount: int
    lock_period_days: int = 30


class ExchangeRequest(BaseModel):
    wallet_id: int
    from_token: str
    to_token: str
    amount: int


# =========================================================================
# Helper Functions
# =========================================================================
def generate_wallet_address() -> str:
    """تولید آدرس کیف پول"""
    return "0x" + secrets.token_hex(20)


def generate_transaction_hash() -> str:
    """تولید هش تراکنش"""
    timestamp = datetime.now().isoformat()
    random_str = secrets.token_hex(16)
    return "0x" + hashlib.sha256(f"{timestamp}{random_str}".encode()).hexdigest()[:64]


# =========================================================================
# Tokens
# =========================================================================
@router.get("/tokens")
async def list_tokens(db: AsyncSession = Depends(get_db)):
    """لیست توکن‌ها"""
    result = await db.execute(select(Token).where(Token.is_active == True))
    tokens = result.scalars().all()
    
    return {
        "tokens": [
            {
                "id": t.id,
                "symbol": t.symbol,
                "name": t.name,
                "token_type": t.token_type.value,
                "total_supply": t.total_supply,
                "circulating_supply": t.circulating_supply,
                "price_usd": t.price_usd,
                "price_irr": t.price_irr,
                "market_cap": t.market_cap,
                "is_stakable": t.is_stakable,
            }
            for t in tokens
        ]
    }


@router.get("/tokens/{symbol}")
async def get_token(symbol: str, db: AsyncSession = Depends(get_db)):
    """دریافت اطلاعات توکن"""
    result = await db.execute(select(Token).where(Token.symbol == symbol))
    token = result.scalar_one_or_none()
    
    if not token:
        raise HTTPException(404, "توکن یافت نشد")
    
    return {
        "token": {
            "id": token.id,
            "symbol": token.symbol,
            "name": token.name,
            "name_en": token.name_en,
            "token_type": token.token_type.value,
            "total_supply": token.total_supply,
            "circulating_supply": token.circulating_supply,
            "burned_amount": token.burned_amount,
            "price_usd": token.price_usd,
            "price_irr": token.price_irr,
            "market_cap": token.market_cap,
            "decimals": token.decimals,
            "max_supply": token.max_supply,
            "contract_address": token.contract_address,
            "blockchain": token.blockchain,
            "description": token.description,
        }
    }


# =========================================================================
# Wallets
# =========================================================================
@router.post("/wallets")
async def create_wallet(data: WalletCreate, db: AsyncSession = Depends(get_db)):
    """ایجاد کیف پول جدید"""
    # بررسی وجود کیف پول
    result = await db.execute(select(Wallet).where(Wallet.user_id == data.user_id))
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(400, "کیف پول قبلاً ایجاد شده است")
    
    # ایجاد کیف پول
    wallet = Wallet(
        user_id=data.user_id,
        wallet_address=generate_wallet_address(),
        eco_balance=0,
        grc_balance=0,
    )
    
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    
    return {
        "id": wallet.id,
        "wallet_address": wallet.wallet_address,
        "status": "created"
    }


@router.get("/wallets/{user_id}")
async def get_wallet(user_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت اطلاعات کیف پول"""
    result = await db.execute(select(Wallet).where(Wallet.user_id == user_id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(404, "کیف پول یافت نشد")
    
    return {
        "wallet": {
            "id": wallet.id,
            "wallet_address": wallet.wallet_address,
            "eco_balance": wallet.eco_balance,
            "grc_balance": wallet.grc_balance,
            "staked_eco": wallet.staked_eco,
            "staked_grc": wallet.staked_grc,
            "total_earned": wallet.total_earned,
            "total_spent": wallet.total_spent,
            "user_level": wallet.user_level,
            "reputation_score": wallet.reputation_score,
        }
    }


# =========================================================================
# Transfers
# =========================================================================
@router.post("/transfer")
async def transfer_tokens(data: TransferRequest, db: AsyncSession = Depends(get_db)):
    """انتقال توکن"""
    # دریافت کیف پول مبدأ
    result = await db.execute(select(Wallet).where(Wallet.id == data.from_wallet_id))
    from_wallet = result.scalar_one_or_none()
    
    if not from_wallet:
        raise HTTPException(404, "کیف پول مبدأ یافت نشد")
    
    # بررسی موجودی
    if data.token_symbol == "ECO":
        if from_wallet.eco_balance < data.amount:
            raise HTTPException(400, "موجودی ECO کافی نیست")
        from_wallet.eco_balance -= data.amount
    elif data.token_symbol == "GRC":
        if from_wallet.grc_balance < data.amount:
            raise HTTPException(400, "موجودی GRC کافی نیست")
        from_wallet.grc_balance -= data.amount
    else:
        raise HTTPException(400, "توکن نامعتبر")
    
    # دریافت یا ایجاد کیف پول مقصد
    result = await db.execute(select(Wallet).where(Wallet.wallet_address == data.to_address))
    to_wallet = result.scalar_one_or_none()
    
    if not to_wallet:
        # ایجاد کیف پول جدید برای آدرس مقصد
        to_wallet = Wallet(
            user_id=0,  # کاربر ناشناس
            wallet_address=data.to_address,
        )
        db.add(to_wallet)
        await db.flush()
    
    # افزایش موجودی مقصد
    if data.token_symbol == "ECO":
        to_wallet.eco_balance += data.amount
    elif data.token_symbol == "GRC":
        to_wallet.grc_balance += data.amount
    
    # ثبت تراکنش
    transaction = Transaction(
        transaction_hash=generate_transaction_hash(),
        wallet_id=from_wallet.id,
        token_symbol=data.token_symbol,
        transaction_type=TransactionType.TRANSFER,
        amount=data.amount,
        from_address=from_wallet.wallet_address,
        to_address=data.to_address,
        status="confirmed",
        description=data.description,
        confirmed_at=datetime.now(),
    )
    
    db.add(transaction)
    
    # به‌روزرسانی آمار
    from_wallet.total_spent += data.amount
    
    await db.commit()
    
    return {
        "transaction_hash": transaction.transaction_hash,
        "status": "confirmed",
        "new_balance": from_wallet.eco_balance if data.token_symbol == "ECO" else from_wallet.grc_balance,
    }


# =========================================================================
# Ecological Actions & Rewards
# =========================================================================
@router.post("/actions")
async def submit_ecological_action(data: EcologicalActionCreate, db: AsyncSession = Depends(get_db)):
    """ثبت اقدام اکولوژیک"""
    # دریافت نرخ پاداش
    result = await db.execute(
        select(RewardRate).where(RewardRate.action_type == EcologicalActionType(data.action_type))
    )
    reward_rate = result.scalar_one_or_none()
    
    if not reward_rate:
        raise HTTPException(404, "نرخ پاداش برای این نوع اقدام تعریف نشده است")
    
    # محاسبه پاداش
    eco_reward = int(reward_rate.eco_per_unit * data.quantity * reward_rate.bonus_multiplier)
    grc_reward = int(reward_rate.grc_per_unit * data.quantity * reward_rate.bonus_multiplier)
    
    # محاسبه تأثیر اکولوژیک
    carbon = reward_rate.carbon_per_unit * data.quantity
    water = reward_rate.water_per_unit * data.quantity
    energy = reward_rate.energy_per_unit * data.quantity
    
    # ایجاد اقدام
    action = EcologicalAction(
        user_id=data.user_id,
        action_type=EcologicalActionType(data.action_type),
        title=data.title,
        description=data.description,
        quantity=data.quantity,
        unit=data.unit,
        latitude=data.latitude,
        longitude=data.longitude,
        location_name=data.location_name,
        evidence_urls=data.evidence_urls,
        eco_reward=eco_reward,
        grc_reward=grc_reward,
        carbon_sequestered=carbon,
        water_saved=water,
        energy_generated=energy,
        status=RewardStatus.PENDING,
    )
    
    db.add(action)
    await db.commit()
    await db.refresh(action)
    
    return {
        "id": action.id,
        "eco_reward": eco_reward,
        "grc_reward": grc_reward,
        "carbon_sequestered": carbon,
        "water_saved": water,
        "energy_generated": energy,
        "status": "pending_verification",
    }


@router.post("/actions/{action_id}/verify")
async def verify_action(action_id: int, verifier_id: int, approved: bool = True, db: AsyncSession = Depends(get_db)):
    """تأیید اقدام اکولوژیک و پرداخت پاداش"""
    result = await db.execute(select(EcologicalAction).where(EcologicalAction.id == action_id))
    action = result.scalar_one_or_none()
    
    if not action:
        raise HTTPException(404, "اقدام یافت نشد")
    
    if action.status != RewardStatus.PENDING:
        raise HTTPException(400, "اقدام قبلاً بررسی شده است")
    
    if approved:
        action.status = RewardStatus.APPROVED
        action.verified_by = verifier_id
        action.verified_at = datetime.now()
        
        # دریافت کیف پول کاربر
        result = await db.execute(select(Wallet).where(Wallet.user_id == action.user_id))
        wallet = result.scalar_one_or_none()
        
        if not wallet:
            raise HTTPException(404, "کیف پول کاربر یافت نشد")
        
        # پرداخت پاداش
        wallet.eco_balance += action.eco_reward
        wallet.grc_balance += action.grc_reward
        wallet.total_earned += action.eco_reward + action.grc_reward
        
        # ثبت تراکنش پاداش
        transaction = Transaction(
            transaction_hash=generate_transaction_hash(),
            wallet_id=wallet.id,
            token_symbol="ECO",
            transaction_type=TransactionType.REWARD,
            amount=action.eco_reward,
            from_address="ecocoin_system",
            to_address=wallet.wallet_address,
            status="confirmed",
            description=f"پاداش اکولوژیک: {action.title}",
            confirmed_at=datetime.now(),
        )
        db.add(transaction)
        
        # ثبت پاداش
        reward = EcologicalReward(
            action_id=action.id,
            wallet_id=wallet.id,
            eco_amount=action.eco_reward,
            grc_amount=action.grc_reward,
            base_reward=action.eco_reward,
            bonus_multiplier=1.0,
            total_reward=action.eco_reward + action.grc_reward,
            status="paid",
            transaction_id=transaction.id,
            paid_at=datetime.now(),
        )
        db.add(reward)
        
        await db.commit()
        
        return {
            "status": "approved",
            "eco_paid": action.eco_reward,
            "grc_paid": action.grc_reward,
        }
    else:
        action.status = RewardStatus.REJECTED
        action.verified_by = verifier_id
        action.verified_at = datetime.now()
        await db.commit()
        
        return {"status": "rejected"}


@router.get("/actions/user/{user_id}")
async def get_user_actions(user_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت اقدامات اکولوژیک کاربر"""
    result = await db.execute(
        select(EcologicalAction)
        .where(EcologicalAction.user_id == user_id)
        .order_by(desc(EcologicalAction.created_at))
    )
    actions = result.scalars().all()
    
    return {
        "actions": [
            {
                "id": a.id,
                "action_type": a.action_type.value,
                "title": a.title,
                "quantity": a.quantity,
                "unit": a.unit,
                "eco_reward": a.eco_reward,
                "grc_reward": a.grc_reward,
                "status": a.status.value,
                "created_at": a.created_at,
            }
            for a in actions
        ],
        "total_earned": sum(a.eco_reward + a.grc_reward for a in actions if a.status == RewardStatus.APPROVED),
    }


# =========================================================================
# Staking
# =========================================================================
@router.post("/stake")
async def stake_tokens(data: StakeRequest, db: AsyncSession = Depends(get_db)):
    """سپرده‌گذاری توکن"""
    result = await db.execute(select(Wallet).where(Wallet.id == data.wallet_id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(404, "کیف پول یافت نشد")
    
    # بررسی موجودی
    if data.token_symbol == "ECO":
        if wallet.eco_balance < data.amount:
            raise HTTPException(400, "موجودی ECO کافی نیست")
        wallet.eco_balance -= data.amount
        wallet.staked_eco += data.amount
    elif data.token_symbol == "GRC":
        if wallet.grc_balance < data.amount:
            raise HTTPException(400, "موجودی GRC کافی نیست")
        wallet.grc_balance -= data.amount
        wallet.staked_grc += data.amount
    else:
        raise HTTPException(400, "توکن نامعتبر")
    
    # ایجاد سپرده‌گذاری
    staking = Staking(
        wallet_id=wallet.id,
        token_symbol=data.token_symbol,
        amount=data.amount,
        lock_period_days=data.lock_period_days,
        end_date=datetime.now() + timedelta(days=data.lock_period_days),
        apy=10.0 if data.token_symbol == "ECO" else 15.0,
    )
    
    db.add(staking)
    
    # ثبت تراکنش
    transaction = Transaction(
        transaction_hash=generate_transaction_hash(),
        wallet_id=wallet.id,
        token_symbol=data.token_symbol,
        transaction_type=TransactionType.STAKE,
        amount=data.amount,
        from_address=wallet.wallet_address,
        to_address="staking_contract",
        status="confirmed",
        description=f"سپرده‌گذاری {data.amount} {data.token_symbol}",
        confirmed_at=datetime.now(),
    )
    db.add(transaction)
    
    await db.commit()
    
    return {
        "staking_id": staking.id,
        "amount": data.amount,
        "end_date": staking.end_date,
        "apy": staking.apy,
    }


# =========================================================================
# Exchange
# =========================================================================
@router.post("/exchange")
async def exchange_tokens(data: ExchangeRequest, db: AsyncSession = Depends(get_db)):
    """تبدیل توکن‌ها"""
    result = await db.execute(select(Wallet).where(Wallet.id == data.wallet_id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(404, "کیف پول یافت نشد")
    
    # دریافت نرخ تبدیل
    result = await db.execute(
        select(ExchangeRate).where(
            (ExchangeRate.from_token == data.from_token) &
            (ExchangeRate.to_token == data.to_token)
        )
    )
    exchange_rate = result.scalar_one_or_none()
    
    if not exchange_rate:
        raise HTTPException(404, "نرخ تبدیل یافت نشد")
    
    # بررسی محدودیت‌ها
    if data.amount < exchange_rate.min_amount:
        raise HTTPException(400, f"حداقل مقدار: {exchange_rate.min_amount}")
    if data.amount > exchange_rate.max_amount:
        raise HTTPException(400, f"حداکثر مقدار: {exchange_rate.max_amount}")
    
    # محاسبه مقدار دریافتی
    fee = int(data.amount * exchange_rate.fee_percent / 100)
    net_amount = data.amount - fee
    received_amount = int(net_amount * exchange_rate.rate)
    
    # کسر از مبدأ
    if data.from_token == "ECO":
        if wallet.eco_balance < data.amount:
            raise HTTPException(400, "موجودی ECO کافی نیست")
        wallet.eco_balance -= data.amount
    elif data.from_token == "GRC":
        if wallet.grc_balance < data.amount:
            raise HTTPException(400, "موجودی GRC کافی نیست")
        wallet.grc_balance -= data.amount
    
    # افزودن به مقصد
    if data.to_token == "ECO":
        wallet.eco_balance += received_amount
    elif data.to_token == "GRC":
        wallet.grc_balance += received_amount
    
    # ثبت تراکنش
    transaction = Transaction(
        transaction_hash=generate_transaction_hash(),
        wallet_id=wallet.id,
        token_symbol=data.from_token,
        transaction_type=TransactionType.EXCHANGE,
        amount=data.amount,
        from_address=wallet.wallet_address,
        to_address="exchange_contract",
        status="confirmed",
        description=f"تبدیل {data.amount} {data.from_token} به {received_amount} {data.to_token}",
        metadata={"received_amount": received_amount, "fee": fee, "rate": exchange_rate.rate},
        confirmed_at=datetime.now(),
    )
    db.add(transaction)
    
    await db.commit()
    
    return {
        "from_amount": data.amount,
        "from_token": data.from_token,
        "to_amount": received_amount,
        "to_token": data.to_token,
        "fee": fee,
        "rate": exchange_rate.rate,
    }


# =========================================================================
# Reward Rates
# =========================================================================
@router.get("/reward-rates")
async def list_reward_rates(db: AsyncSession = Depends(get_db)):
    """لیست نرخ‌های پاداش"""
    result = await db.execute(select(RewardRate).where(RewardRate.is_active == True))
    rates = result.scalars().all()
    
    return {
        "rates": [
            {
                "id": r.id,
                "action_type": r.action_type.value,
                "eco_per_unit": r.eco_per_unit,
                "grc_per_unit": r.grc_per_unit,
                "bonus_multiplier": r.bonus_multiplier,
                "carbon_per_unit": r.carbon_per_unit,
                "water_per_unit": r.water_per_unit,
                "energy_per_unit": r.energy_per_unit,
                "description": r.description,
            }
            for r in rates
        ]
    }


# =========================================================================
# Statistics
# =========================================================================
@router.get("/stats")
async def get_ecocoin_stats(db: AsyncSession = Depends(get_db)):
    """آمار کلی اکو کوین"""
    # تعداد کیف پول‌ها
    wallets_count = (await db.execute(select(func.count(Wallet.id)))).scalar() or 0
    
    # مجموع پاداش‌های پرداخت‌شده
    total_rewards = (await db.execute(
        select(func.sum(EcologicalReward.eco_amount + EcologicalReward.grc_amount))
        .where(EcologicalReward.status == "paid")
    )).scalar() or 0
    
    # تعداد اقدامات اکولوژیک
    actions_count = (await db.execute(select(func.count(EcologicalAction.id)))).scalar() or 0
    
    # تأثیر اکولوژیک کل
    total_carbon = (await db.execute(
        select(func.sum(EcologicalAction.carbon_sequestered))
        .where(EcologicalAction.status == RewardStatus.APPROVED)
    )).scalar() or 0
    
    total_water = (await db.execute(
        select(func.sum(EcologicalAction.water_saved))
        .where(EcologicalAction.status == RewardStatus.APPROVED)
    )).scalar() or 0
    
    total_energy = (await db.execute(
        select(func.sum(EcologicalAction.energy_generated))
        .where(EcologicalAction.status == RewardStatus.APPROVED)
    )).scalar() or 0
    
    return {
        "wallets_count": wallets_count,
        "total_rewards": total_rewards,
        "actions_count": actions_count,
        "ecological_impact": {
            "carbon_sequestered_tons": total_carbon,
            "water_saved_liters": total_water,
            "energy_generated_kwh": total_energy,
        },
    }
'''
    
    write_file(API_DIR / "modules" / "ecocoin" / "router.py", router_content)

    # =========================================================================
    # 3. __init__.py
    # =========================================================================
    print("\n[3] Creating __init__.py...")
    write_file(API_DIR / "modules" / "ecocoin" / "__init__.py", "from . import models, router\n")

    # =========================================================================
    # 4. Update main.py
    # =========================================================================
    print("\n[4] Updating main.py...")
    main_path = API_DIR / "main.py"
    
    if main_path.exists():
        content = main_path.read_text(encoding="utf-8")
        
        if "ecocoin_router" not in content:
            lines = content.split('\n')
            import_idx = router_idx = 0
            
            for i, line in enumerate(lines):
                if line.startswith("from api.modules."):
                    import_idx = i
                if "app.include_router(" in line:
                    router_idx = i
            
            lines.insert(import_idx + 1, "from api.modules.ecocoin.router import router as ecocoin_router")
            lines.insert(router_idx + 2, 'app.include_router(ecocoin_router, prefix="/api/v1")')
            
            main_path.write_text('\n'.join(lines), encoding="utf-8")
            print("   + ecocoin_router added")

    # =========================================================================
    # 5. Frontend - EcoCoin Dashboard
    # =========================================================================
    print("\n[5] Creating EcoCoin frontend...")
    
    frontend_content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Coins, Wallet, TrendingUp, Send, Download,
  Plus, Eye, CheckCircle, Clock, AlertTriangle, Leaf,
  TreePine, Droplets, Sun, Recycle, Wind, Mountain,
  X, Save, ArrowUpCircle, ArrowDownCircle, RefreshCw,
  BarChart3, PieChart, Target, Award, Zap, Shield
} from "lucide-react";

const API_BASE = "http://localhost:8000/api/v1/ecocoin";

export default function EcoCoinPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [wallet, setWallet] = useState<any>(null);
  const [tokens, setTokens] = useState<any[]>([]);
  const [actions, setActions] = useState<any[]>([]);
  const [rewardRates, setRewardRates] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [showModal, setShowModal] = useState<string | null>(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [tokensRes, ratesRes, statsRes] = await Promise.all([
        fetch(`${API_BASE}/tokens`),
        fetch(`${API_BASE}/reward-rates`),
        fetch(`${API_BASE}/stats`),
      ]);
      
      if (tokensRes.ok) setTokens((await tokensRes.json()).tokens || []);
      if (ratesRes.ok) setRewardRates((await ratesRes.json()).rates || []);
      if (statsRes.ok) setStats(await statsRes.json());
      
      // Load wallet for user 1 (demo)
      const walletRes = await fetch(`${API_BASE}/wallets/1`);
      if (walletRes.ok) setWallet((await walletRes.json()).wallet);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#10b981" },
    { id: "wallet", label: "کیف پول", icon: Wallet, color: "#3b82f6" },
    { id: "actions", label: "اقدامات اکولوژیک", icon: Leaf, color: "#22c55e" },
    { id: "rewards", label: "نرخ پاداش‌ها", icon: Award, color: "#f59e0b" },
    { id: "exchange", label: "تبدیل توکن", icon: RefreshCw, color: "#8b5cf6" },
  ];

  const actionIcons: any = {
    tree_planting: TreePine,
    land_restoration: Mountain,
    water_saving: Droplets,
    renewable_energy: Sun,
    recycling: Recycle,
    carbon_reduction: Wind,
    soil_conservation: Leaf,
    biodiversity: TreePine,
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Header */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 to-teal-700 opacity-20" />
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl">
                <Coins className="h-10 w-10 text-white" />
              </div>
              <div>
                <p className="text-emerald-400 text-sm font-medium mb-1">سیستم ارز دیجیتال اکولوژیک</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">اکو کوین (EcoCoin)</h1>
                <p className="text-lg text-slate-300">پاداش‌های اکولوژیک با سیستم دو توکنی</p>
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
        {activeTab === "dashboard" && stats && (
          <div className="space-y-6">
            {/* Tokens */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {tokens.map(token => (
                <motion.div
                  key={token.symbol}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-gradient-to-br from-emerald-900/30 to-teal-900/30 border border-emerald-500/30 rounded-2xl p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 rounded-xl bg-emerald-500/20">
                        <Coins className="h-8 w-8 text-emerald-400" />
                      </div>
                      <div>
                        <h3 className="text-2xl font-black text-white">{token.symbol}</h3>
                        <p className="text-sm text-slate-400">{token.name}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      token.token_type === "eco" ? "bg-emerald-500/20 text-emerald-300" : "bg-purple-500/20 text-purple-300"
                    }`}>
                      {token.token_type === "eco" ? "Utility" : "Governance"}
                    </span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-slate-400">قیمت:</span>
                      <span className="text-white font-bold">${token.price_usd}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">ارزش بازار:</span>
                      <span className="text-white font-bold">${token.market_cap?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">عرضه در گردش:</span>
                      <span className="text-emerald-400 font-bold">{token.circulating_supply?.toLocaleString()}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Wallet className="h-6 w-6 mb-2 text-blue-400" />
                <p className="text-2xl font-black text-white">{stats.wallets_count}</p>
                <p className="text-xs text-slate-400">کیف پول‌ها</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Award className="h-6 w-6 mb-2 text-amber-400" />
                <p className="text-2xl font-black text-white">{stats.total_rewards?.toLocaleString()}</p>
                <p className="text-xs text-slate-400">پاداش‌های پرداختی</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <Leaf className="h-6 w-6 mb-2 text-emerald-400" />
                <p className="text-2xl font-black text-white">{stats.actions_count}</p>
                <p className="text-xs text-slate-400">اقدامات اکولوژیک</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5">
                <TrendingUp className="h-6 w-6 mb-2 text-purple-400" />
                <p className="text-2xl font-black text-white">{stats.ecological_impact?.carbon_sequestered_tons?.toFixed(2)}</p>
                <p className="text-xs text-slate-400">تن CO2 جذب‌شده</p>
              </div>
            </div>

            {/* Ecological Impact */}
            <div className="bg-gradient-to-br from-green-900/20 to-emerald-900/20 border border-green-500/30 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Leaf className="h-6 w-6 text-green-400" />
                تأثیر اکولوژیک کل
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <Wind className="h-12 w-12 text-blue-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">{stats.ecological_impact?.carbon_sequestered_tons?.toFixed(2)}</p>
                  <p className="text-sm text-slate-400">تن CO2 جذب‌شده</p>
                </div>
                <div className="text-center">
                  <Droplets className="h-12 w-12 text-cyan-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">{stats.ecological_impact?.water_saved_liters?.toLocaleString()}</p>
                  <p className="text-sm text-slate-400">لیتر آب صرفه‌جویی‌شده</p>
                </div>
                <div className="text-center">
                  <Sun className="h-12 w-12 text-amber-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">{stats.ecological_impact?.energy_generated_kwh?.toLocaleString()}</p>
                  <p className="text-sm text-slate-400">kWh انرژی تولیدشده</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Wallet */}
        {activeTab === "wallet" && wallet && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-blue-900/30 to-indigo-900/30 border border-blue-500/30 rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <p className="text-blue-300 text-sm mb-2">آدرس کیف پول</p>
                  <p className="text-lg font-mono text-white">{wallet.wallet_address}</p>
                </div>
                <Shield className="h-12 w-12 text-blue-400" />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-slate-900/50 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Coins className="h-8 w-8 text-emerald-400" />
                    <div>
                      <p className="text-sm text-slate-400">EcoCoin (ECO)</p>
                      <p className="text-3xl font-black text-white">{wallet.eco_balance?.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setShowModal("send_eco")} className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold">
                      <Send className="h-4 w-4 inline ml-1" /> ارسال
                    </button>
                    <button onClick={() => setShowModal("stake")} className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-bold">
                      <Target className="h-4 w-4 inline ml-1" /> سپرده‌گذاری
                    </button>
                  </div>
                </div>
                
                <div className="bg-slate-900/50 rounded-xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Coins className="h-8 w-8 text-purple-400" />
                    <div>
                      <p className="text-sm text-slate-400">GreenCredit (GRC)</p>
                      <p className="text-3xl font-black text-white">{wallet.grc_balance?.toLocaleString()}</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => setShowModal("send_grc")} className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm font-bold">
                      <Send className="h-4 w-4 inline ml-1" /> ارسال
                    </button>
                    <button onClick={() => setShowModal("exchange")} className="flex-1 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-bold">
                      <RefreshCw className="h-4 w-4 inline ml-1" /> تبدیل
                    </button>
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-3 gap-4 pt-6 border-t border-slate-700">
                <div className="text-center">
                  <p className="text-sm text-slate-400 mb-1">سطح کاربر</p>
                  <p className="text-2xl font-black text-white">{wallet.user_level}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-slate-400 mb-1">امتیاز اعتبار</p>
                  <p className="text-2xl font-black text-emerald-400">{wallet.reputation_score?.toFixed(1)}</p>
                </div>
                <div className="text-center">
                  <p className="text-sm text-slate-400 mb-1">کل درآمد</p>
                  <p className="text-2xl font-black text-amber-400">{wallet.total_earned?.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Actions */}
        {activeTab === "actions" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">اقدامات اکولوژیک</h2>
              <button onClick={() => setShowModal("action")} className="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> ثبت اقدام جدید
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {rewardRates.map(rate => {
                const Icon = actionIcons[rate.action_type] || Leaf;
                return (
                  <motion.div
                    key={rate.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-emerald-500/50 transition-all"
                  >
                    <Icon className="h-12 w-12 text-emerald-400 mb-4" />
                    <h3 className="text-lg font-bold text-white mb-2">{rate.action_type}</h3>
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">پاداش ECO:</span>
                        <span className="text-emerald-400 font-bold">{rate.eco_per_unit}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">پاداش GRC:</span>
                        <span className="text-purple-400 font-bold">{rate.grc_per_unit}</span>
                      </div>
                    </div>
                    <div className="pt-4 border-t border-slate-700 text-xs text-slate-500">
                      <p>CO2: {rate.carbon_per_unit} تن</p>
                      <p>آب: {rate.water_per_unit} لیتر</p>
                      <p>انرژی: {rate.energy_per_unit} kWh</p>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}

        {/* Rewards */}
        {activeTab === "rewards" && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-white">نرخ پاداش‌های اکولوژیک</h2>
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-800/50">
                  <tr>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">نوع اقدام</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">ECO/واحد</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">GRC/واحد</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">ضریب bonus</th>
                    <th className="text-right px-6 py-4 text-sm font-bold text-slate-300">تأثیر اکولوژیک</th>
                  </tr>
                </thead>
                <tbody>
                  {rewardRates.map(rate => (
                    <tr key={rate.id} className="border-t border-slate-800 hover:bg-slate-800/30">
                      <td className="px-6 py-4 text-white font-bold">{rate.action_type}</td>
                      <td className="px-6 py-4 text-emerald-400 font-bold">{rate.eco_per_unit}</td>
                      <td className="px-6 py-4 text-purple-400 font-bold">{rate.grc_per_unit}</td>
                      <td className="px-6 py-4 text-amber-400">{rate.bonus_multiplier}x</td>
                      <td className="px-6 py-4 text-slate-300 text-sm">
                        <p>CO2: {rate.carbon_per_unit}t</p>
                        <p>H2O: {rate.water_per_unit}L</p>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Exchange */}
        {activeTab === "exchange" && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6">تبدیل توکن‌ها</h2>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">از توکن</label>
                  <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option value="ECO">EcoCoin (ECO)</option>
                    <option value="GRC">GreenCredit (GRC)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">مقدار</label>
                  <input type="number" placeholder="مقدار" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div className="text-center">
                  <ArrowDownCircle className="h-8 w-8 text-purple-400 mx-auto" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">به توکن</label>
                  <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option value="GRC">GreenCredit (GRC)</option>
                    <option value="ECO">EcoCoin (ECO)</option>
                  </select>
                </div>
                <button className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                  <RefreshCw className="h-5 w-5" /> تبدیل توکن
                </button>
              </div>
            </div>
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
                  {showModal === "action" && "ثبت اقدام اکولوژیک"}
                  {showModal === "send_eco" && "ارسال EcoCoin"}
                  {showModal === "send_grc" && "ارسال GreenCredit"}
                  {showModal === "stake" && "سپرده‌گذاری توکن"}
                  {showModal === "exchange" && "تبدیل توکن"}
                </h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>

              {showModal === "action" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نوع اقدام *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      {rewardRates.map(rate => (
                        <option key={rate.id} value={rate.action_type}>{rate.action_type}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">عنوان *</label>
                    <input type="text" placeholder="عنوان اقدام" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">مقدار *</label>
                      <input type="number" placeholder="مقدار" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                    <div>
                      <label className="block text-sm font-bold text-white mb-2">واحد *</label>
                      <input type="text" placeholder="tree, hectare, liter" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                    <textarea rows={3} placeholder="توضیحات..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Save className="h-5 w-5" /> ثبت اقدام
                  </button>
                </div>
              )}

              {(showModal === "send_eco" || showModal === "send_grc") && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">آدرس مقصد *</label>
                    <input type="text" placeholder="0x..." className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" dir="ltr" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مقدار *</label>
                    <input type="number" placeholder="مقدار" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توضیحات</label>
                    <input type="text" placeholder="توضیحات" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Send className="h-5 w-5" /> ارسال
                  </button>
                </div>
              )}

              {showModal === "stake" && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">توکن</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option value="ECO">EcoCoin (ECO) - APY 10%</option>
                      <option value="GRC">GreenCredit (GRC) - APY 15%</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مقدار *</label>
                    <input type="number" placeholder="مقدار" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مدت قفل (روز)</label>
                    <input type="number" placeholder="30" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                    <Target className="h-5 w-5" /> سپرده‌گذاری
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
    
    write_file(WEB_DIR / "app" / "ecocoin" / "page.tsx", frontend_content)

    # =========================================================================
    # 6. Seed Reward Rates
    # =========================================================================
    print("\n[6] Creating seed script for reward rates...")
    
    seed_content = '''# api/scripts/seed_ecocoin.py
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from api.core.database import engine, async_session, Base
from api.modules.ecocoin.models import Token, RewardRate, ExchangeRate, EcologicalActionType, TokenType

async def seed():
    print("Seeding EcoCoin data...")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        # Create tokens
        eco_token = Token(
            symbol="ECO",
            name="EcoCoin",
            name_en="EcoCoin",
            token_type=TokenType.ECO,
            total_supply=1_000_000_000,
            circulating_supply=100_000_000,
            price_usd=0.15,
            price_irr=9000,
            market_cap=15_000_000,
            decimals=18,
            max_supply=1_000_000_000,
            is_stakable=True,
            description="توکن Utility برای پاداش فعالیت‌های اکولوژیک",
        )
        session.add(eco_token)
        
        grc_token = Token(
            symbol="GRC",
            name="GreenCredit",
            name_en="GreenCredit",
            token_type=TokenType.GRC,
            total_supply=0,
            circulating_supply=50_000_000,
            price_usd=0.25,
            price_irr=15000,
            market_cap=12_500_000,
            decimals=18,
            is_stakable=True,
            description="توکن Governance برای رأی‌دهی و حاکمیت",
        )
        session.add(grc_token)
        
        # Create reward rates
        reward_rates = [
            {
                "action_type": EcologicalActionType.TREE_PLANTING,
                "eco_per_unit": 10,
                "grc_per_unit": 2,
                "bonus_multiplier": 1.0,
                "carbon_per_unit": 0.025,
                "description": "۱۰ ECO به ازای هر درخت کاشته‌شده",
            },
            {
                "action_type": EcologicalActionType.LAND_RESTORATION,
                "eco_per_unit": 100,
                "grc_per_unit": 20,
                "bonus_multiplier": 1.5,
                "carbon_per_unit": 5.0,
                "water_per_unit": 10000,
                "description": "۱۰۰ ECO به ازای هر هکتار احیاشده",
            },
            {
                "action_type": EcologicalActionType.WATER_SAVING,
                "eco_per_unit": 5,
                "grc_per_unit": 1,
                "bonus_multiplier": 1.2,
                "water_per_unit": 1000,
                "description": "۵ ECO به ازای هر ۱۰۰۰ لیتر صرفه‌جویی",
            },
            {
                "action_type": EcologicalActionType.RENEWABLE_ENERGY,
                "eco_per_unit": 50,
                "grc_per_unit": 10,
                "bonus_multiplier": 1.3,
                "carbon_per_unit": 0.5,
                "energy_per_unit": 1000,
                "description": "۵۰ ECO به ازای هر MWh انرژی تجدیدپذیر",
            },
            {
                "action_type": EcologicalActionType.RECYCLING,
                "eco_per_unit": 2,
                "grc_per_unit": 0.5,
                "bonus_multiplier": 1.0,
                "carbon_per_unit": 0.005,
                "description": "۲ ECO به ازای هر ۱۰ کیلوگرم بازیافت",
            },
            {
                "action_type": EcologicalActionType.CARBON_REDUCTION,
                "eco_per_unit": 20,
                "grc_per_unit": 5,
                "bonus_multiplier": 1.5,
                "carbon_per_unit": 1.0,
                "description": "۲۰ ECO به ازای هر تن CO2 کاهش‌یافته",
            },
            {
                "action_type": EcologicalActionType.SOIL_CONSERVATION,
                "eco_per_unit": 30,
                "grc_per_unit": 8,
                "bonus_multiplier": 1.2,
                "carbon_per_unit": 0.5,
                "description": "۳۰ ECO به ازای هر هکتار حفاظت خاک",
            },
            {
                "action_type": EcologicalActionType.BIODIVERSITY,
                "eco_per_unit": 50,
                "grc_per_unit": 15,
                "bonus_multiplier": 2.0,
                "description": "۵۰ ECO به ازای هر پروژه تنوع زیستی",
            },
        ]
        
        for rate_data in reward_rates:
            rate = RewardRate(**rate_data)
            session.add(rate)
        
        # Create exchange rates
        exchange_rates = [
            {"from_token": "ECO", "to_token": "GRC", "rate": 0.6, "min_amount": 100, "max_amount": 1000000, "fee_percent": 1.0},
            {"from_token": "GRC", "to_token": "ECO", "rate": 1.5, "min_amount": 50, "max_amount": 500000, "fee_percent": 1.0},
        ]
        
        for rate_data in exchange_rates:
            rate = ExchangeRate(**rate_data)
            session.add(rate)
        
        await session.commit()
        print("✅ EcoCoin data seeded successfully!")
        print("   - 2 tokens created (ECO, GRC)")
        print("   - 8 reward rates created")
        print("   - 2 exchange rates created")

if __name__ == "__main__":
    asyncio.run(seed())
'''
    
    write_file(API_DIR / "scripts" / "seed_ecocoin.py", seed_content)

    # =========================================================================
    # 7. Clean cache
    # =========================================================================
    print("\n[7] Cleaning cache...")
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("   + .next removed")
        except Exception as e:
            print(f"   ! {e}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print("DONE! EcoCoin Dual Token System created!")
    print("=" * 70)
    print("\nFeatures:")
    print("  + Dual Token System (ECO + GRC)")
    print("  + Ecological Rewards (8 action types)")
    print("  + Wallet Management")
    print("  + Token Transfers")
    print("  + Staking (10% APY for ECO, 15% for GRC)")
    print("  + Token Exchange")
    print("  + Ecological Impact Tracking")
    print("\nReward Rates:")
    print("  🌳 Tree Planting: 10 ECO + 2 GRC per tree")
    print("  🏔️ Land Restoration: 100 ECO + 20 GRC per hectare")
    print("  💧 Water Saving: 5 ECO + 1 GRC per 1000L")
    print("  ☀️ Renewable Energy: 50 ECO + 10 GRC per MWh")
    print("  ♻️ Recycling: 2 ECO + 0.5 GRC per 10kg")
    print("  💨 Carbon Reduction: 20 ECO + 5 GRC per ton CO2")
    print("  🌱 Soil Conservation: 30 ECO + 8 GRC per hectare")
    print("  🦋 Biodiversity: 50 ECO + 15 GRC per project")
    print("\nNext steps:")
    print("  1. Seed data: python api/scripts/seed_ecocoin.py")
    print("  2. uvicorn api.main:app --reload --port 8000")
    print("  3. cd apps\\web && pnpm run dev -- -p 3001")
    print("  4. Visit: http://localhost:3001/ecocoin")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    sys.exit(main())
# api/modules/ecocoin/models.py
"""
مدل‌های دیتابیس سیستم توکن اکویی (EcoCoin) - نسخه مالی امن
نسخه 2.0 - اصلاح شده با Numeric و Check Constraints
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, JSON, Boolean, 
    ForeignKey, Text, Enum as SQLEnum, BigInteger, Numeric, CheckConstraint, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


# ============================================================
# Enums
# ============================================================
class TokenType(enum.Enum):
    ECO = "eco"
    GRC = "grc"

class TxType(enum.Enum):
    REWARD = "reward"
    TRANSFER = "transfer"
    STAKE = "stake"
    UNSTAKE = "unstake"
    BURN = "burn"
    MINT = "mint"
    EXCHANGE = "exchange"

# 🔴 اصلاح: اضافه کردن Enum برای وضعیت تراکنش
class TxStatus(enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

class EcoActionType(enum.Enum):
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


# ============================================================
# Models
# ============================================================
class EcoToken(Base):
    """Token definitions (ECO and GRC)"""
    __tablename__ = "eco_tokens"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    name_en = Column(String(100))
    token_type = Column(SQLEnum(TokenType), nullable=False)
    total_supply = Column(BigInteger, default=0)
    circulating_supply = Column(BigInteger, default=0)
    burned_amount = Column(BigInteger, default=0)
    
    # 🔴 اصلاح: تبدیل Float به Numeric برای دقت مالی مطلق
    price_usd = Column(Numeric(precision=20, scale=8), default=0.0)
    price_irr = Column(Numeric(precision=20, scale=8), default=0.0)
    market_cap = Column(Numeric(precision=20, scale=8), default=0.0)
    
    decimals = Column(Integer, default=18)
    max_supply = Column(BigInteger)
    contract_address = Column(String(100))
    blockchain = Column(String(50), default="polygon")
    is_active = Column(Boolean, default=True)
    is_stakable = Column(Boolean, default=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class EcoUserWallet(Base):
    """User wallets for ECO and GRC tokens"""
    __tablename__ = "eco_user_wallets"
    
    # 🔴 اصلاح حیاتی: اضافه کردن Check Constraint برای جلوگیری از موجودی منفی
    __table_args__ = (
        CheckConstraint('eco_balance >= 0', name='check_eco_balance_non_negative'),
        CheckConstraint('grc_balance >= 0', name='check_grc_balance_non_negative'),
        CheckConstraint('staked_eco >= 0', name='check_staked_eco_non_negative'),
        CheckConstraint('staked_grc >= 0', name='check_staked_grc_non_negative'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    wallet_address = Column(String(100), unique=True, nullable=False)
    
    # موجودی‌ها (BigInteger عالی است)
    eco_balance = Column(BigInteger, default=0)
    grc_balance = Column(BigInteger, default=0)
    staked_eco = Column(BigInteger, default=0)
    staked_grc = Column(BigInteger, default=0)
    total_earned = Column(BigInteger, default=0)
    total_spent = Column(BigInteger, default=0)
    
    user_level = Column(Integer, default=1)
    reputation_score = Column(Float, default=0.0) # برای امتیاز اعتباری، Float قابل قبول است
    is_active = Column(Boolean, default=True)
    is_frozen = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    transactions = relationship("EcoTx", back_populates="wallet")
    rewards = relationship("EcoReward", back_populates="wallet")


class EcoTx(Base):
    """All token transactions"""
    __tablename__ = "eco_transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(100), unique=True, nullable=False)
    wallet_id = Column(Integer, ForeignKey("eco_user_wallets.id"), nullable=False, index=True) # 🔴 ایندکس اضافه شد
    token_symbol = Column(String(10), nullable=False, index=True) # 🔴 ایندکس اضافه شد
    tx_type = Column(SQLEnum(TxType), nullable=False)
    amount = Column(BigInteger, nullable=False)
    fee = Column(BigInteger, default=0)
    from_address = Column(String(100))
    to_address = Column(String(100))
    block_number = Column(BigInteger)
    
    # 🔴 اصلاح: تبدیل String به Enum
    status = Column(SQLEnum(TxStatus), default=TxStatus.PENDING, index=True) 
    
    confirmations = Column(Integer, default=0)
    description = Column(Text)
    extra_data = Column(JSON)
    created_at = Column(DateTime, server_default=func.now(), index=True) # 🔴 ایندکس اضافه شد
    confirmed_at = Column(DateTime)

    wallet = relationship("EcoUserWallet", back_populates="transactions")


class EcoAction(Base):
    """Ecological actions submitted by users"""
    __tablename__ = "eco_actions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action_type = Column(SQLEnum(EcoActionType), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text)
    quantity = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(300))
    evidence_urls = Column(JSON)
    verification_method = Column(String(100))
    status = Column(SQLEnum(RewardStatus), default=RewardStatus.PENDING, index=True)
    verified_by = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    eco_reward = Column(BigInteger, default=0)
    grc_reward = Column(BigInteger, default=0)
    carbon_sequestered = Column(Float)
    water_saved = Column(Float)
    energy_generated = Column(Float)
    land_restored = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    rewards = relationship("EcoReward", back_populates="action")


class EcoReward(Base):
    """Rewards paid for ecological actions"""
    __tablename__ = "eco_rewards"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("eco_actions.id"), nullable=False)
    wallet_id = Column(Integer, ForeignKey("eco_user_wallets.id"), nullable=False)
    eco_amount = Column(BigInteger, nullable=False)
    grc_amount = Column(BigInteger, default=0)
    base_reward = Column(BigInteger, nullable=False)
    bonus_multiplier = Column(Numeric(precision=10, scale=4), default=1.0) # 🔴 اصلاح به Numeric
    total_reward = Column(BigInteger, nullable=False)
    status = Column(String(20), default="pending")
    tx_id = Column(Integer, ForeignKey("eco_transactions.id"))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    action = relationship("EcoAction", back_populates="rewards")
    wallet = relationship("EcoUserWallet", back_populates="rewards")


class EcoStaking(Base):
    """Token staking records"""
    __tablename__ = "eco_staking"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("eco_user_wallets.id"), nullable=False, index=True)
    token_symbol = Column(String(10), nullable=False)
    amount = Column(BigInteger, nullable=False)
    start_date = Column(DateTime, server_default=func.now())
    end_date = Column(DateTime)
    lock_period_days = Column(Integer, default=30)
    apy = Column(Numeric(precision=10, scale=4), default=10.0) # 🔴 اصلاح به Numeric
    accumulated_rewards = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True, index=True)
    is_unlocked = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class EcoRewardRate(Base):
    """Reward rates per ecological action type"""
    __tablename__ = "eco_reward_rates"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(SQLEnum(EcoActionType), unique=True, nullable=False)
    eco_per_unit = Column(BigInteger, nullable=False)
    grc_per_unit = Column(BigInteger, default=0)
    minimum_quantity = Column(Float, default=1.0)
    maximum_quantity = Column(Float, default=1000000.0)
    bonus_multiplier = Column(Numeric(precision=10, scale=4), default=1.0) # 🔴 اصلاح به Numeric
    carbon_per_unit = Column(Numeric(precision=20, scale=8), default=0.0) # 🔴 اصلاح به Numeric
    water_per_unit = Column(Numeric(precision=20, scale=8), default=0.0)
    energy_per_unit = Column(Numeric(precision=20, scale=8), default=0.0)
    is_active = Column(Boolean, default=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())


class EcoExchangeRate(Base):
    """Exchange rates between tokens"""
    __tablename__ = "eco_exchange_rates"

    id = Column(Integer, primary_key=True, index=True)
    from_token = Column(String(10), nullable=False)
    to_token = Column(String(10), nullable=False)
    rate = Column(Numeric(precision=20, scale=8), nullable=False) # 🔴 اصلاح به Numeric
    min_amount = Column(BigInteger, default=0)
    max_amount = Column(BigInteger, default=1000000)
    fee_percent = Column(Numeric(precision=10, scale=4), default=1.0) # 🔴 اصلاح به Numeric
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now())
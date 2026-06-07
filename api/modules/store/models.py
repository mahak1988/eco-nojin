# api/modules/store/models.py
import enum

from sqlalchemy import JSON, Boolean, Column, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.core.database import Base


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


class StoreWallet(Base):
    __tablename__ = "store_store_wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    user = relationship("User")

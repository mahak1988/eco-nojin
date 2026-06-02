from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from api.core.database import Base


class UserAccount(Base):
    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String(32), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    name = Column(String(100), default="")
    wallet_address = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

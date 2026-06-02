from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.sql import func
from api.core.database import Base


class StoreItem(Base):
    __tablename__ = "store_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, default="")
    price = Column(Float, default=0)
    currency = Column(String(8), default="IRR")
    status = Column(String(32), default="active")
    stock = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

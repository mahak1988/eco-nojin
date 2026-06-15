"""SQLAlchemy models for financial domain."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from api.core.database import Base
from datetime import datetime


class ProjectBudgetDB(Base):
    __tablename__ = "project_budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True)
    capex = Column(Float)
    opex_annual = Column(Float)
    currency = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class CarbonCreditDB(Base):
    __tablename__ = "carbon_credits"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(String, index=True)
    volume_tco2e = Column(Float)
    verification_date = Column(DateTime)
    price_per_ton = Column(Float)
    status = Column(String)
    blockchain_tx_hash = Column(String, nullable=True)

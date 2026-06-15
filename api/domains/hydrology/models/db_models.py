"""SQLAlchemy Database Models for Hydrology Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class HydrologySimulations(Base):
    """مدل پایگاه داده برای hydrology_simulations"""
    __tablename__ = "hydrology_simulations"

    id = Column(Integer, primary_key=True)
    watershed_id = Column(String(100), index=True, nullable=False)
    model_type = Column(String(50), nullable=False)
    scenario_name = Column(String(200), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    results_json = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<HydrologySimulations(id={self.id})>"

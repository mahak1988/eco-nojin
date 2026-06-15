"""SQLAlchemy Database Models for Mrv Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class MrvReports(Base):
    """مدل پایگاه داده برای mrv_reports"""
    __tablename__ = "mrv_reports"

    id = Column(Integer, primary_key=True)
    report_id = Column(String(100), unique=True, nullable=False)
    pilot_site = Column(String(50), index=True, nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    soc_change_tco2 = Column(Float, default=0.0)
    biomass_sequestration_tco2 = Column(Float, default=0.0)
    water_saved_m3 = Column(Float, default=0.0)
    methodology = Column(String(100), default="IPCC AFOLU Tier 2")
    report_hash = Column(String(64), nullable=True)
    blockchain_tx = Column(String(100), nullable=True)
    verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<MrvReports(id={self.id})>"

"""SQLAlchemy Database Models for Logframe Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class LogframeIndicators(Base):
    """مدل پایگاه داده برای logframe_indicators"""
    __tablename__ = "logframe_indicators"

    id = Column(Integer, primary_key=True)
    indicator_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    level = Column(String(50), nullable=False)
    sdg_targets = Column(String(200), nullable=True)
    baseline_value = Column(Float, nullable=True)
    target_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    gef_core = Column(Boolean, default=False)
    gcf_core = Column(Boolean, default=False)
    ndc_aligned = Column(Boolean, default=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<LogframeIndicators(id={self.id})>"

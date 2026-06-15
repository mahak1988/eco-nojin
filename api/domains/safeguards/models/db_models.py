"""SQLAlchemy Database Models for Safeguards Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class Grievances(Base):
    """مدل پایگاه داده برای grievances"""
    __tablename__ = "grievances"

    id = Column(Integer, primary_key=True)
    grievance_id = Column(String(100), unique=True, nullable=False)
    pilot_site = Column(String(50), index=True, nullable=False)
    category = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(50), default="received")
    description = Column(Text, nullable=True)
    complainant_type = Column(String(50), default="individual")
    complainant_gender = Column(String(20), default="not_disclosed")
    is_anonymous = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Grievances(id={self.id})>"

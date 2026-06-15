"""SQLAlchemy Database Models for Dashboard Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class Dashboards(Base):
    """مدل پایگاه داده برای dashboards"""
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True)
    dashboard_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    owner_id = Column(String(100), nullable=True)
    config_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Dashboards(id={self.id})>"

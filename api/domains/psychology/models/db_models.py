"""SQLAlchemy Database Models for Psychology Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class PsychologyTests(Base):
    """مدل پایگاه داده برای psychology_tests"""
    __tablename__ = "psychology_tests"

    id = Column(Integer, primary_key=True)
    test_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(String(100), index=True, nullable=False)
    pilot_site = Column(String(50), index=True, nullable=True)
    score = Column(Float, nullable=True)
    interpretation = Column(String(50), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PsychologyTests(id={self.id})>"

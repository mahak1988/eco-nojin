"""SQLAlchemy Database Models for Training Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class TrainingSessions(Base):
    """مدل پایگاه داده برای training_sessions"""
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    pilot_site = Column(String(50), index=True, nullable=False)
    module_id = Column(String(100), nullable=False)
    activity_type = Column(String(50), nullable=False)
    participant_count = Column(Integer, default=0)
    women_count = Column(Integer, default=0)
    youth_count = Column(Integer, default=0)
    conducted_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TrainingSessions(id={self.id})>"

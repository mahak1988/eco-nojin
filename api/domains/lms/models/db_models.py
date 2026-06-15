"""SQLAlchemy Database Models for Lms Domain"""
from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, Date
from sqlalchemy.sql import func
from datetime import datetime

try:
    from api.core.database import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class LmsCourses(Base):
    """مدل پایگاه داده برای lms_courses"""
    __tablename__ = "lms_courses"

    id = Column(Integer, primary_key=True)
    course_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(300), nullable=False)
    language = Column(String(10), default="fa")
    duration_hours = Column(Float, nullable=True)
    pilot_site = Column(String(50), nullable=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<LmsCourses(id={self.id})>"

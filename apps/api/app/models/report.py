"""Report Model"""

from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.models.base import Base, TimestampMixin, IDMixin


class Report(Base, IDMixin, TimestampMixin):
    """Report model"""
    __tablename__ = "reports"

    title = Column(String, nullable=False)
    type = Column(String, nullable=False)
    content = Column(JSON, default=dict)
    generated_at = Column(DateTime)
    generated_by = Column(Integer)
    status = Column(String, default="draft")

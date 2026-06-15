"""Audit Model"""

from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from app.models.base import Base, IDMixin


class Audit(Base, IDMixin):
    """Audit log model"""
    __tablename__ = "audits"

    action = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    target_type = Column(String)
    target_id = Column(Integer)
    details = Column(JSON, default=dict)
    ip_address = Column(String)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="audits")

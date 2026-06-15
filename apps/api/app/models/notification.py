"""Notification Model"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, IDMixin


class Notification(Base, IDMixin, TimestampMixin):
    """Notification model"""
    __tablename__ = "notifications"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    type = Column(String, default="info")
    is_read = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="notifications")

"""Setting Model"""

from sqlalchemy import Column, String, JSON
from app.models.base import Base, TimestampMixin, IDMixin


class Setting(Base, IDMixin, TimestampMixin):
    """Setting model"""
    __tablename__ = "settings"

    key = Column(String, unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    category = Column(String, default="general")
    description = Column(String)

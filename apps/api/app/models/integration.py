"""Integration Model"""

from sqlalchemy import Column, String, Enum, JSON
import enum
from app.models.base import Base, TimestampMixin, IDMixin


class IntegrationStatus(str, enum.Enum):
    CONNECTED = "connected"
    AVAILABLE = "available"
    DISCONNECTED = "disconnected"


class Integration(Base, IDMixin, TimestampMixin):
    """Integration model"""
    __tablename__ = "integrations"

    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    status = Column(Enum(IntegrationStatus), default=IntegrationStatus.AVAILABLE)
    config = Column(JSON, default=dict)
    last_sync = Column(String)

"""Module Model"""

from sqlalchemy import Column, String, Integer, Enum, JSON
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin, IDMixin


class ModuleStatus(str, enum.Enum):
    LIVE = "live"
    BETA = "beta"
    COMING_SOON = "coming_soon"


class Module(Base, IDMixin, TimestampMixin):
    """Module model"""
    __tablename__ = "modules"

    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    status = Column(Enum(ModuleStatus), default=ModuleStatus.COMING_SOON)
    config = Column(JSON, default=dict)
    version = Column(String, default="1.0.0")

    # Relationships
    data_points = relationship("DataPoint", back_populates="module")

"""DataPoint Model"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin, IDMixin


class DataStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class DataPoint(Base, IDMixin, TimestampMixin):
    """DataPoint model"""
    __tablename__ = "data_points"

    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    data_type = Column(String, nullable=False)
    value = Column(JSON, nullable=False)
    unit = Column(String)
    timestamp = Column(DateTime, nullable=False)
    status = Column(Enum(DataStatus), default=DataStatus.PENDING)
    ai_confidence = Column(Float)
    extra_data = Column(JSON, default=dict)

    # Relationships
    project = relationship("Project", back_populates="data_points")
    module = relationship("Module", back_populates="data_points")
    user = relationship("User", back_populates="data_points")

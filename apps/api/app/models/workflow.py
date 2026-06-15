"""Workflow Model"""

from sqlalchemy import Column, String, Integer, JSON, Enum
import enum
from app.models.base import Base, TimestampMixin, IDMixin


class WorkflowStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Workflow(Base, IDMixin, TimestampMixin):
    """Workflow model"""
    __tablename__ = "workflows"

    name = Column(String, nullable=False)
    description = Column(String)
    steps = Column(JSON, default=list)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.ACTIVE)
    current_step = Column(Integer, default=0)

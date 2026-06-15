"""Project Model"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.models.base import Base, TimestampMixin, IDMixin


class ProjectType(str, enum.Enum):
    WATER = "water"
    FOREST = "forest"
    SOIL = "soil"
    CARBON = "carbon"
    MIXED = "mixed"


class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"


class Project(Base, IDMixin, TimestampMixin):
    """Project model"""
    __tablename__ = "projects"

    name = Column(String, nullable=False)
    description = Column(String)
    country = Column(String, nullable=False)
    region = Column(String)
    type = Column(Enum(ProjectType), nullable=False)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.PLANNING)
    start_date = Column(DateTime)
    hectares = Column(Float, default=0.0)
    budget = Column(Float, default=0.0)
    spent = Column(Float, default=0.0)
    progress = Column(Integer, default=0)
    manager_id = Column(Integer, ForeignKey("users.id"))

    # Relationships with CASCADE DELETE
    manager = relationship("User", back_populates="projects")
    data_points = relationship(
        "DataPoint",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    kpis = relationship(
        "KPI",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

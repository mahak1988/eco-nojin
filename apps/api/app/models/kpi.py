"""KPI Model"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, IDMixin


class KPI(Base, IDMixin, TimestampMixin):
    """KPI model"""
    __tablename__ = "kpis"

    name = Column(String, nullable=False)
    description = Column(String)
    value = Column(Float, default=0.0)
    target = Column(Float)
    unit = Column(String)
    category = Column(String)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))

    # Relationships
    project = relationship("Project", back_populates="kpis")

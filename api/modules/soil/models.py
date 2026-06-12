# api/modules/soil/models.py

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.core.database import Base


class SoilProfile(Base):
    __tablename__ = "soil_profiles"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    layers = relationship("SoilLayer", back_populates="profile")


class SoilLayer(Base):
    __tablename__ = "soil_layers"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("soil_profiles.id"), nullable=False)

    depth_top_cm = Column(Float, nullable=False)      # مثلاً 0
    depth_bottom_cm = Column(Float, nullable=False)   # مثلاً 30

    bulk_density = Column(Float, nullable=True)
    field_capacity = Column(Float, nullable=True)
    wilting_point = Column(Float, nullable=True)
    saturated_hydraulic_conductivity = Column(Float, nullable=True)
    organic_carbon = Column(Float, nullable=True)

    profile = relationship("SoilProfile", back_populates="layers")
# api/modules/farmer/models.py

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.core.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True, unique=True, index=True)
    national_id = Column(String(50), nullable=True, unique=True, index=True)

    created_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # ارتباط با ماژول soil_water
    soil_water_analyses = relationship(
        "SoilWaterAnalysis",
        back_populates="farmer",
        lazy="selectin",
    )
    soil_erosion_analyses = relationship("SoilErosionAnalysis", back_populates="farmer", lazy="selectin")
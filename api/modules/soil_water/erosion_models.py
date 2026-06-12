from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from api.core.database import Base


class SoilErosionAnalysis(Base):
    """
    ذخیره تحلیل‌های RUSLE برای هر موقعیت/مزرعه.

    A = R * K * LS * C * P
    """

    __tablename__ = "soil_erosion_analyses"

    id = Column(Integer, primary_key=True, index=True)

    # ارتباط اختیاری با کشاورز و مکان
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True, index=True)
    location_id = Column(String(255), nullable=True, index=True)

    # فاکتورهای RUSLE
    R = Column(Float, nullable=False)   # rainfall erosivity
    K = Column(Float, nullable=False)   # soil erodibility
    LS = Column(Float, nullable=False)  # slope length & steepness
    C = Column(Float, nullable=False)   # cover-management
    P = Column(Float, nullable=False)   # support practice

    # خروجی
    annual_soil_loss = Column(Float, nullable=False)  # t/ha/year
    risk_class = Column(String(32), nullable=False)   # very_low/low/moderate/high/severe

    # متادیتا
    title = Column(String(255), nullable=True)
    description = Column(String(2000), nullable=True)
    meta = Column(JSON, nullable=True)  # برای ذخیره منبع داده، روش محاسبه R/K/LS و...

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    farmer = relationship("Farmer", back_populates="soil_erosion_analyses", lazy="joined")
"""Crop catalog ORM with agronomic fields."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    name_fa: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    scientific_name: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    category: Mapped[str] = mapped_column(String(80), default="cereal", nullable=False)
    season: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    water_need_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    growth_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Agronomy
    planting_method: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    row_spacing_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    plant_spacing_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sowing_depth_cm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seed_rate_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    irrigation_method: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    irrigation_interval_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    kc_mid: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # crop coefficient
    fertilizer_n_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fertilizer_p_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fertilizer_k_kg_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_ph_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_ph_max: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    harvest_method: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    harvest_moisture_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    common_pests: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    common_diseases: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    care_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

"""Crop catalog ORM with agronomic fields."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base


class Crop(Base):
    __tablename__ = "crops"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    name_fa: Mapped[str | None] = mapped_column(String(120), nullable=True)
    scientific_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    category: Mapped[str] = mapped_column(String(80), default="cereal", nullable=False)
    season: Mapped[str | None] = mapped_column(String(40), nullable=True)
    water_need_mm: Mapped[float | None] = mapped_column(Float, nullable=True)
    growth_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Agronomy
    planting_method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    row_spacing_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    plant_spacing_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    sowing_depth_cm: Mapped[float | None] = mapped_column(Float, nullable=True)
    seed_rate_kg_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    irrigation_method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    irrigation_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    kc_mid: Mapped[float | None] = mapped_column(Float, nullable=True)  # crop coefficient
    fertilizer_n_kg_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    fertilizer_p_kg_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    fertilizer_k_kg_ha: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_ph_min: Mapped[float | None] = mapped_column(Float, nullable=True)
    soil_ph_max: Mapped[float | None] = mapped_column(Float, nullable=True)
    harvest_method: Mapped[str | None] = mapped_column(String(80), nullable=True)
    harvest_moisture_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    common_pests: Mapped[str | None] = mapped_column(Text, nullable=True)
    common_diseases: Mapped[str | None] = mapped_column(Text, nullable=True)
    care_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

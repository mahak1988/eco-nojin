"""Crop catalog ORM."""

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
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

"""Farm ORM models."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base
from apps.shared_core.timeutil import utc_now


class Farm(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    region: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    area_ha: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    # GeoJSON polygon as text for Phase1 (PostGIS later)
    geojson: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

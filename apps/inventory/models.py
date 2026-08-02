"""Inventory: seeds, fertilizers, pesticides."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base
from apps.shared_core.timeutil import utc_now


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    sku: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    min_stock: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    npk: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    active_ingredient: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    target_pest: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    farm_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=utc_now, onupdate=utc_now, nullable=False
    )

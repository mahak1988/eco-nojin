"""Inventory: seeds, fertilizers, pesticides."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(40), nullable=False
    )  # seed|fertilizer|pesticide|tool
    sku: Mapped[str | None] = mapped_column(String(80), nullable=True)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)
    quantity: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    min_stock: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    npk: Mapped[str | None] = mapped_column(String(40), nullable=True)  # e.g. 20-20-20
    active_ingredient: Mapped[str | None] = mapped_column(String(120), nullable=True)
    target_pest: Mapped[str | None] = mapped_column(String(160), nullable=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

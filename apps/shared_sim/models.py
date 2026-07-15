"""
shared_sim models | مدل‌های shared_sim
=====================================
SQLAlchemy ORM models for the shared_sim module.

NOTE: This is a starter template. Adjust fields and relationships
      to match your actual domain model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

# Adjust this import to match your project's database session setup
try:
    from apps.shared_core.database.base import Base
except ImportError:
    # Fallback: define a minimal Base if shared_core is not yet set up
    from sqlalchemy.orm import DeclarativeBase
    class Base(DeclarativeBase):
        pass


class SharedSim(Base):
    """Primary shared_sim entity."""

    __tablename__ = "shared_sim"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<SharedSim(id={self.id}, name={self.name!r})>"

    def to_dict(self) -> dict:
        """Serialize to dictionary (for API responses)."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

"""
Agriculture Schools Models
=========================
Database models for agricultural education institutions.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.session import Base


class AgricultureSchool(Base):
    """Agricultural education institution model."""

    __tablename__ = "agriculture_schools"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    province: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False)
    school_type: Mapped[str] = mapped_column(String(30), default="university", nullable=False)
    established: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    students_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    logo: Mapped[str] = mapped_column(String(10), default="📣", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    fields: Mapped[List["SchoolField"]] = relationship("SchoolField", back_populates="school", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<AgricultureSchool(id={self.id}, name={self.name!r})>"


class SchoolField(Base):
    """Field of study for agriculture schools."""

    __tablename__ = "school_fields"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    school_id: Mapped[int] = mapped_column(Integer, ForeignKey("agriculture_schools.id"), nullable=False, index=True)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Relationships
    school: Mapped["AgricultureSchool"] = relationship("AgricultureSchool", back_populates="fields")

    def __repr__(self) -> str:
        return f"<SchoolField(school_id={self.school_id}, field={self.field_name!r})>"


class SchoolType(str):
    UNIVERSITY = "university"
    INSTITUTE = "institute"
    TRAINING_CENTER = "training-center"
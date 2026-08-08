"""
Education Models
================
Database models for educational content and courses.
"""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.session import Base


class CourseCategory(str, PyEnum):
    """Course category enumeration."""

    AGRICULTURE = "agriculture"
    WATER_MANAGEMENT = "water-management"
    ENVIRONMENTAL_SCIENCE = "environmental-science"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"
    SCIENCE = "science"


class DifficultyLevel(str, PyEnum):
    """Course difficulty level enumeration."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Course(Base):
    """Educational course model."""

    __tablename__ = "courses"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(50), default="beginner", nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    instructor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instructor_id: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    lessons: Mapped[list["Lesson"]] = relationship(
        "Lesson", back_populates="course", cascade="all, delete-orphan"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<Course(id={self.id}, title={self.title!r})>"


class Lesson(Base):
    """Lesson within a course."""

    __tablename__ = "lessons"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    course_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("courses.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="lessons")

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<Lesson(course_id={self.course_id}, title={self.title!r})>"


class Enrollment(Base):
    """User enrollment in a course."""

    __tablename__ = "enrollments"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    course_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("courses.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0.0 to 1.0
    enrolled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")

    def __repr__(self) -> str:
        """Handle __repr__."""
        return f"<Enrollment(course_id={self.course_id}, user_id={self.user_id})>"


# Backward compatibility aliases
CourseLevel = DifficultyLevel

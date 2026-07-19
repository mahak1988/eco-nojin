"""
Library Models
==============
Database models for digital library and resource management.
"""

from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.session import Base


class LibraryResource(Base):
    """Digital library resource (article, document, video, etc.)."""

    __tablename__ = "library_resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # bytes
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # comma-separated
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    download_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<LibraryResource(id={self.id}, title={self.title!r})>"


class LibraryCategory(str):
    RESEARCH = "research"
    GUIDES = "guides"
    POLICIES = "policies"
    REPORTS = "reports"
    TRAINING = "training"


class ResourceCategory(str):
    AGRICULTURE = "agriculture"
    WATER = "water"
    ENVIRONMENT = "environment"
    ECONOMICS = "economics"
    TECHNOLOGY = "technology"
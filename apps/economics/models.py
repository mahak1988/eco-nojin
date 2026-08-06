"""
Economics Models
================
Database models for economic analysis, cost-benefit calculations,
and financial planning for agricultural operations.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.shared_core.database.base import Base


class AnalysisType(str, PyEnum):
    """Type of economic analysis."""
    COST_BENEFIT = "cost_benefit"
    ROI = "roi"
    NPV = "npv"
    IRR = "irr"
    BREAK_EVEN = "break_even"


class Currency(str, PyEnum):
    """Supported currencies."""
    USD = "USD"
    EUR = "EUR"
    IRR = "IRR"
    AFN = "AFN"
    IQD = "IQD"
    JOD = "JOD"


class EconomicAnalysis(Base):
    """Economic analysis record for a farm or project."""

    __tablename__ = "economic_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("farms.id"), nullable=True, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False, default="cost_benefit")
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="USD")
    total_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_revenue: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_benefit: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    npv: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    irr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    roi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    payback_period_years: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    break_even_point: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    discount_rate: Mapped[float] = mapped_column(Float, default=0.1, nullable=False)
    time_horizon_years: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    cost_items: Mapped[list["CostItem"]] = relationship(
        "CostItem", back_populates="analysis", cascade="all, delete-orphan"
    )
    benefit_items: Mapped[list["BenefitItem"]] = relationship(
        "BenefitItem", back_populates="analysis", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<EconomicAnalysis(id={self.id}, title={self.title!r}, type={self.analysis_type})>"


class CostItem(Base):
    """Individual cost line item in an economic analysis."""

    __tablename__ = "economic_cost_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(Integer, ForeignKey("economic_analyses.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    year: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    analysis: Mapped["EconomicAnalysis"] = relationship("EconomicAnalysis", back_populates="cost_items")

    def __repr__(self) -> str:
        return f"<CostItem(id={self.id}, category={self.category!r}, amount={self.amount})>"


class BenefitItem(Base):
    """Individual benefit/revenue line item in an economic analysis."""

    __tablename__ = "economic_benefit_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    analysis_id: Mapped[int] = mapped_column(Integer, ForeignKey("economic_analyses.id"), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    frequency: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    year: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    analysis: Mapped["EconomicAnalysis"] = relationship("EconomicAnalysis", back_populates="benefit_items")

    def __repr__(self) -> str:
        return f"<BenefitItem(id={self.id}, category={self.category!r}, amount={self.amount})>"
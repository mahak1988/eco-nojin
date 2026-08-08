"""
Traditional Ecological Knowledge (TEK) Models
==============================================
Earth Memory Layer - Layer 2 of Hydroma-Nojin Architecture.

Stores 3000-year ecosystem knowledge extracted from successful ancient
civilizations: Qanat (Iran), Waru Waru (Andes), Terra Preta (Amazon),
Milpa (Maya), Subak (Bali).

Based on: Hydroma-Nojin Platform paper - Section 2.2 & 3.4
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime, Float, ForeignKey, JSON, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from apps.shared_core.database.session import Base

logger = logging.getLogger(__name__)

class HistoricalPattern(Base):
    """Traditional Ecological Knowledge pattern from a historical civilization."""
    __tablename__ = "historical_patterns"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pattern_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_fa: Mapped[str] = mapped_column(String(255), nullable=False)
    civilization: Mapped[str] = mapped_column(String(255), nullable=False)
    civilization_fa: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(255), nullable=False)
    age_years: Mapped[int] = mapped_column(Integer, nullable=False)
    problem_category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    solution_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    climate_zones: Mapped[str] = mapped_column(JSON, nullable=False, default=list)
    principles: Mapped[str] = mapped_column(JSON, nullable=False, default=list)
    applicability_conditions: Mapped[str] = mapped_column(JSON, nullable=False, default=dict)
    formulas: Mapped[str] = mapped_column(JSON, nullable=False, default=list)
    recommendation_template: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    recommendation_template_fa: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    success_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    sustainability_index: Mapped[float] = mapped_column(Float, nullable=False, default=0.8)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    match_results: Mapped[List["TEKMatchResult"]] = relationship("TEKMatchResult", back_populates="pattern", cascade="all, delete-orphan")
    __table_args__ = (Index("ix_patterns_climate_category", "problem_category", "is_active"), Index("ix_patterns_age_score", "age_years", "success_score"))
    def __repr__(self): return f"<HistoricalPattern(id={self.pattern_id}, civ='{self.civilization}', age={self.age_years}y)>"

class TEKMatchResult(Base):
    """Result of matching a TEK pattern against current conditions."""
    __tablename__ = "tek_match_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pattern_id: Mapped[int] = mapped_column(Integer, ForeignKey("historical_patterns.id", ondelete="CASCADE"), index=True, nullable=False)
    farm_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("farms.id", ondelete="SET NULL"), index=True, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    climate_zone: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    annual_rainfall_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    groundwater_depth_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    elevation_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    soil_organic_carbon_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    frost_risk: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    matched_principles: Mapped[str] = mapped_column(JSON, nullable=False, default=list)
    recommendation: Mapped[str] = mapped_column(Text, nullable=True)
    recommendation_fa: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    pattern: Mapped["HistoricalPattern"] = relationship("HistoricalPattern", back_populates="match_results")
    __table_args__ = (Index("ix_tek_match_farm", "farm_id", "pattern_id"),)
    def __repr__(self): return f"<TEKMatchResult(pattern={self.pattern_id}, score={self.match_score:.2f})>"

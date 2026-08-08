"""
Economics Schemas
=================
Pydantic models for request/response validation of economic analysis.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CostItemBase(BaseModel):
    """Base schema for cost items."""

    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., ge=0)
    is_recurring: bool = False
    frequency: str | None = None
    year: int = Field(1, ge=1)


class CostItemCreate(CostItemBase):
    """Schema for creating a cost item."""


class CostItemResponse(CostItemBase):
    """Schema for cost item response."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    analysis_id: int


class BenefitItemBase(BaseModel):
    """Base schema for benefit items."""

    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., ge=0)
    is_recurring: bool = False
    frequency: str | None = None
    year: int = Field(1, ge=1)


class BenefitItemCreate(BenefitItemBase):
    """Schema for creating a benefit item."""


class BenefitItemResponse(BenefitItemBase):
    """Schema for benefit item response."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    analysis_id: int


class EconomicAnalysisBase(BaseModel):
    """Base schema for economic analysis."""

    title: str = Field(..., min_length=1, max_length=255)
    analysis_type: str = Field("cost_benefit", pattern="^(cost_benefit|roi|npv|irr|break_even)$")
    currency: str = Field("USD", max_length=10)
    discount_rate: float = Field(0.1, ge=0, le=1)
    time_horizon_years: int = Field(5, ge=1, le=50)
    notes: str | None = None


class EconomicAnalysisCreate(EconomicAnalysisBase):
    """Schema for creating an economic analysis."""

    farm_id: int | None = None
    project_id: str | None = None
    cost_items: list[CostItemCreate] = Field(default_factory=list)
    benefit_items: list[BenefitItemCreate] = Field(default_factory=list)


class EconomicAnalysisUpdate(BaseModel):
    """Schema for updating an economic analysis."""

    title: str | None = Field(None, min_length=1, max_length=255)
    analysis_type: str | None = Field(None, pattern="^(cost_benefit|roi|npv|irr|break_even)$")
    currency: str | None = Field(None, max_length=10)
    discount_rate: float | None = Field(None, ge=0, le=1)
    time_horizon_years: int | None = Field(None, ge=1, le=50)
    notes: str | None = None
    is_active: bool | None = None


class EconomicAnalysisResponse(EconomicAnalysisBase):
    """Schema for economic analysis response."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    farm_id: int | None = None
    project_id: str | None = None
    total_cost: float
    total_revenue: float
    total_benefit: float
    npv: float | None = None
    irr: float | None = None
    roi: float | None = None
    payback_period_years: float | None = None
    break_even_point: float | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    cost_items: list[CostItemResponse] = Field(default_factory=list)
    benefit_items: list[BenefitItemResponse] = Field(default_factory=list)


class EconomicAnalysisListResponse(BaseModel):
    """Paginated list response."""

    items: list[EconomicAnalysisResponse]
    total: int
    skip: int = 0
    limit: int = 100


class CostBenefitResult(BaseModel):
    """Result of a cost-benefit calculation."""

    total_cost: float
    total_benefit: float
    net_benefit: float
    benefit_cost_ratio: float
    roi: float
    npv: float | None = None
    payback_period_years: float | None = None
    break_even_point: float | None = None

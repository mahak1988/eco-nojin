"""
Economics Schemas
=================
Pydantic models for request/response validation of economic analysis.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class CostItemBase(BaseModel):
    """Base schema for cost items."""
    category: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=255)
    amount: float = Field(..., ge=0)
    is_recurring: bool = False
    frequency: Optional[str] = None
    year: int = Field(1, ge=1)


class CostItemCreate(CostItemBase):
    """Schema for creating a cost item."""
    pass


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
    frequency: Optional[str] = None
    year: int = Field(1, ge=1)


class BenefitItemCreate(BenefitItemBase):
    """Schema for creating a benefit item."""
    pass


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
    notes: Optional[str] = None


class EconomicAnalysisCreate(EconomicAnalysisBase):
    """Schema for creating an economic analysis."""
    farm_id: Optional[int] = None
    project_id: Optional[str] = None
    cost_items: list[CostItemCreate] = Field(default_factory=list)
    benefit_items: list[BenefitItemCreate] = Field(default_factory=list)


class EconomicAnalysisUpdate(BaseModel):
    """Schema for updating an economic analysis."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    analysis_type: Optional[str] = Field(None, pattern="^(cost_benefit|roi|npv|irr|break_even)$")
    currency: Optional[str] = Field(None, max_length=10)
    discount_rate: Optional[float] = Field(None, ge=0, le=1)
    time_horizon_years: Optional[int] = Field(None, ge=1, le=50)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class EconomicAnalysisResponse(EconomicAnalysisBase):
    """Schema for economic analysis response."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    farm_id: Optional[int] = None
    project_id: Optional[str] = None
    total_cost: float
    total_revenue: float
    total_benefit: float
    npv: Optional[float] = None
    irr: Optional[float] = None
    roi: Optional[float] = None
    payback_period_years: Optional[float] = None
    break_even_point: Optional[float] = None
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
    npv: Optional[float] = None
    payback_period_years: Optional[float] = None
    break_even_point: Optional[float] = None
"""KPI Pydantic Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


class KPIBase(BaseModel):
    """Base KPI schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    value: float = Field(default=0.0)
    target: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    project_id: int


class KPICreate(KPIBase):
    """Schema for creating a KPI"""
    pass


class KPIUpdate(BaseModel):
    """Schema for updating a KPI"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    value: Optional[float] = None
    target: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None


class KPIResponse(KPIBase):
    """Schema for KPI response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


class KPIListResponse(BaseModel):
    """Schema for KPI list response"""
    kpis: List[KPIResponse]
    total: int

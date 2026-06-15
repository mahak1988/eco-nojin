"""DataPoint Pydantic Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


class DataPointBase(BaseModel):
    """Base data point schema"""
    project_id: int
    module_id: int
    data_type: str = Field(..., min_length=2, max_length=100)
    value: Dict[str, Any]
    unit: Optional[str] = None
    timestamp: datetime


class DataPointCreate(DataPointBase):
    """Schema for creating a data point"""
    extra_data: Optional[Dict[str, Any]] = None


class DataPointUpdate(BaseModel):
    """Schema for updating a data point"""
    value: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(pending|verified|rejected|flagged)$")
    ai_confidence: Optional[float] = Field(None, ge=0, le=100)
    extra_data: Optional[Dict[str, Any]] = None


class DataPointResponse(DataPointBase):
    """Schema for data point response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    status: str
    ai_confidence: Optional[float] = None
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime


class DataPointListResponse(BaseModel):
    """Schema for data point list response"""
    data_points: List[DataPointResponse]
    total: int
    page: int
    per_page: int

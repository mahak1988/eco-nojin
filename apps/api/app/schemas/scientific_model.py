"""
Pydantic schemas for ScientificModel
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ScientificModelBase(BaseModel):
    model_id: str
    name: str
    category: str
    description: Optional[str] = None
    formula: Optional[str] = None
    interpretation_guide: Optional[str] = None
    standards: Optional[str] = None
    is_active: bool = True
    is_featured: bool = False
    default_parameters: Optional[Dict[str, Any]] = None


class ScientificModelCreate(ScientificModelBase):
    pass


class ScientificModelUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    description: Optional[str] = None
    interpretation_guide: Optional[str] = None
    default_parameters: Optional[Dict[str, Any]] = None


class ScientificModelResponse(ScientificModelBase):
    id: int
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScientificModelListResponse(BaseModel):
    models: list[ScientificModelResponse]
    total: int
    active_count: int
    featured_count: int
    categories: Dict[str, int]

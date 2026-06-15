"""Project Pydantic Schemas"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.schemas.user import UserResponse


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    country: str = Field(..., min_length=2, max_length=100)
    region: Optional[str] = None
    type: str = Field(..., pattern="^(water|forest|soil|carbon|mixed)$")
    hectares: float = Field(..., gt=0)
    budget: float = Field(default=0.0, ge=0)


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    manager_id: Optional[int] = None


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(water|forest|soil|carbon|mixed)$")
    status: Optional[str] = Field(None, pattern="^(planning|active|completed|suspended)$")
    hectares: Optional[float] = Field(None, gt=0)
    budget: Optional[float] = Field(None, ge=0)
    spent: Optional[float] = Field(None, ge=0)
    progress: Optional[int] = Field(None, ge=0, le=100)
    manager_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    """Schema for project response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: str
    start_date: Optional[datetime] = None
    spent: float
    progress: int
    manager_id: Optional[int] = None
    created_at: datetime
    manager: Optional[UserResponse] = None


class ProjectListResponse(BaseModel):
    """Schema for project list response"""
    projects: List[ProjectResponse]
    total: int
    page: int
    per_page: int

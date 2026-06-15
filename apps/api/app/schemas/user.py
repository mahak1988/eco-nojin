"""User Pydantic Schemas"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    location: Optional[str] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8, max_length=100)
    role: str = Field(default="farmer", pattern="^(farmer|researcher|investor)$")


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = None
    bio: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    role: str
    status: str
    trust_score: float
    is_verified: bool
    created_at: datetime


class UserInDB(UserResponse):
    """Schema for user in database (includes hashed password)"""
    hashed_password: str

"""Drought Domain Schemas (Pydantic).

این ماژول شامل اسکیماهای اعتبارسنجی برای API خشکسالی است.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DroughtIndexBase(BaseModel):
    name: str = Field(..., description="نام شاخص خشکسالی")
    value: float = Field(..., ge=-5.0, le=5.0)
    timestamp: datetime
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    severity: Optional[str] = None


class DroughtIndexCreate(DroughtIndexBase):
    pass


class DroughtIndexResponse(DroughtIndexBase):
    id: Optional[int] = None
    
    class Config:
        from_attributes = True


class SPEIRequest(BaseModel):
    station_id: str
    start_date: datetime
    end_date: datetime
    scale_months: int = Field(default=3, ge=1, le=48)


class CHIRPSRequest(BaseModel):
    lat: float = Field(..., ge=-50, le=50)
    lon: float = Field(..., ge=-180, le=180)
    start_date: datetime
    end_date: datetime

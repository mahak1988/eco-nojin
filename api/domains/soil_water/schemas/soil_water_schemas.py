"""Soil & Water Domain Schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class SoilAnalysisRequest(BaseModel):
    location_lat: float = Field(..., ge=-90, le=90)
    location_lon: float = Field(..., ge=-180, le=180)
    soil_type: str
    organic_matter_percent: float = Field(..., ge=0, le=100)
    moisture_content: float = Field(..., ge=0, le=100)
    ph_level: float = Field(..., ge=0, le=14)


class ErosionRiskResponse(BaseModel):
    location_lat: float
    location_lon: float
    risk_level: str
    rusle_value: float
    contributing_factors: List[str]
    recommendation: str

from datetime import datetime
from typing import Optional, Literal, List

from pydantic import BaseModel, Field


ErosionRiskLiteral = Literal["very_low", "low", "moderate", "high", "severe"]


class RUSLEFactorsBase(BaseModel):
    R: float = Field(gt=0, description="Rainfall-runoff erosivity factor")
    K: float = Field(gt=0, description="Soil erodibility factor")
    LS: float = Field(gt=0, description="Slope length & steepness factor")
    C: float = Field(gt=0, le=1, description="Cover-management factor (0-1)")
    P: float = Field(gt=0, le=1, description="Support practice factor (0-1)")


class SoilErosionBase(BaseModel):
    location_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


class SoilErosionCreate(RUSLEFactorsBase, SoilErosionBase):
    farmer_id: Optional[int] = Field(default=None)


class SoilErosionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    location_id: Optional[str] = None


class SoilErosionDB(SoilErosionBase, RUSLEFactorsBase):
    id: int
    farmer_id: Optional[int] = None

    annual_soil_loss: float
    risk_class: ErosionRiskLiteral

    meta: Optional[dict] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SoilErosionList(BaseModel):
    total: int
    items: List[SoilErosionDB]
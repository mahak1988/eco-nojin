from datetime import datetime
from pydantic import BaseModel, Field


class FarmerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str | None = None
    phone: str | None = None
    farm_location: str | None = None
    farm_size_hectares: float | None = Field(default=None, ge=0)


class FarmerCreate(FarmerBase):
    pass


class FarmerUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    farm_location: str | None = None
    farm_size_hectares: float | None = Field(default=None, ge=0)


class FarmerResponse(FarmerBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class FarmerListResponse(BaseModel):
    total: int
    farmers: list[FarmerResponse]

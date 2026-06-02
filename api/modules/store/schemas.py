from datetime import datetime
from pydantic import BaseModel, Field


class StoreItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    price: float = Field(ge=0, default=0)
    currency: str = "IRR"
    status: str = "active"
    stock: int = Field(ge=0, default=0)


class StoreItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, ge=0)
    status: str | None = None
    stock: int | None = Field(default=None, ge=0)


class StoreItemResponse(StoreItemCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class StoreListResponse(BaseModel):
    items: list[StoreItemResponse]
    total: int

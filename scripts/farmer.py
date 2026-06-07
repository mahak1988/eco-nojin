"""
Farmer Router - مسیرهای API برای ماژول کشاورز
Endpoint های مدیریت کشاورزان و فعالیت‌های کشاورزی
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

# افزودن مسیر پروژه به sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from scripts.core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger(__name__)

router = APIRouter(
    prefix="/farmers", tags=["farmers"], responses={404: {"description": "Not found"}}
)


# ============================================================================
# Pydantic Models
# ============================================================================


class FarmerBase(BaseModel):
    """مدل پایه کشاورز"""

    name: str = Field(..., min_length=2, max_length=100, description="نام کشاورز")
    email: Optional[str] = Field(None, description="ایمیل")
    phone: Optional[str] = Field(None, description="شماره تماس")
    farm_location: Optional[str] = Field(None, description="موقعیت مزرعه")
    farm_size_hectares: Optional[float] = Field(None, ge=0, description="مساحت مزرعه")


class FarmerCreate(FarmerBase):
    """مدل ایجاد کشاورز"""

    pass


class FarmerUpdate(BaseModel):
    """مدل به‌روزرسانی کشاورز"""

    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    farm_location: Optional[str] = None
    farm_size_hectares: Optional[float] = None


class FarmerResponse(FarmerBase):
    """مدل پاسخ کشاورز"""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FarmerListResponse(BaseModel):
    """مدل پاسخ لیست کشاورزان"""

    total: int
    farmers: List[FarmerResponse]


# ============================================================================
# Endpoints
# ============================================================================


@router.get("/", response_model=FarmerListResponse)
async def list_farmers(skip: int = 0, limit: int = 100):
    """
    دریافت لیست کشاورزان
    """
    logger.info(f"list_farmers | skip={skip} | limit={limit}")

    # TODO: اتصال به دیتابیس
    # farmers = db.query(Farmer).offset(skip).limit(limit).all()

    return {"total": 0, "farmers": []}


@router.post("/", response_model=FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(farmer: FarmerCreate):
    """
    ایجاد کشاورز جدید
    """
    logger.info(f"create_farmer | name={farmer.name}")

    # TODO: ذخیره در دیتابیس
    # db_farmer = Farmer(**farmer.dict())
    # db.add(db_farmer)
    # db.commit()

    # پاسخ موقت
    return {
        "id": 1,
        "name": farmer.name,
        "email": farmer.email,
        "phone": farmer.phone,
        "farm_location": farmer.farm_location,
        "farm_size_hectares": farmer.farm_size_hectares,
        "created_at": datetime.now(),
        "updated_at": None,
    }


@router.get("/{farmer_id}", response_model=FarmerResponse)
async def get_farmer(farmer_id: int):
    """
    دریافت اطلاعات یک کشاورز
    """
    logger.info(f"get_farmer | farmer_id={farmer_id}")

    # TODO: دریافت از دیتابیس
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Farmer {farmer_id} not found"
    )


@router.put("/{farmer_id}", response_model=FarmerResponse)
async def update_farmer(farmer_id: int, farmer: FarmerUpdate):
    """
    به‌روزرسانی اطلاعات کشاورز
    """
    logger.info(f"update_farmer | farmer_id={farmer_id}")

    # TODO: به‌روزرسانی در دیتابیس
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Farmer {farmer_id} not found"
    )


@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(farmer_id: int):
    """
    حذف کشاورز
    """
    logger.info(f"delete_farmer | farmer_id={farmer_id}")

    # TODO: حذف از دیتابیس
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail=f"Farmer {farmer_id} not found"
    )


@router.get("/{farmer_id}/activities")
async def get_farmer_activities(farmer_id: int):
    """
    دریافت فعالیت‌های کشاورز
    """
    logger.info(f"get_farmer_activities | farmer_id={farmer_id}")

    return {"farmer_id": farmer_id, "activities": []}

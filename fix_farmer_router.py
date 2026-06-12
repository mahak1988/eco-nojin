#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix farmer router DELETE endpoint
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
API_DIR = BASE_DIR / "api"


def fix_farmer_router():
    print("🔧 اصلاح api/modules/farmer/router.py...")
    
    content = '''"""
Farmer Router - مدیریت کشاورزان
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.deps import require_write_auth
from api.modules.farmer import crud, schemas

router = APIRouter(tags=["Farmers"])


@router.get("/", response_model=schemas.FarmerListResponse)
async def list_farmers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """لیست تمام کشاورزان"""
    farmers, total = await crud.list_farmers(db, skip=skip, limit=limit)
    return schemas.FarmerListResponse(total=total, farmers=farmers)


@router.post("/", response_model=schemas.FarmerResponse, status_code=status.HTTP_201_CREATED)
async def create_farmer(
    farmer: schemas.FarmerCreate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    """ایجاد کشاورز جدید"""
    return await crud.create_farmer(db, farmer)


@router.get("/{farmer_id}", response_model=schemas.FarmerResponse)
async def get_farmer(farmer_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت اطلاعات یک کشاورز"""
    farmer = await crud.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return farmer


@router.put("/{farmer_id}", response_model=schemas.FarmerResponse)
async def update_farmer(
    farmer_id: int,
    farmer: schemas.FarmerUpdate,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    """به‌روزرسانی اطلاعات کشاورز"""
    updated = await crud.update_farmer(db, farmer_id, farmer)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return updated


# 🔴 اصلاح: حذف response_model از DELETE
@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(
    farmer_id: int,
    db: AsyncSession = Depends(get_db),
    _user: str = Depends(require_write_auth),
):
    """حذف کشاورز"""
    if not await crud.delete_farmer(db, farmer_id):
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return None


@router.get("/{farmer_id}/activities")
async def get_farmer_activities(farmer_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت فعالیت‌های کشاورز"""
    farmer = await crud.get_farmer(db, farmer_id)
    if not farmer:
        raise HTTPException(status_code=404, detail=f"Farmer {farmer_id} not found")
    return {"farmer_id": farmer_id, "activities": []}
'''
    
    path = API_DIR / "modules" / "farmer" / "router.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ farmer/router.py اصلاح شد\n")


def main():
    print("=" * 70)
    print("🔧 Fixing Farmer Router")
    print("=" * 70)
    print()
    
    try:
        fix_farmer_router()
        
        print("=" * 70)
        print("✅ فایل با موفقیت اصلاح شد!")
        print("=" * 70)
        print()
        print("🚀 گام بعدی:")
        print("  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
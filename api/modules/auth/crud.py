"""
Authentication CRUD operations
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth import models, schemas


async def upsert_user(db: AsyncSession, req: schemas.LoginRequest) -> models.UserAccount:
    """ایجاد یا به‌روزرسانی کاربر"""
    # جستجوی کاربر با farmer_id
    result = await db.execute(
        select(models.UserAccount).where(models.UserAccount.farmer_id == req.fid)
    )
    user = result.scalar_one_or_none()
    
    if user:
        # به‌روزرسانی کاربر موجود
        user.phone = req.phone
        if req.name:
            user.name = req.name
    else:
        # ایجاد کاربر جدید
        user = models.UserAccount(
            farmer_id=req.fid,
            phone=req.phone,
            name=req.name or "",
        )
        db.add(user)
    
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_farmer_id(db: AsyncSession, farmer_id: str) -> models.UserAccount | None:
    """دریافت کاربر با farmer_id"""
    result = await db.execute(
        select(models.UserAccount).where(models.UserAccount.farmer_id == farmer_id)
    )
    return result.scalar_one_or_none()


async def get_user_by_phone(db: AsyncSession, phone: str) -> models.UserAccount | None:
    """دریافت کاربر با شماره تلفن"""
    result = await db.execute(
        select(models.UserAccount).where(models.UserAccount.phone == phone)
    )
    return result.scalar_one_or_none()


async def link_wallet(db: AsyncSession, farmer_id: str, wallet_address: str) -> models.UserAccount | None:
    """اتصال آدرس کیف پول به کاربر"""
    user = await get_user_by_farmer_id(db, farmer_id)
    if not user:
        return None
    
    user.wallet_address = wallet_address
    await db.commit()
    await db.refresh(user)
    return user

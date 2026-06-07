from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.modules.auth.models import UserAccount
from api.modules.auth.schemas import LoginRequest


async def get_user_by_farmer_id(db: AsyncSession, farmer_id: str) -> UserAccount | None:
    result = await db.execute(select(UserAccount).where(UserAccount.farmer_id == farmer_id))
    return result.scalar_one_or_none()


async def upsert_user(db: AsyncSession, req: LoginRequest) -> UserAccount:
    user = await get_user_by_farmer_id(db, req.fid)
    if user:
        user.phone = req.phone
        if req.name:
            user.name = req.name
    else:
        user = UserAccount(farmer_id=req.fid, phone=req.phone, name=req.name or req.fid)
        db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def link_wallet(db: AsyncSession, farmer_id: str, wallet: str) -> UserAccount | None:
    user = await get_user_by_farmer_id(db, farmer_id)
    if not user:
        return None
    user.wallet_address = wallet
    await db.commit()
    await db.refresh(user)
    return user

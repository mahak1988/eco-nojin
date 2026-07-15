from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.shared_core.database.repository import BaseRepository
from apps.users.models import User
from typing import Optional

class UserRepository(BaseRepository[User]):
    """
    Repository اختصاصی برای مدل User.
    متدهای اختصاصی برای عملیات مرتبط با کاربران.
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        دریافت کاربر بر اساس ایمیل.
        
        Args:
            email: ایمیل کاربر
        
        Returns:
            شیء User یا None
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalars().first()
    
    async def get_active_users(self, limit: int = 100, offset: int = 0):
        """دریافت کاربران فعال."""
        return await self.get_multi(
            filter_by={"is_active": True},
            limit=limit,
            offset=offset
        )
    
    async def get_superuser_count(self) -> int:
        """شمارش تعداد superuserها."""
        return await self.count(filter_by={"is_superuser": True})
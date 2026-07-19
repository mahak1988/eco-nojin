"""
User Service - Business Logic
=============================
Refactored to use centralized security and configuration.
Uses Argon2/Bcrypt from shared_core.security with settings from config.
"""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from apps.shared_core.config import settings
from apps.users.models import User
from apps.users.repository import UserRepository
from apps.users.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)

# Use centralized configuration from shared_core
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


class UserService:
    """
    سرویس مدیریت کاربران.
    این کلاس مسئول تمام عملیات مرتبط با کاربران است.
    """
    
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
    
    async def register_user(self, user_in: UserCreate) -> User:
        """
        ثبت‌نام کاربر جدید.
        
        Args:
            user_in: اطلاعات کاربر
        
        Returns:
            کاربر ایجاد شده
        
        Raises:
            ValueError: اگر ایمیل تکراری باشد
        """
        # بررسی تکراری نبودن ایمیل
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise ValueError("ایمیل قبلاً ثبت شده است")
        
        # hash کردن پسورد با Argon2/Bcrypt
        hashed_password = get_password_hash(user_in.password)
        
        # ایجاد کاربر
        user_data = {
            "email": user_in.email,
            "hashed_password": hashed_password,
            "full_name": user_in.full_name,
            "is_active": True,
            "is_superuser": False
        }
        
        user = await self.repo.create(user_data)
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        احراز هویت کاربر.
        
        Args:
            email: ایمیل کاربر
            password: پسورد plaintext
        
        Returns:
            کاربر در صورت موفقیت، None در صورت شکست
        """
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def create_access_token_for_user(self, user: User) -> str:
        """
        ساخت توکن دسترسی برای کاربر.
        
        Args:
            user: شیء کاربر
        
        Returns:
            توکن JWT
        """
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return access_token
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """دریافت کاربر بر اساس شناسه."""
        return await self.repo.get_by_id(user_id)
    
    async def update_user(self, user: User, user_in: UserUpdate) -> User:
        """
        بروزرسانی اطلاعات کاربر.
        
        Args:
            user: کاربر فعلی
            user_in: اطلاعات جدید
        
        Returns:
            کاربر بروزرسانی شده
        """
        update_data = user_in.model_dump(exclude_unset=True)
        
        # اگر پسورد تغییر کرده، hash کن
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        updated_user = await self.repo.update(user, update_data)
        return updated_user
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        غیرفعال کردن کاربر (Soft Delete).
        
        Args:
            user_id: شناسه کاربر
        
        Returns:
            True در صورت موفقیت
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            return False
        
        await self.repo.update(user, {"is_active": False})
        return True
"""
User Service - Business Logic
=============================
Refactored to use centralized security and configuration.
Uses Argon2/Bcrypt from shared_core.security with settings from config.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from apps.users.models import User
from apps.users.repository import UserRepository
from apps.users.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)

# Use centralized configuration from shared_core
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def decode_access_token(token: str) -> dict:
    """Decode and verify a JWT access token (wrapper around decode_token)."""
    return decode_token(token)


class UserService:
    """
    سرویس مدیریت کاربران.
    این کلاس مسئول تمام عملیات مرتبط با کاربران است.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Handle __init__ (session)."""
        self.repo = UserRepository(session)

    async def register_user(self, user_in: UserCreate) -> User:
        """
        ثبت‌نام کاربر جدید.

        Args:
            user_in: اطلاعات کاربر برای ثبت‌نام

        Returns:
            User: شیء کاربر ایجاد شده

        Raises:
            ValueError: اگر ایمیل تکراری باشد
        """
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise ValueError("Email already registered")
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            phone=user_in.phone,
            organization=user_in.organization,
            role=user_in.role,
        )
        return await self.repo.create(db_user)

    async def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user by email and password."""
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_access_token_for_user(self, user: User) -> str:
        """Create an access token for the authenticated user."""
        return create_access_token(subject=user.id)

    async def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieve a user by their ID."""
        return await self.repo.get_by_id(user_id)

    async def update_user(self, user_id: int, user_in: UserUpdate) -> User | None:
        """Update user details."""
        update_data = user_in.model_dump(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        return await self.repo.update(user_id, update_data)

    async def update_user_permissions(self, user_id: int, permissions: list[str]) -> User | None:
        """
        Update permissions for a user. This is a placeholder for the actual permission logic
        which might involve a separate Permission table/model or a role-based lookup.
        For this example, we'll just log the action and return the user if found.
        """
        logger.info(f"Updating permissions for user {user_id} to {permissions}.")
        # In a real implementation, you would update a permissions table or a roles table
        # based on the 'permissions' list provided.
        # This is a stub implementation that just retrieves and returns the user.
        user = await self.repo.get_by_id(user_id)
        if user:
            # Example: Update a 'permissions' field on the user object if it existed
            # user.permissions = permissions
            # await self.repo.update(user_id, {"permissions": permissions})
            pass
        return user

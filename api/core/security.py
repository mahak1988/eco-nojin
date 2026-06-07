# api/core/security.py (یا dependencies.py)
"""
ماژول امنیت و احراز هویت (Enterprise-Ready)
نسخه 2.0 - شامل JWT، دریافت کاربر و RBAC
"""
from datetime import datetime, timedelta, timezone
from typing import List, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.database import get_db

# 🔴 فرض بر این است که مدل User در این مسیر قرار دارد. مسیر را در صورت نیاز اصلاح کنید:
from api.modules.library.models import User, UserRole

security_scheme = HTTPBearer(auto_error=False)


# ============================================================
# 1. توابع مدیریت توکن (Token Management)
# ============================================================
def create_access_token(subject: str | int, expires_delta: Optional[timedelta] = None) -> str:
    """ساخت توکن دسترسی (عمر کوتاه - پیش‌فرض ۳۰ دقیقه)"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # 🔴 اصلاح امنیتی: عمر توکن به جای روز، ۳۰ دقیقه است!
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> str:
    """رمزگشایی توکن (بدون وابستگی به FastAPI HTTPException)"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "type"]},
        )
        if payload.get("type") != "access":
            raise ValueError("Invalid token type")
        return str(payload["sub"])
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.PyJWTError:
        raise ValueError("Invalid token signature or format")


# ============================================================
# 2. Dependency های احراز هویت (Authentication Dependencies)
# ============================================================
async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> str:
    """استخراج ID کاربر از توکن (لایه اول اعتبارسنجی)"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="عدم ارسال توکن احراز هویت",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return decode_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    دریافت کامل آبجکت کاربر از دیتابیس.
    این تابع در اندپوینت‌ها استفاده می‌شود تا نیاز به کوئری مجدد نباشد.
    """
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر مرتبط با این توکن یافت نشد (احتمالاً حذف شده است)",
        )

    if not user.is_verified:  # اگر فیلد is_verified در مدل User دارید
        raise HTTPException(status_code=403, detail="حساب کاربری شما هنوز تایید نشده است")

    return user


# ============================================================
# 3. سیستم کنترل دسترسی مبتنی بر نقش (RBAC)
# ============================================================
class RoleChecker:
    """کلاسی برای بررسی نقش کاربر (قابل استفاده به عنوان Dependency)"""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"شما دسترسی لازم برای این عملیات را ندارید. نقش‌های مجاز: {[r.value for r in self.allowed_roles]}",
            )
        return current_user


# 🔴 تعریف آماده برای استفاده در اندپوینت‌ها:
require_reviewer_or_admin = RoleChecker([UserRole.REVIEWER, UserRole.ADMIN])
require_admin_only = RoleChecker([UserRole.ADMIN])

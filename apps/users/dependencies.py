from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.users.service import UserService, decode_access_token
from apps.users.models import User

# ==========================================
# OAuth2 Configuration
# ==========================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")

# ==========================================
# Dependencies
# ==========================================
async def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    """Dependency برای دریافت UserService."""
    return UserService(session)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    Dependency برای دریافت کاربر فعلی از توکن JWT.
    
    این dependency در endpoint هایی استفاده می‌شود که نیاز به احراز هویت دارند.
    
    Raises:
        HTTPException 401: اگر توکن نامعتبر باشد
        HTTPException 404: اگر کاربر یافت نشود
        HTTPException 400: اگر کاربر غیرفعال باشد
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="توکن احراز هویت نامعتبر است",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # رمزگشایی توکن
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # دریافت کاربر از دیتابیس
    try:
        user = await user_service.get_user_by_id(int(user_id))
    except (ValueError, TypeError):
        raise credentials_exception
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="کاربر غیرفعال است"
        )
    
    return user

async def get_current_active_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency برای دریافت superuser فعلی.
    
    Raises:
        HTTPException 403: اگر کاربر superuser نباشد
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="دسترسی غیرمجاز"
        )
    return current_user
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.users.schemas import (
    UserCreate, 
    UserResponse, 
    UserUpdate, 
    LoginRequest, 
    Token
)
from apps.users.service import UserService
from apps.users.dependencies import get_user_service, get_current_user, get_current_active_superuser
from apps.users.models import User

router = APIRouter(prefix="/users", tags=["Users"])

# ==========================================
# Public Endpoints
# ==========================================
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """
    ثبت‌نام کاربر جدید.
    
    - **email**: ایمیل معتبر
    - **password**: حداقل ۸ کاراکتر
    - **full_name**: نام کامل (اختیاری)
    """
    try:
        user = await user_service.register_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """
    ورود کاربر و دریافت توکن JWT.
    
    - **email**: ایمیل کاربر
    - **password**: پسورد
    """
    user = await user_service.authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ایمیل یا پسورد اشتباه است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = await user_service.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

# ==========================================
# Protected Endpoints (نیاز به احراز هویت)
# ==========================================
@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    دریافت اطلاعات کاربر فعلی.
    
    این endpoint نیاز به توکن JWT در هدر Authorization دارد.
    """
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    بروزرسانی اطلاعات کاربر فعلی.
    """
    updated_user = await user_service.update_user(current_user, user_in)
    return updated_user

# ==========================================
# Admin Endpoints (نیاز به Superuser)
# ==========================================
@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    دریافت لیست کاربران (فقط برای Superuser).
    """
    users = await user_service.repo.get_multi(limit=limit, offset=skip)
    return users

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    current_user: User = Depends(get_current_active_superuser),
    user_service: UserService = Depends(get_user_service)
):
    """
    غیرفعال کردن کاربر (فقط برای Superuser).
    """
    success = await user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد"
        )
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# ==========================================
# Base Schemas
# ==========================================
class UserBase(BaseModel):
    """اسکیمای پایه کاربر (فیلدهای مشترک)."""
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=255)

# ==========================================
# Create & Update Schemas
# ==========================================
class UserCreate(UserBase):
    """اسکیمای ثبت‌نام کاربر."""
    password: str = Field(..., min_length=8, max_length=128)

class UserUpdate(BaseModel):
    """اسکیمای بروزرسانی پروفایل."""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=128)

# ==========================================
# Response Schemas
# ==========================================
class UserResponse(UserBase):
    """اسکیمای پاسخ (بدون پسورد)."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

class UserInDB(UserResponse):
    """اسکیمای داخلی (با پسورد hash شده)."""
    hashed_password: str

# ==========================================
# Auth Schemas
# ==========================================
class Token(BaseModel):
    """اسکیمای توکن JWT."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """داده‌های داخل توکن."""
    user_id: Optional[int] = None
    email: Optional[EmailStr] = None

class LoginRequest(BaseModel):
    """اسکیمای درخواست ورود."""
    email: EmailStr
    password: str
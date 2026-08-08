"""schemas module."""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ==========================================
# Base Schemas
# ==========================================
class UserBase(BaseModel):
    """اسکیمای پایه کاربر (فیلدهای مشترک)."""

    email: EmailStr
    full_name: str | None = Field(None, max_length=255)


# ==========================================
# Create & Update Schemas
# ==========================================
class UserCreate(UserBase):
    """اسکیمای ثبت‌نام کاربر."""

    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """اسکیمای بروزرسانی پروفایل."""

    full_name: str | None = Field(None, max_length=255)
    email: EmailStr | None = None
    password: str | None = Field(None, min_length=8, max_length=128)


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

    user_id: int | None = None
    email: EmailStr | None = None


class LoginRequest(BaseModel):
    """اسکیمای درخواست ورود."""

    email: EmailStr
    password: str

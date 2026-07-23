from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
import re

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
    password: str = Field(..., min_length=12, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength: min 12 chars, at least one uppercase, one lowercase, one digit."""
        if len(v) < 12:
            raise ValueError('رمز عبور باید حداقل ۱۲ کاراکتر باشد')
        if not re.search(r'[A-Z]', v):
            raise ValueError('رمز عبور باید حداقل یک حرف بزرگ داشته باشد')
        if not re.search(r'[a-z]', v):
            raise ValueError('رمز عبور باید حداقل یک حرف کوچک داشته باشد')
        if not re.search(r'\d', v):
            raise ValueError('رمز عبور باید حداقل یک عدد داشته باشد')
        return v

class UserUpdate(BaseModel):
    """اسکیمای بروزرسانی پروفایل."""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=12, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is None:
            return v
        if len(v) < 12:
            raise ValueError('رمز عبور باید حداقل ۱۲ کاراکتر باشد')
        if not re.search(r'[A-Z]', v):
            raise ValueError('رمز عبور باید حداقل یک حرف بزرگ داشته باشد')
        if not re.search(r'[a-z]', v):
            raise ValueError('رمز عبور باید حداقل یک حرف کوچک داشته باشد')
        if not re.search(r'\d', v):
            raise ValueError('رمز عبور باید حداقل یک عدد داشته باشد')
        return v

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
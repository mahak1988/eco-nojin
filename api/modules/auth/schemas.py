"""
Authentication Schemas - Pydantic models
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ============================================================================
# Login & Register
# ============================================================================

class LoginRequest(BaseModel):
    """درخواست ورود"""
    fid: str = Field(..., min_length=3, max_length=32, description="شناسه کاربری")
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$", description="شماره تلفن")
    name: str = Field(default="", max_length=100, description="نام کاربر")


class TokenResponse(BaseModel):
    """پاسخ ورود - شامل توکن"""
    access_token: str
    token_type: str = "bearer"
    farmer_id: str


# ============================================================================
# OTP
# ============================================================================

class OtpRequest(BaseModel):
    """درخواست ارسال کد OTP"""
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    fid: str = Field(default="", max_length=32)


class OtpRequestResponse(BaseModel):
    """پاسخ درخواست OTP"""
    sent: bool
    phone: str
    dev_code: Optional[str] = None
    expires_in: int = 300
    message: Optional[str] = None


class OtpVerify(BaseModel):
    """تأیید کد OTP"""
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    code: str = Field(..., min_length=4, max_length=8)
    fid: str = Field(..., min_length=3, max_length=32)
    name: str = Field(default="", max_length=100)


# ============================================================================
# Profile
# ============================================================================

class ProfileResponse(BaseModel):
    """پاسخ پروفایل کاربر"""
    fid: str
    name: str
    phone: str
    registered_at: datetime
    wallet_address: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# 🔴 Wallet - کلاس‌های جدید
# ============================================================================

class WalletLinkRequest(BaseModel):
    """درخواست اتصال کیف پول"""
    wallet_address: str = Field(..., min_length=10, max_length=128)


class WalletLinkResponse(BaseModel):
    """پاسخ اتصال کیف پول"""
    success: bool
    wallet_address: str

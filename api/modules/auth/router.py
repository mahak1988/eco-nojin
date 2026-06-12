"""
Authentication Router - OTP-based login
"""
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.security import create_access_token, get_current_user_id
from api.modules.auth import crud, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OTP Store (in-memory for development)
_otp_store: dict[str, dict] = {}


def generate_otp(phone: str) -> str:
    """تولید کد OTP 6 رقمی"""
    code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    _otp_store[phone] = {
        "code": code,
        "expires": datetime.now() + timedelta(minutes=5),
        "attempts": 0,
    }
    return code


def verify_otp(phone: str, code: str) -> bool:
    """تأیید کد OTP"""
    stored = _otp_store.get(phone)
    if not stored:
        return False
    
    if datetime.now() > stored["expires"]:
        del _otp_store[phone]
        return False
    
    if stored["attempts"] >= 5:
        del _otp_store[phone]
        return False
    
    if stored["code"] != code:
        stored["attempts"] += 1
        return False
    
    del _otp_store[phone]
    return True


@router.post("/otp/request", response_model=schemas.OtpRequestResponse)
async def request_otp(req: schemas.OtpRequest):
    """درخواست کد OTP"""
    from api.core.config import settings
    
    code = generate_otp(req.phone)
    
    # در حالت توسعه، کد را برگردان
    if settings.DEBUG or settings.OTP_DEV_MODE:
        return schemas.OtpRequestResponse(
            sent=True,
            phone=req.phone,
            dev_code=code,
            expires_in=300,
            message="کد OTP تولید شد (حالت توسعه)"
        )
    
    # TODO: ارسال SMS واقعی
    return schemas.OtpRequestResponse(
        sent=True,
        phone=req.phone,
        expires_in=300,
        message="کد OTP ارسال شد"
    )


@router.post("/otp/verify", response_model=schemas.TokenResponse)
async def verify_otp_login(req: schemas.OtpVerify, db: AsyncSession = Depends(get_db)):
    """تأیید کد OTP و ورود"""
    if not verify_otp(req.phone, req.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="کد وارد شده نامعتبر یا منقضی شده است",
        )
    
    # Upsert کاربر
    login_req = schemas.LoginRequest(fid=req.fid, phone=req.phone, name=req.name)
    user = await crud.upsert_user(db, login_req)
    
    # ساخت توکن
    token = create_access_token(subject=user.farmer_id)
    
    return schemas.TokenResponse(
        access_token=token,
        token_type="bearer",
        farmer_id=user.farmer_id,
    )


@router.post("/login", response_model=schemas.TokenResponse)
async def login(req: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    """ورود ساده (فقط برای توسعه)"""
    user = await crud.upsert_user(db, req)
    token = create_access_token(subject=user.farmer_id)
    return schemas.TokenResponse(
        access_token=token,
        token_type="bearer",
        farmer_id=user.farmer_id,
    )


@router.get("/profile", response_model=schemas.ProfileResponse)
async def get_profile(
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """دریافت پروفایل کاربر"""
    user = await crud.get_user_by_farmer_id(db, farmer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد",
        )
    
    return schemas.ProfileResponse(
        fid=user.farmer_id,
        name=user.name or user.farmer_id,
        phone=user.phone,
        registered_at=user.created_at,
        wallet_address=user.wallet_address,
    )


@router.post("/profile/wallet", response_model=schemas.WalletLinkResponse)
async def link_wallet(
    req: schemas.WalletLinkRequest,
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """اتصال آدرس کیف پول"""
    user = await crud.link_wallet(db, farmer_id, req.wallet_address)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد",
        )
    return schemas.WalletLinkResponse(
        success=True,
        wallet_address=user.wallet_address,
    )

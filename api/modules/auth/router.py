# api/modules/auth/router.py
"""
ماژول احراز هویت و مدیریت کاربر (OTP-based)
نسخه 2.0 - بهینه‌سازی کوئری‌ها و اصلاح ساختار درخواست‌ها
"""
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.core.database import get_db
from api.core.security import create_access_token, get_current_user_id
from api.modules.auth import crud, schemas

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/otp/request", response_model=schemas.OtpRequestResponse)
async def request_otp(req: schemas.OtpRequest):
    # ایمپورت داخلی برای جلوگیری از Circular Import (اگر نیاز است)
    from api.services.sms import send_otp_sms

    code = generate_otp(req.phone)
    sent = await send_otp_sms(req.phone, code)

    if not sent and not settings.OTP_DEV_MODE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="سرویس پیامک در دسترس نیست. پیکربندی Kavenegar یا Twilio را بررسی کنید.",
        )

    payload = {"sent": True, "phone": req.phone, "expires_in": 300}
    if settings.DEBUG or settings.OTP_DEV_MODE:
        payload["dev_code"] = code  # فقط در محیط توسعه ارسال شود

    return payload


@router.post("/otp/verify", response_model=schemas.TokenResponse)
async def verify_otp_login(req: schemas.OtpVerify, db: AsyncSession = Depends(get_db)):
    if not verify_otp(req.phone, req.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="کد وارد شده نامعتبر یا منقضی شده است"
        )

    # Upsert کاربر (ایجاد یا به‌روزرسانی)
    login_req = schemas.LoginRequest(fid=req.fid, phone=req.phone, name=req.name)
    user = await crud.upsert_user(db, login_req)

    # ساخت توکن با farmer_id به عنوان subject
    token = create_access_token(subject=user.farmer_id)

    return schemas.TokenResponse(access_token=token, farmer_id=user.farmer_id)


@router.post("/login", response_model=schemas.TokenResponse)
async def login(req: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    ⚠️ هشدار امنیتی: این اندپوینت بدون بررسی رمز عبور یا OTP، کاربر را upsert می‌کند.
    اگر این رفتار عمدی نیست، باید فیلد password به Schema اضافه شده و در CRUD بررسی شود.
    """
    user = await crud.upsert_user(db, req)
    token = create_access_token(subject=user.farmer_id)
    return schemas.TokenResponse(access_token=token, farmer_id=user.farmer_id)


@router.get("/profile", response_model=schemas.ProfileResponse)
async def get_profile(
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """دریافت پروفایل کاربر با استفاده از farmer_id استخراج شده از توکن"""
    user = await crud.get_user_by_farmer_id(db, farmer_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="کاربر با این شناسه یافت نشد"
        )

    return schemas.ProfileResponse(
        fid=user.farmer_id,
        name=user.name or user.farmer_id,
        phone=user.phone,
        registered_at=user.created_at,
        wallet_address=user.wallet_address,
    )


# 🔴 اصلاح: استفاده از Pydantic Schema به جای str خام
@router.post("/profile/wallet", response_model=schemas.WalletResponse)
async def link_wallet(
    req: schemas.WalletLinkRequest,  # اکنون به صورت Body ارسال می‌شود
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """اتصال آدرس کیف پول به حساب کاربری"""
    user = await crud.link_wallet(db, farmer_id, req.wallet_address)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="کاربر یافت نشد")
    return {"success": True, "wallet_address": user.wallet_address}

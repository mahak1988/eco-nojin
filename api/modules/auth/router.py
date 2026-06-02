from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.core.database import get_db
from api.core.security import create_access_token, get_current_user_id
from api.core.config import settings
from api.modules.auth import crud, schemas
from api.modules.auth.otp_store import generate_otp, verify_otp

router = APIRouter(tags=["Auth"])


@router.post("/otp/request")
async def request_otp(req: schemas.OtpRequest):
    from api.services.sms import send_otp_sms

    code = generate_otp(req.phone)
    sent = await send_otp_sms(req.phone, code)
    if not sent and not settings.OTP_DEV_MODE:
        raise HTTPException(
            status_code=503,
            detail="SMS service unavailable. Configure Kavenegar or Twilio.",
        )
    payload = {"sent": True, "phone": req.phone, "expires_in": 300}
    if settings.DEBUG or settings.OTP_DEV_MODE:
        payload["dev_code"] = code
    return payload


@router.post("/otp/verify", response_model=schemas.TokenResponse)
async def verify_otp_login(req: schemas.OtpVerify, db: AsyncSession = Depends(get_db)):
    if not verify_otp(req.phone, req.code):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    login_req = schemas.LoginRequest(fid=req.fid, phone=req.phone, name=req.name)
    user = await crud.upsert_user(db, login_req)
    token = create_access_token(user.farmer_id)
    return schemas.TokenResponse(access_token=token, farmer_id=user.farmer_id)


@router.post("/login", response_model=schemas.TokenResponse)
async def login(req: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.upsert_user(db, req)
    token = create_access_token(user.farmer_id)
    return schemas.TokenResponse(access_token=token, farmer_id=user.farmer_id)


@router.get("/profile", response_model=schemas.ProfileResponse)
async def get_profile(
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await crud.get_user_by_farmer_id(db, farmer_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.ProfileResponse(
        fid=user.farmer_id,
        name=user.name or user.farmer_id,
        phone=user.phone,
        registered_at=user.created_at,
        wallet_address=user.wallet_address,
    )


@router.post("/profile/wallet")
async def link_wallet(
    wallet: str,
    farmer_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    user = await crud.link_wallet(db, farmer_id, wallet)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True, "wallet_address": user.wallet_address}

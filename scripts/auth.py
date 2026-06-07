# scripts/api/routers/auth.py
import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET", "dev-secret-change-in-prod")
ALGORITHM = "HS256"


class LoginReq(BaseModel):
    fid: str = Field(..., min_length=3, max_length=20)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")


class TokenRes(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmer_id: str


class ProfileRes(BaseModel):
    fid: str
    name: str
    phone: str
    registered_at: str
    wallet_address: str | None = None


def create_token(fid: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=7)
    payload = {"sub": fid, "exp": expire, "type": "access"}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/login", response_model=TokenRes)
async def login(req: LoginReq):
    # In production: verify phone via OTP, check DB
    # For demo: accept any valid-format request
    if len(req.fid) < 3:
        raise HTTPException(status_code=400, detail="Invalid farmer ID")
    token = create_token(req.fid)
    return TokenRes(access_token=token, farmer_id=req.fid)


@router.get("/profile", response_model=ProfileRes)
async def get_profile(fid: str = Depends(verify_token)):
    # In production: fetch from DB
    return ProfileRes(
        fid=fid,
        name="Demo Farmer",
        phone="+989123456789",
        registered_at=datetime.now(timezone.utc).isoformat(),
        wallet_address=None,
    )


@router.post("/profile/wallet")
async def link_wallet(wallet: str, fid: str = Depends(verify_token)):
    # In production: save to DB with signature verification
    return {"success": True, "message": "Wallet linked"}

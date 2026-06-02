from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    fid: str = Field(..., min_length=3, max_length=32)
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    name: str = Field(default="", max_length=100)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    farmer_id: str


class OtpRequest(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    fid: str = Field(default="", max_length=32)


class OtpVerify(BaseModel):
    phone: str = Field(..., pattern=r"^\+?[0-9]{10,15}$")
    code: str = Field(..., min_length=4, max_length=8)
    fid: str = Field(..., min_length=3, max_length=32)
    name: str = Field(default="", max_length=100)


class ProfileResponse(BaseModel):
    fid: str
    name: str
    phone: str
    registered_at: datetime
    wallet_address: str | None = None

    class Config:
        from_attributes = True

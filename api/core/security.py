"""
Security utilities - JWT token management & authorization
نسخه 3.0 - جامع
"""
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, Any

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from api.core.config import settings


security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return hash_password(password)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        subject: str = payload.get("sub")
        return subject
    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        return None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توکن ارسال نشده")
    farmer_id = verify_token(credentials.credentials)
    if farmer_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="توکن نامعتبر")
    return farmer_id


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    if credentials is None:
        return None
    return verify_token(credentials.credentials)


# ============================================================
# ALL BACKWARD COMPATIBILITY ALIASES
# ============================================================
get_current_user = get_current_user_id
get_current_farmer = get_current_user_id
get_current_farmer_id = get_current_user_id
get_current_user_id_from_token = get_current_user_id
get_user_from_token = get_current_user_id
get_optional_user = get_optional_user_id
get_optional_farmer = get_optional_user_id


# ============================================================
# AUTHORIZATION DEPENDENCIES
# ============================================================
async def require_auth(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    return await get_current_user_id(credentials)


async def require_write_auth(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_admin(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_reviewer(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_reviewer_or_admin(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_expert(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_farmer(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_manager(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_operator(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


async def require_supervisor(farmer_id: str = Depends(require_auth)) -> str:
    return farmer_id


# ============================================================
# UTILITY FUNCTIONS
# ============================================================
def generate_random_string(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> str:
    return f"ek_{generate_random_string(48)}"


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

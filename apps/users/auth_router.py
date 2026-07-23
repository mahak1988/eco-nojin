"""
Eco Nojin - Authentication Router (Final Version with RBAC)
===========================================================
"""
import os
import re
from datetime import datetime, timedelta
from typing import Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, model_validator, field_validator
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db
from apps.users.models import User

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @model_validator(mode='before')
    @classmethod
    def check_email_or_username(cls, values: Any) -> Any:
        if isinstance(values, dict):
            has_email = bool(values.get('email'))
            has_username = bool(values.get('username'))
            
            if not has_email and not has_username:
                raise ValueError("Either email or username must be provided")
            
            if has_username and not has_email and "@" in values['username']:
                values['email'] = values['username']
                
        return values

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "farmer"  # نقش پیش‌فرض
    
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

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str = "user"
    is_active: bool
    is_superuser: bool = False
    created_at: datetime
    updated_at: datetime

class AuthResponse(BaseModel):
    accessToken: str
    refreshToken: str
    user: UserResponse

class RefreshRequest(BaseModel):
    refreshToken: str

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None or payload.get("type") != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(request.password)
    
    user_data = {
        "email": request.email,
        "hashed_password": hashed_pw,
        "full_name": request.full_name,
        "role": request.role,  # <-- نقش از درخواست خوانده می‌شود
        "is_active": True,
        "is_superuser": False
    }

    new_user = User(**user_data)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    user_response = UserResponse(
        id=new_user.id,
        email=new_user.email,
        full_name=getattr(new_user, "full_name", None),
        role=getattr(new_user, "role", "user"),
        is_active=getattr(new_user, "is_active", True),
        is_superuser=getattr(new_user, "is_superuser", False),
        created_at=new_user.created_at,
        updated_at=new_user.updated_at
    )
    
    return {
        "accessToken": create_access_token({"sub": new_user.email}),
        "refreshToken": create_refresh_token({"sub": new_user.email}),
        "user": user_response
    }

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    identifier = request.email or request.username
    
    if not identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid login credentials"
        )

    query = select(User).where(User.email == identifier)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    stored_password = getattr(user, "hashed_password", None) or getattr(user, "password", None)
    
    if not user or not verify_password(request.password, stored_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=getattr(user, "full_name", None),
        role=getattr(user, "role", "user"),
        is_active=getattr(user, "is_active", True),
        is_superuser=getattr(user, "is_superuser", False),
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return {
        "accessToken": create_access_token({"sub": user.email}),
        "refreshToken": create_refresh_token({"sub": user.email}),
        "user": user_response
    }

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=getattr(current_user, "full_name", None),
        role=getattr(current_user, "role", "user"),
        is_active=getattr(current_user, "is_active", True),
        is_superuser=getattr(current_user, "is_superuser", False),
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(request.refreshToken, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        full_name=getattr(user, "full_name", None),
        role=getattr(user, "role", "user"),
        is_active=getattr(user, "is_active", True),
        is_superuser=getattr(user, "is_superuser", False),
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return {
        "accessToken": create_access_token({"sub": user.email}),
        "refreshToken": create_refresh_token({"sub": user.email}),
        "user": user_response
    }
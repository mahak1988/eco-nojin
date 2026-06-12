#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Security & Deps Files
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
API_DIR = BASE_DIR / "api"


# ============================================================================
# File 1: api/core/security.py - با اضافه کردن alias ها
# ============================================================================
def fix_security():
    print("🔧 بازنویسی api/core/security.py...")
    
    content = '''"""
Security utilities - JWT token management
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from api.core.config import settings


# Security scheme
security = HTTPBearer(auto_error=False)


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """ساخت JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """تأیید و decode کردن توکن"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        farmer_id: str = payload.get("sub")
        if farmer_id is None:
            return None
        return farmer_id
    except JWTError:
        return None


# 🔴 Alias برای backward compatibility
decode_token = verify_token


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """استخراج farmer_id از توکن JWT"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن احراز هویت ارسال نشده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    farmer_id = verify_token(credentials.credentials)
    if farmer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return farmer_id


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    """استخراج farmer_id (اختیاری)"""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)
'''
    
    path = API_DIR / "core" / "security.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ security.py بازنویسی شد\n")


# ============================================================================
# File 2: api/core/deps.py
# ============================================================================
def fix_deps():
    print("🔧 بازنویسی api/core/deps.py...")
    
    content = '''"""
Dependencies for FastAPI routes
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from api.core.security import security, verify_token, get_current_user_id


async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """الزام به احراز هویت - بازگرداندن farmer_id"""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="احراز هویت الزامی است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    farmer_id = verify_token(credentials.credentials)
    if farmer_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="توکن نامعتبر یا منقضی شده است",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return farmer_id


async def require_write_auth(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی نوشتن (همان احراز هویت)"""
    # در آینده می‌توان بررسی role را اضافه کرد
    return farmer_id


async def require_admin(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی ادمین"""
    # TODO: بررسی role از دیتابیس
    # فعلاً همان احراز هویت کافی است
    return farmer_id


# Alias برای backward compatibility
get_current_farmer_id = get_current_user_id
'''
    
    path = API_DIR / "core" / "deps.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ deps.py بازنویسی شد\n")


# ============================================================================
# Main
# ============================================================================
def main():
    print("=" * 70)
    print("🔧 Fixing Security & Deps Files")
    print("=" * 70)
    print()
    
    try:
        fix_security()
        fix_deps()
        
        print("=" * 70)
        print("✅ تمام فایل‌ها با موفقیت بازنویسی شدند!")
        print("=" * 70)
        print()
        print("🚀 گام بعدی:")
        print("  uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
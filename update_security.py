#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update security.py with all backward compatibility aliases
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
API_DIR = BASE_DIR / "api"


def update_security():
    print("🔧 به‌روزرسانی api/core/security.py با تمام alias ها...")
    
    content = '''"""
Security utilities - JWT token management
نسخه 2.0 - با تمام alias های backward compatibility
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


# 🔴 Alias های backward compatibility
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


# 🔴 Alias های اضافی برای backward compatibility
get_current_user = get_current_user_id
get_current_farmer = get_current_user_id
get_current_farmer_id = get_current_user_id


async def get_optional_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[str]:
    """استخراج farmer_id (اختیاری)"""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)


# Alias
get_optional_user = get_optional_user_id
'''
    
    path = API_DIR / "core" / "security.py"
    path.write_text(content, encoding="utf-8")
    print("  ✅ security.py با تمام alias ها به‌روزرسانی شد\n")


def main():
    print("=" * 70)
    print("🔧 Updating Security with All Aliases")
    print("=" * 70)
    print()
    
    try:
        update_security()
        
        print("=" * 70)
        print("✅ فایل با موفقیت به‌روزرسانی شد!")
        print("=" * 70)
        print()
        print("📋 Alias های اضافه شده:")
        print("  ✅ decode_token = verify_token")
        print("  ✅ get_current_user = get_current_user_id")
        print("  ✅ get_current_farmer = get_current_user_id")
        print("  ✅ get_current_farmer_id = get_current_user_id")
        print("  ✅ get_optional_user = get_optional_user_id")
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
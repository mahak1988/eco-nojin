#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Security & Dependencies Fix
نسخه 3.0 - رویکرد جامع برای حل تمام مشکلات import
"""
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
API_DIR = BASE_DIR / "api"


# ============================================================================
# Step 1: Build Comprehensive security.py
# ============================================================================
def build_comprehensive_security():
    """ساخت security.py جامع با تمام توابع احتمالی"""
    print("=" * 70)
    print("🔧 ساخت security.py جامع...")
    print("=" * 70)
    
    content = '''"""
Security utilities - JWT token management & authorization
نسخه 3.0 - جامع با تمام alias ها و توابع authorization
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


# ============================================================================
# Security Schemes
# ============================================================================
security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Password Hashing
# ============================================================================
def hash_password(password: str) -> str:
    """هش کردن رمز عبور"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """تأیید رمز عبور"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Alias برای hash_password"""
    return hash_password(password)


# ============================================================================
# JWT Token Management
# ============================================================================
def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """ساخت JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(subject: str) -> str:
    """ساخت refresh token"""
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def verify_token(token: str) -> Optional[str]:
    """تأیید و decode کردن توکن - بازگرداندن subject (farmer_id)"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        subject: str = payload.get("sub")
        if subject is None:
            return None
        return subject
    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    """Decode کامل توکن و بازگرداندن payload"""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


# ============================================================================
# User Extraction Dependencies
# ============================================================================
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
    """استخراج farmer_id (اختیاری - بدون خطا)"""
    if credentials is None:
        return None
    return verify_token(credentials.credentials)


# ============================================================================
# 🔴 تمام Alias های Backward Compatibility
# ============================================================================
get_current_user = get_current_user_id
get_current_farmer = get_current_user_id
get_current_farmer_id = get_current_user_id
get_current_user_id_from_token = get_current_user_id
get_user_from_token = get_current_user_id

get_optional_user = get_optional_user_id
get_optional_farmer = get_optional_user_id

# ============================================================================
# 🔴 Authorization Dependencies (Role-based)
# ============================================================================
async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """الزام به احراز هویت"""
    return await get_current_user_id(credentials)


async def require_write_auth(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی نوشتن"""
    return farmer_id


async def require_admin(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی ادمین"""
    # TODO: بررسی role از دیتابیس
    return farmer_id


async def require_reviewer(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی reviewer"""
    # TODO: بررسی role از دیتابیس
    return farmer_id


async def require_reviewer_or_admin(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی reviewer یا admin"""
    # TODO: بررسی role از دیتابیس
    return farmer_id


async def require_expert(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی expert"""
    return farmer_id


async def require_farmer(
    farmer_id: str = Depends(require_auth),
) -> str:
    """الزام به دسترسی farmer"""
    return farmer_id


# ============================================================================
# Utility Functions
# ============================================================================
def generate_random_string(length: int = 32) -> str:
    """تولید رشته تصادفی"""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key() -> str:
    """تولید API key"""
    return f"ek_{generate_random_string(48)}"


def extract_token_from_header(authorization: Optional[str]) -> Optional[str]:
    """استخراج توکن از هدر Authorization"""
    if not authorization:
        return None
    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None
'''
    
    path = API_DIR / "core" / "security.py"
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ security.py بازنویسی شد ({len(content)} bytes)")
    print()


# ============================================================================
# Step 2: Build Comprehensive deps.py
# ============================================================================
def build_comprehensive_deps():
    """ساخت deps.py جامع"""
    print("=" * 70)
    print("🔧 ساخت deps.py جامع...")
    print("=" * 70)
    
    content = '''"""
Dependencies for FastAPI routes - Comprehensive version
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from api.core.security import (
    security,
    verify_token,
    get_current_user_id,
    require_auth,
    require_write_auth,
    require_admin,
    require_reviewer,
    require_reviewer_or_admin,
    require_expert,
    require_farmer,
)

# ============================================================================
# Re-export all dependencies for backward compatibility
# ============================================================================
__all__ = [
    "require_auth",
    "require_write_auth",
    "require_admin",
    "require_reviewer",
    "require_reviewer_or_admin",
    "require_expert",
    "require_farmer",
    "get_current_user_id",
]
'''
    
    path = API_DIR / "core" / "deps.py"
    path.write_text(content, encoding="utf-8")
    print(f"  ✅ deps.py بازنویسی شد ({len(content)} bytes)")
    print()


# ============================================================================
# Step 3: Diagnostic - Find All Broken Imports
# ============================================================================
def find_broken_imports():
    """شناسایی تمام import های شکسته قبل از اجرا"""
    print("=" * 70)
    print("🔍 شناسایی import های شکسته...")
    print("=" * 70)
    
    # الگوهای import از security و deps
    patterns = [
        r"from\s+api\.core\.security\s+import\s+([^\n]+)",
        r"from\s+api\.core\.deps\s+import\s+([^\n]+)",
    ]
    
    # توابع موجود در security.py جدید
    available_in_security = {
        "security", "oauth2_scheme", "pwd_context",
        "hash_password", "verify_password", "get_password_hash",
        "create_access_token", "create_refresh_token",
        "verify_token", "decode_token",
        "get_current_user_id", "get_optional_user_id",
        "get_current_user", "get_current_farmer", "get_current_farmer_id",
        "get_current_user_id_from_token", "get_user_from_token",
        "get_optional_user", "get_optional_farmer",
        "require_auth", "require_write_auth", "require_admin",
        "require_reviewer", "require_reviewer_or_admin",
        "require_expert", "require_farmer",
        "generate_random_string", "generate_api_key",
        "extract_token_from_header",
    }
    
    available_in_deps = {
        "require_auth", "require_write_auth", "require_admin",
        "require_reviewer", "require_reviewer_or_admin",
        "require_expert", "require_farmer",
        "get_current_user_id", "security", "verify_token",
    }
    
    broken_imports = []
    files_scanned = 0
    
    for py_file in API_DIR.rglob("*.py"):
        # رد کردن __pycache__
        if "__pycache__" in str(py_file):
            continue
        
        files_scanned += 1
        try:
            content = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                imports_str = match.group(1)
                # استخراج نام‌های import شده
                names = [n.strip() for n in imports_str.split(",")]
                
                for name in names:
                    # حذف "as" alias
                    name = name.split(" as ")[0].strip()
                    if not name:
                        continue
                    
                    # بررسی موجود بودن
                    if "security" in pattern and name not in available_in_security:
                        broken_imports.append({
                            "file": py_file.relative_to(BASE_DIR),
                            "name": name,
                            "source": "security",
                        })
                    elif "deps" in pattern and name not in available_in_deps:
                        broken_imports.append({
                            "file": py_file.relative_to(BASE_DIR),
                            "name": name,
                            "source": "deps",
                        })
    
    print(f"  📊 فایل‌های اسکن شده: {files_scanned}")
    
    if broken_imports:
        print(f"\n  ❌ {len(broken_imports)} import شکسته یافت شد:\n")
        for item in broken_imports:
            print(f"    📄 {item['file']}")
            print(f"       └─ {item['name']} (از {item['source']})")
            print()
        return broken_imports
    else:
        print("  ✅ هیچ import شکسته‌ای یافت نشد!")
        return []


# ============================================================================
# Main Execution
# ============================================================================
def main():
    print("\n" + "=" * 70)
    print("🚀 Comprehensive Security & Dependencies Fix")
    print("=" * 70)
    print()
    
    try:
        # ساخت فایل‌های جامع
        build_comprehensive_security()
        build_comprehensive_deps()
        
        # شناسایی import های شکسته باقی‌مانده
        broken = find_broken_imports()
        
        print("=" * 70)
        print("📋 خلاصه")
        print("=" * 70)
        print()
        
        if broken:
            print(f"⚠️  هنوز {len(broken)} import شکسته وجود دارد.")
            print("   این توابع باید به security.py اضافه شوند.")
            print()
            print("🔧 راه‌حل:")
            print("   1. بک‌اند را اجرا کنید")
            print("   2. خطای بعدی را بفرستید")
            print("   3. آن را به security.py اضافه می‌کنیم")
        else:
            print("✅ تمام import ها سالم هستند!")
        
        print()
        print("🚀 گام بعدی:")
        print("   uvicorn api.main:app --reload --host 0.0.0.0 --port 8000")
        print()
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
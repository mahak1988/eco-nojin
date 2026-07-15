import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from apps.users.models import User
from apps.users.repository import UserRepository
from apps.users.schemas import UserCreate, UserUpdate

# ==========================================
# Security Configuration
# ==========================================
SECRET_KEY = "your-secret-key-change-in-production-min-32-chars"  # TODO: Move to .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ==========================================
# Password Hashing (using bcrypt directly)
# ==========================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    بررسی صحت پسورد.
    
    Args:
        plain_password: پسورد plaintext
        hashed_password: پسورد hash شده
    
    Returns:
        True در صورت صحت، False در غیر این صورت
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except (ValueError, TypeError):
        return False

def get_password_hash(password: str) -> str:
    """
    تبدیل پسورد به hash با استفاده از bcrypt.
    
    محدودیت 72 بایت bcrypt به صورت خودکار مدیریت می‌شود.
    
    Args:
        password: پسورد plaintext
    
    Returns:
        پسورد hash شده
    """
    # محدودیت 72 بایت bcrypt را مدیریت می‌کنیم
    password_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

# ==========================================
# JWT Token Management
# ==========================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    ساخت توکن JWT.
    
    Args:
        data: داده‌های داخل توکن (مثل user_id)
        expires_delta: مدت زمان انقضا
    
    Returns:
        توکن JWT به صورت string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    رمزگشایی توکن JWT.
    
    Returns:
        دیکشنری داده‌های توکن یا None در صورت خطا
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ==========================================
# User Service (Business Logic)
# ==========================================
class UserService:
    """
    سرویس مدیریت کاربران.
    این کلاس مسئول تمام عملیات مرتبط با کاربران است.
    """
    
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
    
    async def register_user(self, user_in: UserCreate) -> User:
        """
        ثبت‌نام کاربر جدید.
        
        Args:
            user_in: اطلاعات کاربر
        
        Returns:
            کاربر ایجاد شده
        
        Raises:
            ValueError: اگر ایمیل تکراری باشد
        """
        # بررسی تکراری نبودن ایمیل
        existing_user = await self.repo.get_by_email(user_in.email)
        if existing_user:
            raise ValueError("ایمیل قبلاً ثبت شده است")
        
        # hash کردن پسورد
        hashed_password = get_password_hash(user_in.password)
        
        # ایجاد کاربر
        user_data = {
            "email": user_in.email,
            "hashed_password": hashed_password,
            "full_name": user_in.full_name,
            "is_active": True,
            "is_superuser": False
        }
        
        user = await self.repo.create(user_data)
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        احراز هویت کاربر.
        
        Args:
            email: ایمیل کاربر
            password: پسورد plaintext
        
        Returns:
            کاربر در صورت موفقیت، None در صورت شکست
        """
        user = await self.repo.get_by_email(email)
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    async def create_access_token_for_user(self, user: User) -> str:
        """
        ساخت توکن دسترسی برای کاربر.
        
        Args:
            user: شیء کاربر
        
        Returns:
            توکن JWT
        """
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return access_token
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """دریافت کاربر بر اساس شناسه."""
        return await self.repo.get_by_id(user_id)
    
    async def update_user(self, user: User, user_in: UserUpdate) -> User:
        """
        بروزرسانی اطلاعات کاربر.
        
        Args:
            user: کاربر فعلی
            user_in: اطلاعات جدید
        
        Returns:
            کاربر بروزرسانی شده
        """
        update_data = user_in.model_dump(exclude_unset=True)
        
        # اگر پسورد تغییر کرده، hash کن
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        user = await self.repo.update(user, update_data)
        return user
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        غیرفعال کردن کاربر (Soft Delete).
        
        Args:
            user_id: شناسه کاربر
        
        Returns:
            True در صورت موفقیت
        """
        user = await self.repo.get_by_id(user_id)
        if not user:
            return False
        
        await self.repo.update(user, {"is_active": False})
        return True
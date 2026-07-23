# users | ماژول احراز هویت و مدیریت کاربران Econojin

> **نکته:** این ماژول **مدیریت کاربران و احراز هویت** پلتفرم Econojin را بر عهده دارد.
> شامل ثبت‌نام، ورود (JWT + OTP)، مدیریت پروفایل و دسترسی‌های role-based است.

## مسئولیت‌ها

این ماژول چهار وظیفه‌ی اصلی دارد:

1. **مدیریت کاربران** (`router.py`, `service.py`, `repository.py`)
   - ثبت‌نام کاربر جدید با ایمیل و رمز عبور
   - بروزرسانی پروفایل کاربر
   - غیرفعال کردن کاربران (فقط superuser)
   - لیست کردن کاربران با صفحه‌بندی

2. **احراز هویت JWT** (`auth_router.py`)
   - ورود با ایمیل و رمز عبور و دریافت توکن Bearer
   - اعتبارسنجی توکن در تمام endpointهای محافظت‌شده
   - پشتیبانی از OTP (کد یکبارمصرف پیامکی)

3. **Role-Based Access Control** (`dependencies.py`)
   - `get_current_user` — استخراج کاربر از توکن JWT
   - `get_current_active_user` — بررسی فعال بودن کاربر
   - `get_current_active_superuser` — بررسی superuser بودن

4. **امنیت احراز هویت** (`config.py`, `exceptions.py`)
   - تنظیمات توکن (مدت اعتبار، الگوریتم HS256)
   - استثناهای سفارشی (InvalidCredentials, UserNotFound)

## ساختار

```
users/
├── __init__.py                # Module init
├── router.py                  # ★ روتر اصلی کاربران
├── auth_router.py             # ★ روتر احراز هویت (login/register/otp)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # Database access (SQLAlchemy)
├── models.py                  # ★ ORM model User
├── dependencies.py            # ★ FastAPI dependencies (auth)
├── config.py                  # ★ تنظیمات auth
├── exceptions.py              # ★ استثناهای سفارشی
└── tests/                     # Pytest tests
    ├── test_router.py
    └── ...
```

## مدل داده (`models.py`)

```python
class User(Base):
    """مدل کاربر برای پلتفرم SaaS با پشتیبانی RBAC."""
    
    __tablename__ = "users"
    
    id: int                    # شناسه یکتا
    email: str                 # ایمیل (unique, index)
    hashed_password: str       # رمز عبور هش شده
    full_name: str | None      # نام کامل (اختیاری)
    is_active: bool            # وضعیت فعال بودن (پیش‌فرض: True)
    is_superuser: bool         # دسترسی ادمین (پیش‌فرض: False)
    created_at: datetime       # تاریخ ایجاد
    updated_at: datetime       # تاریخ بروزرسانی
```

**نکته امنیتی:** رمز عبور هرگز به صورت plaintext ذخیره نمی‌شود. هش کردن با Argon2 (اولیه) و Bcrypt (پشتیبان) در `apps/shared_core/security.py` انجام می‌شود.

## Endpointهای API

### مسیرهای عمومی (نیاز به احراز هویت ندارند)

| Method | Path | توضیح |
|--------|------|--------|
| POST | `/api/v1/users/register` | ثبت‌نام کاربر جدید (ایمیل + رمز عبور) |
| POST | `/api/v1/auth/login` | ورود و دریافت توکن JWT |

**ثبت‌نام:**
```json
// POST /api/v1/users/register
{
    "email": "user@example.com",
    "password": "mysecurepassword123",
    "full_name": "کاربر نمونه"  // اختیاری
}
// Response 201
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "کاربر نمونه",
    "is_active": true,
    "is_superuser": false,
    "created_at": "2025-01-15T10:30:00Z"
}
```

**ورود:**
```json
// POST /api/v1/auth/login
{
    "email": "user@example.com",
    "password": "mysecurepassword123"
}
// Response 200
{
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

### مسیرهای محافظت‌شده (نیاز به Bearer token)

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/api/v1/users/me` | دریافت اطلاعات کاربر فعلی |
| PUT | `/api/v1/users/me` | بروزرسانی پروفایل کاربر فعلی |

**استفاده از توکن:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### مسیرهای ادمین (فقط superuser)

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/api/v1/users/` | لیست کاربران (با صفحه‌بندی) |
| DELETE | `/api/v1/users/{user_id}` | غیرفعال کردن کاربر |

**لیست کاربران:**
```bash
curl -H "Authorization: Bearer TOKEN" \
     "http://localhost:8000/api/v1/users/?skip=0&limit=100"
```

## احراز هویت JWT

### جریان احراز هویت

```
1. کاربر ───POST /auth/login───→ سرور
2. سرور ───验证 ایمیل و رمز───→ دیتابیس
3. سرور ───ایجاد JWT───→ {
       "sub": "user_id",
       "exp": "8 روز بعد"
   }
4. سرور ───Response───→ { "access_token": "eyJ...", "token_type": "bearer" }
5. کاربر ───GET /users/me───→ Authorization: Bearer eyJ...
6. سرور ───decode JWT───→ payload
7. سرور ───Response───→ { "id": 1, "email": "...", ... }
```

### ویژگی‌های توکن
- **الگوریتم:** HS256
- **مدت اعتبار:** ۸ روز (قابل تنظیم در `.env`)
- **کلید امضا:** `SECRET_KEY` از `.env` (در production حتماً تغییر دهید)
- **حمل payload:** `{"sub": user_id, "exp": timestamp}`

## OTP (کد یکبارمصرف)

پشتیبانی از احراز هویت دو مرحله‌ای از طریق SMS:

| Method | Path | توضیح |
|--------|------|--------|
| POST | `/api/v1/auth/otp/request` | درخواست کد OTP |
| POST | `/api/v1/auth/otp/verify` | تأیید کد OTP |

ارائه‌دهندگان SMS:
- **Kavenegar** — داخلی، هزینه پایین
- **Twilio** — بین‌المللی
- **Mock** — برای تست محلی (پیش‌فرض)

فعال/غیرفعال کردن: `ENABLE_OTP=true/false` در `.env`

## Dependency Injection

### وابستگی‌های قابل استفاده در سایر ماژول‌ها

```python
from apps.users.dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_active_superuser,
    get_user_service,
)
from apps.users.models import User

# در endpointهای محافظت‌شده:
async def protected_endpoint(
    current_user: User = Depends(get_current_user)
):
    return {"email": current_user.email}

# در endpointهای ادمین:
async def admin_endpoint(
    current_user: User = Depends(get_current_active_superuser)
):
    return {"message": "Welcome admin!"}
```

## مثال‌های کاربردی

### ثبت‌نام و ورود با curl

```bash
# 1. ثبت‌نام
curl -X POST http://localhost:8000/api/v1/users/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@econojin.com", "password": "Test1234!", "full_name": "کاربر تست"}'

# 2. ورود و دریافت توکن
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@econojin.com", "password": "Test1234!"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3. دریافت اطلاعات کاربر
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### استفاده در کد پایتون

```python
import httpx

# ثبت‌نام
response = httpx.post(
    "http://localhost:8000/api/v1/users/register",
    json={"email": "user@example.com", "password": "SecurePass123"}
)

# ورود
response = httpx.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"email": "user@example.com", "password": "SecurePass123"}
)
token = response.json()["access_token"]

# درخواست محافظت‌شده
response = httpx.get(
    "http://localhost:8000/api/v1/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
```

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/users/tests/ -v

# اجرای سرور توسعه
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## متغیرهای محیطی (`.env`)

```ini
# احراز هویت
SECRET_KEY=your-secret-key-here       # حداقل 32 کاراکتر تصادفی
ALGORITHM=HS256                        # الگوریتم JWT
ACCESS_TOKEN_EXPIRE_MINUTES=11520      # 8 روز
REQUIRE_AUTH_FOR_WRITES=false          # الزام auth برای نوشتن

# SMS / OTP
SMS_PROVIDER=mock                      # kavenegar | twilio | mock
KAVENEGAR_API_KEY=                     # API Key Kavenegar
TWILIO_ACCOUNT_SID=                    # Account SID Twilio
TWILIO_AUTH_TOKEN=                     # Auth Token Twilio
TWILIO_PHONE_NUMBER=                   # شماره فرستنده Twilio

# Superuser پیش‌فرض
FIRST_SUPERUSER=admin@econojin.com
FIRST_SUPERUSER_PASSWORD=changethis    # در production تغییر دهید
```

## تغییرات مهم

- **فاز ۲:** اضافه شدن `auth_router.py` مجزا برای مسیرهای احراز هویت
- **فاز ۲:** اضافه شدن `config.py` و `exceptions.py` برای مدیریت متمرکز تنظیمات auth
- **فاز ۲:** بازنویسی کامل dependency injection با پشتیبانی از User model واقعی
- **فاز ۲:** افزودن OTP و پشتیبانی از SMS (Kavenegar/Twilio)
- **فاز ۲:** رمزنگاری رمز عبور با Argon2 (جایگزین Bcrypt) با پشتیبان Bcrypt

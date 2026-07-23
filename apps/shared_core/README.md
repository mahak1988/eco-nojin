# shared_core | مرجع رسمی لایه اشتراکی پلتفرم Econojin

> **نکته:** این ماژول **مرجع رسمی** لایه اشتراکی (shared) برای کل پلتفرم Econojin است.
> ماژول قدیمی `apps/shared` (قالب auto-scaffolded خالی) در تاریخ ۱۴۰۵/۰۴/۲۶ منسوخ و
> حذف شد. همه‌ی مدل‌ها، Base، session و repository مرکزی باید از همین‌جا تأمین شوند.

## مسئولیت‌ها

این ماژول شش وظیفه‌ی اصلی دارد:

1. **زیرساخت پایه‌ی دیتابیس** (`database/`)
   - `Base` (DeclarativeBase) که همه‌ی مدل‌های ORM از آن ارث می‌برند.
   - `engine` و `async_session_maker` برای SQLAlchemy 2.0 Async.
   - `get_db_session` Dependency برای FastAPI.
   - `init_db` / `close_db` برای lifespan اپلیکیشن.
2. **Repository عمومی** (`database/repository.py`)
   - `BaseRepository[T]` با CRUD کامل (get/get_multi/create/update/delete/count).
3. **مدل‌های مشترک** (`models.py`)
   - `SharedCore`, `AdminSetting`, `AuditLog`, `SystemReport`.
4. **پیکربندی متمرکز** (`config.py`)
   - مدیریت تمام تنظیمات پروژه با Pydantic v2 Settings.
   - بارگذاری از `.env` با اعتبارسنجی خودکار.
5. **امنیت** (`security.py`)
   - هش کردن رمز عبور با Argon2 (اولیه) و Bcrypt (پشتیبان).
   - ایجاد و اعتبارسنجی توکن JWT با HS256.
   - تولید کد OTP (۶ رقمی).
6. **Middleware و Monitoring**
   - `RateLimitMiddleware` — محدودیت نرخ درخواست (پیش‌فرض ۱۲۰/دقیقه).
   - `AuditLogMiddleware` — ثبت رویدادهای حسابرسی.
   - یکپارچه‌سازی Sentry برای خطاهای production.

## ساختار

```
shared_core/
├── __init__.py                  # Module init (version = 1.0.0)
├── config.py                    # ★ Pydantic v2 Settings متمرکز
├── security.py                  # ★ JWT + Argon2/Bcrypt + OTP
├── deps.py                      # ★ Dependency Injection (get_current_user, etc.)
├── crud.py                      # ★ Base CRUD Generic
├── models.py                    # ORM models مشترک
├── schemas.py                   # Pydantic schemas پایه
├── service.py                   # Business logic مشترک
├── repository.py                # (سطح بالا) - wrapper روی BaseRepository
├── router.py                    # FastAPI router مشترک (در صورت نیاز)
├── dependencies.py              # Dependencies مشترک
├── database/
│   ├── __init__.py
│   ├── session.py               # Engine, Base, get_db_session, init_db
│   └── repository.py            # BaseRepository[T] - CRUD عمومی
├── middleware/
│   ├── rate_limit.py            # Rate limiting middleware
│   └── audit_log.py             # Audit logging middleware
├── monitoring/
│   └── sentry.py                # Sentry integration
└── tests/                       # Pytest tests
    ├── test_database_session.py
    ├── test_env_loading.py
    ├── test_shared_core.py
    └── test_xai_models.py
```

## مدل‌های داده

| Model          | Table            | توضیح                                   |
|----------------|------------------|------------------------------------------|
| `SharedCore`   | `shared_core`    | موجودیت پایه‌ی عمومی (نام/توضیح/وضعیت).   |
| `AdminSetting` | `admin_settings` | تنظیمات key-value سیستمی (unique key).    |
| `AuditLog`     | `audit_logs`     | رویدادهای حسابرسی (actor, event_type).   |
| `SystemReport` | `system_reports` | گزارش‌های سیستمی با status و payload.    |

## پیکربندی متمرکز (`config.py`)

تمامی تنظیمات پروژه از طریق کلاس `Settings` مدیریت می‌شود:

```python
from apps.shared_core.config import settings

# دسترسی به تنظیمات
print(settings.PROJECT_NAME)       # "Econojin API"
print(settings.ENVIRONMENT)        # "local" | "staging" | "production"
print(settings.API_V1_STR)         # "/api/v1"
print(settings.DATABASE_URL)       # SQLite یا PostgreSQL
print(settings.LLM_PROVIDER)       # "groq" | "gemini" | "xai" | ...
```

### ویژگی‌های کلیدی تنظیمات:
- ✅ بارگذاری از `.env` با Pydantic v2 validation
- ✅ محاسبه خودکار `SQLALCHEMY_DATABASE_URI` بر اساس تنظیمات
- ✅ Feature flags: `ENABLE_OTP`, `ENABLE_SIMULATION`, `ENABLE_ECOCOIN`, `ENABLE_GIS`
- ✅ اعتبارسنجی secrets پیش‌فرض ("changethis") برای امنیت production
- ✅ پشتیبانی از CORS پویا با `all_cors_origins`
- ❌ در محیط production، مقداردهی `SECRET_KEY`, `POSTGRES_PASSWORD`, و `FIRST_SUPERUSER_PASSWORD` اجباری است

## امنیت (`security.py`)

### هش کردن رمز عبور
```python
from apps.shared_core.security import get_password_hash, verify_password

hashed = get_password_hash("my_secret_password")
is_valid = verify_password("my_secret_password", hashed)  # True
```

### توکن JWT
```python
from apps.shared_core.security import create_access_token, decode_token

token = create_access_token(subject=user_id)
payload = decode_token(token)  # {"sub": user_id, "exp": timestamp}
```

### Dependency Injection (`deps.py`)
```python
from apps.shared_core.deps import (
    SessionDep,           # AsyncSession
    CurrentUser,          # کاربر احراز هویت شده
    CurrentActiveUser,    # کاربر فعال
    CurrentSuperUser,     # کاربر superuser
    TokenDep,             # Bearer token اختیاری
)
```

## نحوه‌ی استفاده

### Dependency Injection در FastAPI

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared_core.database.session import get_db_session

async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
    ...
```

### استفاده از DI سطح بالا
```python
from apps.shared_core.deps import SessionDep, CurrentUser

@app.get("/items")
async def list_items(
    session: SessionDep,
    current_user: CurrentUser,
):
    # session: AsyncSession
    # current_user: dict with user info
    ...
```

### ساخت Repository اختصاصی

```python
from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared_core.database.repository import BaseRepository
from apps.shared_core.models import AdminSetting

class AdminSettingRepository(BaseRepository[AdminSetting]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AdminSetting)

    async def get_by_key(self, key: str) -> AdminSetting | None:
        ...
```

## اجرای تست‌ها

```bash
# از ریشه‌ی پروژه
pytest apps/shared_core/tests/ -v

# تست‌های خاص
pytest apps/shared_core/tests/test_database_session.py -v
```

## اجرای سرور توسعه

```bash
cd d:\econojin.com
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## تغییرات مهم

- **۱۴۰۵/۰۴/۲۶:** ماژول `apps/shared` قدیمی حذف شد. این ماژول قالب خالی auto-scaffolded
  بود و هیچ کد واقعی نداشت. همه‌ی ارجاعات باید به `apps.shared_core` هدایت شوند.
- **فاز ۲:** افزودن `config.py` (Pydantic v2 Settings)، `security.py` (JWT + Argon2)، 
  `deps.py` (DI pattern)، `crud.py` (Base CRUD Generic).
- **فاز ۲:** افزودن middlewareهای `rate_limit` و `audit_log` و یکپارچه‌سازی Sentry.

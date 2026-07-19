# گزارش جامع تحلیل و ارتقاء پروژه Econojin

## ۱. خلاصه اجرایی (Executive Summary)

پروژه **Econojin** در وضعیت فنی جذابی قرار دارد: از نظر **معماری ماژولار** و **الگوهای توسعه**، چهارچوب خوبی دارد (با الگوی Model→Schema→Repository→Service→Router). اما در زمینه **امنیت** و **یکپارچگی کد**، نقاط ضعف جدی وجود دارد که مانع استقرار ایمن در production می‌شوند.

**نقاط بحرانی شناسایی‌شده:**
- نقص امنیتی **بحرانی**: کلید مخفی JWT دیکدود در کد (در `apps/users/service.py` خط 14)
- تنازعات امنیتی: دو سیستم مدیریت توکن مجزا و ناسازگار
- داشبورد GitLab CI بهتر از GitHub Actions فعلی
- استفاده از bcrypt مستقیم به‌جای Argon2 پیشرفته
- عدم وجود rate limiting ورودی (Brute Force Protection)

---

## ۲. جدول مقایسه‌ای جامع (KPI Comparison)

| حوزه (Domain) | شاخص (Metric) | پروژه من (Econojin) | پروژه برتر (Best-in-Class) | فاصله (Gap) | شدت (Criticality) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **معماری (Architecture)** | الگوی معماری | ماژولار Monorepo با الگوی موجود | Clean Architecture / Hexagonal | متوسط | متوسط |
| | مقیاس‌پذیری | async SQLAlchemy، Docker Compose | Kubernetes + Horizontal Pod Autoscaling | متوسط | متوسط |
| | ماژولار بودن | ✅ ۱۵ ماژول API، ولی وابقه circular | Clean separation با dependency injection | متوسط | متوسط |
| **امنیت (Security)** | مدیریت اسرار | کلید دیکدود در کد (بحرانی) | HashiCorp Vault / AWS Secrets Manager | **بحرانی** | **بحرانی** |
| | اعتبارسنجی ورودی | Pydantic v2، ولی ناقص | Pydantic + Validate سفارشی | کم | کم |
| | احراز هویت و مجوز | JWT HS256 + OTP | Auth0 / OAuth2 / RBAC مدرن | متوسط | متوسط |
| | لاگ‌گیری امنیتی | ساده، فقط لاگ سطح API | Audit Trail با Sentry + ELK | متوسط | متوسط |
| | وابستگی‌های آسیب‌پذیر | ابزارهای اسکن موجود | pip-audit + Dependabot | **بحرانی** | متوسط |
| **کد (Code)** | کیفیت کد | الگوهای موجود، تنازعات | الگوی یکپارچه بدون تکرار | **بحرانی** | متوسط |
| | پوشش تست | 70%+ (pytest-asyncio) | >80% coverage با CI gate | متوسط | متوسط |
| | مدیریت خطا | Exception handler سراسری | Error codes استاندارد + trace IDs | کم | کم |
| **زیرساخت (DevOps)** | مستندات | خوب، ولی گپ‌ها | مستندات کامل ۱۰۰٪ | متوسط | کم |
| | CI/CD Pipeline | GitHub Actions پیچیده | GitLab CI یا GitHub Actions بهبود یافته | متوسط | متوسط |
| | Monitoring & Observability | Prometheus + Sentry | OpenTelemetry + AlertManager | متوسط | متوسط |

---

## ۳. لیست فایل‌های برتر استخراج‌شده

### ۳.۱ FastAPI Best Practices Repository
**مرجع:** https://github.com/zhanymkanov/fastapi-best-practices

- **نام فایل برتر**: `src/auth/config.py`
- **دلیل برتری**: استفاده از Pydantic Settings جداگانه برای تنظیمات auth (`JWT_ALG`، `JWT_SECRET`، `JWT_EXP`) باعث می‌شود تنظیمات به‌صورت ماژولار و ایمن مدیریت شوند
- **کمبود در پروژه من**: تنظیمات auth در هر ماژول تکراری است و در `apps/users/service.py` کلید دیکدود شده

### ۳.۲ Full-Stack FastAPI Template
**مرجع:** https://github.com/fastapi/full-stack-fastapi-postgresql

- **نام فایل برتر**: `backend/app/core/security.py`
- **دلیل برتری**: استفاده از Argon2 به‌عنوان رمزنگاری پیش‌فرض با fallback به bcrypt، و توابع ایمنی type-safe با docstringهای کامل
- **کمبود در پروژه من**: در `apps/shared_core/security.py` Argon2 استفاده شده، اما در `apps/users/service.py` از bcrypt مستقیم استفاده می‌شود (ناهمگونی)

### ۳.۳ Shadcn-UI Monorepo
**مرجع:** https://github.com/shadcn-ui/ui

- **نام فایل برتر**: `packages/ui/src/button.tsx`
- **دلیل برتری**: Design System کامل با TypeScript strict mode، variants، و className merging با `tailwind-merge`
- **کمبود در پروژه من**: Design System در `packages/ui` وجود دارد، اما کامپوننت‌های کشاورزی اختصاصی کم‌است

---

## ۴. لیست ماژول‌ها و قابلیت‌های گم‌شده

| ماژول/فایل گم‌شده | دلیل نیاز | اولویت |
| :--- | :--- | :--- |
| **auth/config.py** | جداسازی تنظیمات JWT به‌صورت ماژولار (JWT_SECRET از .env بخوانده نشود) | **بحرانی** |
| **auth/exceptions.py** | تعریف استاندارد خطاهای auth (`InvalidCredentials`، `TokenExpired`، `AccountLocked`) | متوسط |
| **middleware/rate_limit.py** | جلوگیری از حملات Brute Force در ورود (مثلاً ۵ تلاش در دقیقه) | **بحرانی** |
| **middleware/audit_log.py** | لاگ‌گیری همه درخواست‌های auth برای ردیابی نفوذ | متوسط |
| **tests/conftest.py** | Fixtureهای آماده برای تست integration (override dependencies) | متوسط |
| **alembic migrations** | migrations داینامیک به‌جای `create_all` — ضروری برای production | **بحرانی** |
| **scripts/check_god_files.py** | اسکریپت گفت‌وگو شده در CI ولی وجود ندارد | متوسط |

---

## ۵. نقشه‌راه اصلاحی دقیق و گام‌به‌گام

### گام ۰. (P0 - امنیت) رفع نقص امنیتی بحرانی
```diff
--- a/apps/users/service.py
+++ b/apps/users/service.py
@@ -11,11 +11,4 @@
 # JWT Token Management
-# ==========================================
-SECRET_KEY = "your-secret-key-change-in-production-min-32-chars"  # TODO: Move to .env
-ALGORITHM = "HS256"
-ACCESS_TOKEN_EXPIRE_MINUTES = 30
+# تمام توابع از apps.shared_core.security و settings استفاده می‌کنند
```

**راه‌حل:** حذف کامل این توابع و استفاده از `apps/shared_core/security.py` + `apps/shared_core/config.py`

### گام ۱. ایجاد فایل auth/config.py
```python
# apps/users/config.py
"""User module configuration with proper secret management."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Literal
import warnings

class UserSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    
    JWT_ALGORITHM: Literal["HS256", "RS256"] = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    PASSWORD_MIN_LENGTH: int = 8
    
    @model_validator(mode="after")
    def _validate_secrets(self):
        if self.JWT_ALGORITHM == "HS256":
            warnings.warn(
                "HS256 is not recommended for production. Consider RS256.",
                stacklevel=1,
            )
        return self

user_settings = UserSettings()
```

### گام ۲. ایجاد rate limiting middleware
```python
# apps/shared_core/middleware/rate_limit.py
"""Rate limiting middleware to prevent brute force attacks."""
from time import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

# In-memory store (برای production از Redis استفاده کنید)
_failed_attempts: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_WINDOW = 60  # ثانیه
_MAX_ATTEMPTS = 5

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        path = request.url.path
        
        # فقط برای endpointهای auth
        if path.startswith("/api/v1/auth"):
            now = time()
            attempts = _failed_attempts[f"{client_ip}:{path}"]
            
            # حذف تلاش‌های قدیمی
            _failed_attempts[f"{client_ip}:{path}"] = [
                t for t in attempts if now - t < _RATE_LIMIT_WINDOW
            ]
            
            if len(_failed_attempts[f"{client_ip}:{path}"]) >= _MAX_ATTEMPTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many attempts. Please try again later.",
                )
        
        response = await call_next(request)
        
        # ثبت تلاش‌های ناموفق
        if response.status_code == 401:
            _failed_attempts[f"{client_ip}:{path}"].append(time())
        
        return response
```

### گام ۳. نوشتن Alembic migrations
```python
# alembic/versions/20240501_create_users_table.py
"""Create users table with proper constraints."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20240501_create_users"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean, default=True, nullable=False),
        sa.Column("is_superuser", sa.Boolean, default=False, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
```

### گام ۴. بهبود CI/CD - افزودن Security Gate
```yaml
# .github/workflows/07-pre-commit.yml (جدید)
name: Pre-commit Checks
on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - uses: pre-commit/action@v3.0.1
        with:
          extra_args: --all-files
```

### گام ۵. رفع تنازعات security
باید از یک منبع تنظیمات واحد استفاده شود. فایل `apps/users/service.py` را با استفاده از `apps.shared_core.security` جایگزین کنید:

```python
# apps/users/service.py (بخش اصلاح‌شده)
from apps.shared_core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_token,
)
from apps.shared_core.config import settings

# حذف تمام تعریف‌های دیگر SECRET_KEY، ALGORITHM و ...
# استفاده مستقیم از settings.ALGORITHM و settings.SECRET_KEY
```

### گام ۶. بهبود Dockerfile
```dockerfile
# docker/Dockerfile.api (بهبود یافته)
FROM python:3.12-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
RUN pip install --upgrade pip && pip wheel --no-cache-dir --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /wheels /wheels
COPY . .
RUN pip install --no-cache /wheels/*
ENV PYTHONUNBUFFERED=1
USER 1000
CMD ["uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## ۶. دستورات اجرایی برای رفع فوری

```bash
# ۱. حذف کلید دیکدود از کد
$ git grep -n "SECRET_KEY.*=.*your-secret\|changethis" apps/users/service.py
# خروجی را حذف کنید و از settings استفاده کنید

# ۲. اضافه کردن rate limiting
$ pip install slowapi
# یا استفاده از redis برای production

# ۳. اجرای security scan
$ pip install bandit safety pip-audit
$ bandit -r apps/ -ll --skip B101
$ pip-audit -r requirements.txt
```

---

## ۷. توصیه‌های نهایی

| اولویت | عمل | زمان تخمین |
|-------|-----|------------|
| 🔴 بحرانی | حذف کلید دیکدود از `apps/users/service.py` | ۱ ساعت |
| 🔴 بحرانی | یکپارچه‌سازی security بین دو فایل | ۲ ساعت |
| 🟠 متوسط | افزودن rate limiting middleware | ۳ ساعت |
| 🟠 متوسط | نوشتن Alembic migrations | ۴ ساعت |
| 🟢 کم | بهبود Dockerfile با multi-stage | ۲ ساعت |
| 🟢 کم | افزودن pre-commit hooks | ۱ ساعت |

---

*این گزارش بر اساس تحلیل کد و مقایسه با استانداردهای FastAPI/React در گیت‌هاب تهیه شده است.*
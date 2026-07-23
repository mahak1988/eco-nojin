# 📋 برنامه توسعه Econojin - فاز ۱: تثبیت زیرساخت

## وضعیت فعلی پروژه (پس از مطالعه کامل)

### ✅ نقاط قوت شناسایی‌شده
1. **ساختار ماژولار**: ۱۵ اپلیکیشن مجزا با مسئولیت‌های مشخص
2. **معماری لایه‌ای**: Router → Service → Repository به درستی پیاده‌سازی شده
3. **پشتیبانی چندزبانه**: فارسی/انگلیسی در کامنت‌ها و مستندات
4. **دیتابیس Async**: استفاده از SQLAlchemy + aiosqlite
5. **مدل‌های شبیه‌سازی**: ۸ حوزه تخصصی (Hydrology, Soil, Carbon, Biodiversity, etc.)
6. **احراز هویت دوگانه**: Users + Auth routers
7. **Admin Panel**: ماژول مدیریت جداگانه
8. **AI Agents**: یکپارچگی با LLM Factory
9. **Docker Compose**: ۴ فایل compose برای محیط‌های مختلف
10. **Alembic**: سیستم Migration راه‌اندازی شده

### ❌ مشکلات بحرانی شناسایی‌شده

#### ۱. مشکلات Alembic و Migration
- [ ] `alembic/script.py.mako` وجود نداشت (اکنون اضافه شد)
- [ ] ایمپورت خودکار مدل‌ها در `env.py` ناقص بود
- [ ] محدودیت SQLite در ALTER COLUMN
- [ ] ۸۰+ جدول قدیمی نیاز به حذف دارند

#### ۲. مشکلات CRUD Endpoints
- [ ] **apps/api/router.py**: فقط CRUD ساده بدون منطق کسب‌وکار
- [ ] **apps/simulation/router.py**: عدم یکپارچگی با مدل‌های شبیه‌سازی واقعی
- [ ] **service.py** در هر دو ماژول: خط ۴۴-۴۵ dead code دارد
- [ ] اعتبارسنجی داده‌ها در سطح Service انجام نمی‌شود

#### ۳. مشکلات Database Session
- [ ] fallback stub در routerها هنوز فعال است
- [ ] مسیر دیتابیس: `apps/econojin.db` باید به ریشه پروژه منتقل شود
- [ ] عدم مدیریت صحیح transaction در nested operations

#### ۴. مشکلات Frontend Integration
- [ ] صفحات web با داده‌های mock کار می‌کنند
- [ ] عدم اتصال به API endpoints واقعی
- [ ] React Query به صورت سراسری پیاده‌سازی نشده
- [ ] TypeScript types با backend schemas همخوانی ندارد

#### ۵. مشکلات Testing
- [ ] پوشش تست بک‌اند < 20%
- [ ] تست‌های E2E وجود ندارند
- [ ] تست‌های integration برای شبیه‌سازی‌ها ناقص است

#### ۶. مشکلات Deployment
- [ ] Docker images بهینه نشده‌اند
- [ ] CI/CD pipeline ناقص
- [ ] مانیتورینگ و logging متمرکز وجود ندارد
- [ ] Health checks ناقص هستند

---

## 🎯 اهداف فاز ۱ (هفته ۱-۲)

### هدف اصلی: تثبیت زیرساخت و رفع مشکلات بحرانی

#### ۱. تکمیل Alembic Migration System ✅ (انجام شد)
- [x] بازسازی `alembic/env.py` با ایمپورت خودکار تمام مدل‌ها
- [x] ایجاد `alembic/script.py.mako`
- [x] تولید migration اولیه برای جداول فعلی
- [x] تنظیم دیتابیس روی آخرین revision

#### ۲. استانداردسازی CRUD Endpoints
- [ ] اصلاح `apps/api/service.py`: حذف dead code و افزودن اعتبارسنجی
- [ ] اصلاح `apps/simulation/service.py`: حذف dead code
- [ ] افزودن validation layer در Service برای تمام ماژول‌ها
- [ ] پیاده‌سازی custom exceptions به جای ValueError
- [ ] افزودن audit logging برای عملیات CRUD

#### ۳. یکپارچه‌سازی Database Sessions
- [ ] تغییر مسیر دیتابیس به `/workspace/econojin.db`
- [ ] حذف fallback stub از تمام routerها
- [ ] افزودن dependency injection صحیح در main.py
- [ ] تست transaction management

#### ۴. راه‌اندازی API Gateway
- [ ] ایجاد `apps/api_gateway/` برای routing مرکزی
- [ ] پیاده‌سازی rate limiting
- [ ] افزودن request/response logging
- [ ] ایجاد health check aggregator

#### ۵. بهبود ساختار تست
- [ ] افزودن pytest fixtures برای database sessions
- [ ] نوشتن test cases برای CRUD operations
- [ ] راه‌اندازی coverage reporting
- [ ] ایجاد test data factories

#### ۶. مستندسازی API
- [ ] به‌روزرسانی OpenAPI/Swagger docs
- [ ] افزودن examples به تمام endpoints
- [ ] ایجاد Postman collection
- [ ] مستندسازی error codes

---

## 📅 زمان‌بندی فاز ۱

### روز ۱-۲: تثبیت Alembic ✅
- [x] بررسی و اصلاح env.py
- [x] ایجاد script.py.mako
- [x] تولید migration اولیه
- [x] تست rollback/upgrade

### روز ۳-۴: استانداردسازی Services
- [ ] اصلاح service.py در api و simulation
- [ ] ایجاد exceptions.py در shared_core
- [ ] افزودن validation decorators
- [ ] نوشتن unit tests برای services

### روز ۵-۶: یکپارچگی Database
- [ ] انتقال دیتابیس به ریشه
- [ ] حذف stubs از routerها
- [ ] تست concurrent requests
- [ ] بهینه‌سازی connection pool

### روز ۷-۸: API Gateway
- [ ] ایجاد ساختار api_gateway
- [ ] پیاده‌سازی middlewareها
- [ ] افزودن rate limiting
- [ ] تست load balancing

### روز ۹-۱۰: Testing & Documentation
- [ ] نوشتن ۵۰+ test case
- [ ] راه‌اندازی coverage (هدف: ۶۰٪+)
- [ ] به‌روزرسانی Swagger docs
- [ ] ایجاد Postman collection

### روز ۱۱-۱۲: Docker & Deployment Prep
- [ ] بهینه‌سازی Dockerfile
- [ ] افزودن multi-stage build
- [ ] ایجاد docker-compose.dev.yml
- [ ] تست deployment محلی

### روز ۱۳-۱۴: Final Review & Bug Fixes
- [ ] code review کامل
- [ ] رفع bugs شناسایی‌شده
- [ ] performance testing
- [ ] آماده‌سازی برای فاز ۲

---

## 🔧 اقدامات فنی جزئی‌تر

### ۱. ایجاد Custom Exceptions
```python
# apps/shared_core/exceptions.py
class EconojinException(Exception):
    base_status_code = 500
    
class NotFoundError(EconojinException):
    base_status_code = 404
    
class ValidationError(EconojinException):
    base_status_code = 400
    
class UnauthorizedError(EconojinException):
    base_status_code = 401
```

### ۲. اصلاح Service Layer
```python
# قبل (مشکل‌دار):
async def update(self, id: int, data: SimulationUpdate) -> Simulation:
    return await self.get(id)  # raises if not found
    # The line below actually performs the update
    obj = await self.repo.update(id, data)  # ← هرگز اجرا نمی‌شود!

# بعد (اصلاح‌شده):
async def update(self, id: int, data: SimulationUpdate) -> Simulation:
    existing = await self.get(id)  # raises if not found
    validated_data = self._validate_update(existing, data)
    obj = await self.repo.update(id, validated_data)
    await self._audit_log("update", id, data)
    return obj
```

### ۳. افزودن Validation Layer
```python
# apps/shared_core/validators.py
from pydantic import BaseModel, field_validator

class BaseValidator(BaseModel):
    @field_validator('*')
    @classmethod
    def sanitize_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
```

### ۴. بهبود Database Configuration
```python
# تغییر از:
DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"

# به:
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite+aiosqlite:///{PROJECT_ROOT}/econojin.db"
)
```

---

## 📊 معیارهای موفقیت فاز ۱

| معیار | وضعیت فعلی | هدف پایان فاز ۱ |
|-------|-----------|----------------|
| پوشش تست بک‌اند | <20% | ≥60% |
| تعداد endpoints مستند | ۱۵ | ۴۰+ |
| خطاهای unhandled | زیاد | صفر |
| زمان startup | ~5s | <2s |
| Database migrations | ناقص | کامل و تست‌شده |
| Docker image size | ~1.2GB | <500MB |
| API response time (p95) | نامشخص | <200ms |

---

## 🚀 آماده‌سازی برای فاز ۲

پس از تکمیل فاز ۱، پروژه آماده ورود به **فاز ۲: توسعه ماژول‌های کسب‌وکار** خواهد بود:

1. **ماژول کشاورزی**: یکپارچگی DSSAT/APSIM با API
2. **ماژول آب**: SWAT/MODFLOW simulation endpoints
3. **ماژول کربن**: RothC/CO2Fix calculations
4. **ماژول اقتصاد**: TEEB valuation engine
5. **Frontend**: اتصال صفحات به API واقعی
6. **Auth**: JWT tokens و role-based access

---

## 📝 چک‌لیست روزانه

### روز جاری: روز ۱ ✅
- [x] مطالعه کامل پروژه
- [x] شناسایی مشکلات
- [x] ایجاد برنامه توسعه
- [x] اصلاح alembic/env.py
- [x] ایجاد alembic/script.py.mako
- [x] تولید migration اولیه
- [x] تنظیم دیتابیس روی head

### فردا: روز ۲
- [ ] تست migration با downgrade/upgrade
- [ ] شروع اصلاح service.py ها
- [ ] ایجاد exceptions.py
- [ ] نوشتن ۱۰ test case اول

---

## 🔗 منابع و مراجع

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/latest/explanation/fixtures.html)
- [Docker Multi-stage](https://docs.docker.com/build/building/multi-stage/)

---

**تهیه‌شده توسط**: تیم توسعه Econojin  
**تاریخ**: ۲۰۲۴-۰۷-۲۳  
**نسخه**: 1.0  
**وضعیت**: در حال اجرا

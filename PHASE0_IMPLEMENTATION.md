# پیاده‌سازی فاز ۰ — رفع بدهی فنی و تثبیت پایه

**آخرین به‌روزرسانی:** مرداد ۱۴۰۵
**وضعیت:** 🔄 در حال برنامه‌ریزی

---

## فهرست کارها

### T-01: تکمیل Alembic Migrations (تثبیت ساختار پایگاه داده)

#### ۱.۱ بررسی وضعیت فعلی migrations

**وضعیت فعلی:**
- فایل‌های migration موجود:
  - `0001_admin_models.py` — admin_settings, audit_logs, system_reports
  - `0002_core_models.py` — users, conversations, messages, simulation, shared_core, shared_ai, shared_knowledge, shared_sim, api
  - `20260727_0001_baseline_education.py` — courses, lessons, enrollments
  - `20260727_0002_rbac.py` — roles, permissions, role_permissions, user_roles
  - `20260727_0002_users_profile_fields.py` — phone, organization, role columns on users

**مشکلات شناسایی‌شده:**
1. ⚠️ دو migration با revision `20260727_0002` هم‌نام هستند (تعارض)
2. ⚠️ مدل‌های زیر در هیچ migrationای ثبت نشده‌اند:
   - `farms.models.Farm`
   - `crops.models.Crop`
   - `planting.models.PlantingPlan`, `FarmTask`
   - `inventory.models.InventoryItem`
   - `monitoring.models.Sensor`, `SensorReading`, `AlertRule`, `AlertEvent`
   - `simulation.runs.models.SimulationRun`
   - `simulation.scenario.models.Scenario`, `ScenarioResult`, `ComparisonSession`, `ModelChain`
   - `ai_agents.models.Conversation`, `Message`
   - `api.models.accounting.*` (14 مدل)
   - `api.models.agriculture_school.*`
   - `api.models.library.LibraryResource`
   - `api.models.community.Post`, `Comment`, `Like`
   - `api.models.games.*`
   - `shared_knowledge.models.*`
   - `shared_sim.models.*`
3. ⚠️ فایل `model_registry.py` فقط ۱۲ ماژول را ثبت کرده، مدل‌های کلیدی (simulation.runs, simulation.scenario, ai_agents, water, weather و ...) را شامل نمی‌شود
4. ⚠️ از `create_all()` در `session.py` برای محیط local استفاده می‌شود که باید با Alembic جایگزین شود

#### ۱.۲ اقدامات مورد نیاز

```bash
# ۱. اصلاح model_registry.py برای شامل شدن تمام مدل‌ها
# ۲. رفع تعارض revision‌های تکراری (20260727_0002)
# ۳. ایجاد migration یکپارچه برای تمام مدل‌های گمشده
# ۴. غیرفعال کردن create_all() در محیط‌های غیر local
```

**فایل‌های هدف:**
- `alembic/env.py` — اصلاح مسیر import مدل‌ها
- `alembic/versions/` — ایجاد migration جدید
- `apps/shared_core/database/model_registry.py` — افزودن تمام ماژول‌ها
- `apps/shared_core/database/session.py` — جایگزینی create_all

---

### T-02: امنیت و پیکربندی

#### ۲.۱ محدود کردن CORS Origins

**مشکل:** در `apps/main.py` از CORS با `allow_origins=["*"]` استفاده شده که یک ریسک امنیتی است.

**راهکار:** 
- جایگزینی با لیست origins از `settings.BACKEND_CORS_ORIGINS`
- افزودن middleware برای اعتبارسنجی Origin در سطح درخواست

```python
# در main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### ۲.۲ فعال‌سازی Rate Limiting

**مشکل:** rate limiting وجود ندارد یا غیرفعال است.

**راهکار:**
- استفاده از `slowapi` یا پیاده‌سازی middleware اختصاصی
- تنظیم محدودیت‌های پیش‌فرض:
  - عمومی: ۶۰ req/min
  - احراز هویت: ۱۰ req/min
  - APIهای سنگین: ۵ req/min
- ذخیره‌سازی در Redis برای production

#### ۲.۳ مدیریت SECRET_KEY

**مشکل:** کلید پیش‌فرض ضعیف: `"local-dev-only-change-me-use-secrets-token-urlsafe-48"`

**راهکار:**
- ایجاد `.env.example` با توضیحات برای مقداردهی
- افزودن اعتبارسنجی در production (قبلاً در config.py پیاده‌سازی شده)
- افزودن توضیحات کامل برای تولید کلید امن:

```bash
# تولید کلید امن
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

#### ۲.۴ Externalize Hardcoded Values

**فایل‌های شناسایی‌شده با مقادیر hardcoded:**

| فایل | مقدار | راهکار |
|------|-------|--------|
| `apps/main.py` | مسیر `security/` در sys.path | استفاده از settings |
| `apps/water/router.py` | داده‌های static | انتقال به دیتابیس |
| `apps/farms/router.py` | مقادیر mock | اتصال به API واقعی |

---

### T-03: مهاجرت مدل‌های علمی

#### ۳.۱ وضعیت فعلی

مدل‌های علمی در دو مکان وجود دارند:
1. **`scripts/`** — مدل‌های قدیمی (SWAT+, ERA5-Land, Sentinel-2)
2. **`apps/simulation/`** — مدل‌های جدید (RothC, AquaCrop)

#### ۳.۲ اقدامات

- [ ] انتقال مدل‌های `scripts/` به `apps/simulation/`
- [ ] ایجاد API endpoint برای هر مدل علمی
- [ ] یکپارچه‌سازی با Celery برای پردازش ناهمزمان
- [ ] افزودن schemaهای Pydantic برای validation

---

### T-04: استانداردسازی API Responses

#### ۴.۱ ایجاد Response Schema یکنواخت

```python
# apps/shared_core/schemas.py
from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, Any

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None
    error: Optional[str] = None
    pagination: Optional[dict] = None

class PaginatedResponse(APIResponse, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int
```

#### ۴.۲ Error Handling یکنواخت

- ایجاد error handlerهای سفارشی برای HTTPException
- استانداردسازی error codes
- افزودن logging برای تمام خطاها

---

### T-05: پاکسازی Legacy Code

#### ۵.۱ فایل‌های قدیمی برای حذف یا مهاجرت

| مسیر | وضعیت | اقدام |
|------|--------|-------|
| `scripts/main.py` | 🔴 قدیمی | انتقال به `apps/simulation/` |
| `backend/` | 🔴 قدیمی | حذف بعد از تایید عدم استفاده |
| `eco_nojin_dev.py` | 🟡 احتمالی | بررسی و حذف |
| `eco_nojin_manager.py` | 🟡 احتمالی | بررسی و حذف |

#### ۵.۲ مستندسازی

- افزودن توضیحات deprecation برای فایل‌های قدیمی
- به‌روزرسانی README.md

---

### T-06: افزایش Test Coverage

#### ۶.۱ اهداف

- **Backend:** ≥ 70% coverage
- **Frontend:** ≥ 50% coverage (TypeScript)

#### ۶.۲ تست‌های مورد نیاز

| ماژول | تست‌های موجود | تست‌های مورد نیاز |
|-------|--------------|------------------|
| Users/Auth | پایه | کامل (login, register, OTP, refresh) |
| Farms | حداقلی | CRUD کامل |
| Crops | حداقلی | CRUD کامل |
| Monitoring | ندارد | Sensor, Reading, Alert |
| Simulation | Partial | AquaCrop, RothC |
| AI Agents | ندارد | Conversation, Message |
| Accounting | ندارد | کامل |

#### ۶.۳ ابزارها

```bash
# اجرای تست‌ها
pytest apps/ -v --cov=apps --cov-report=term-missing

# بررسی coverage
pytest --cov=apps --cov-report=html
```

---

### T-07: تکمیل TypeScript Types

#### ۷.۱ بسته‌های TypeScript

| بسته | وضعیت | اقدام |
|------|--------|-------|
| `@econojin/types` | 🟡 ناقص | تکمیل types برای API responses |
| `@econojin/api-client` | 🟡 ناقص | افزودن تایپ‌های از دست رفته |
| `@econojin/hooks` | 🟢 مناسب | بررسی و تکمیل |

#### ۷.۲ اولویت‌ها

1. تکمیل types برای Farm, Crop, User
2. افزودن types برای Simulation models
3. types برای Monitoring (Sensor, Reading, Alert)
4. types برای Accounting (Account, Invoice, Payment)

---

### T-08: اتصال صفحات Frontend به API

#### ۸.۱ صفحات Stub/Mock

| صفحه | API مورد نیاز | اولویت |
|------|--------------|--------|
| GIS | satellite router | بالا |
| Community | community router | بالا |
| Education | education router | متوسط |
| Library | library router | متوسط |
| Games | games router | متوسط |
| EcoMining | simulation router | پایین |

---

### T-09: به‌روزرسانی model_registry.py

**وضعیت فعلی:** فقط ۱۲ ماژول ثبت شده است.

**لیست کامل مدل‌ها برای ثبت:**

```python
_MODEL_MODULES = [
    # Core
    "apps.users.models",
    "apps.shared_core.rbac.models",
    "apps.shared_core.models",
    
    # Domain
    "apps.farms.models",
    "apps.crops.models",
    "apps.planting.models",
    "apps.inventory.models",
    "apps.monitoring.models",
    "apps.weather.models",
    "apps.water.models",
    
    # AI & Knowledge
    "apps.ai_agents.models",
    "apps.shared_ai.models",
    "apps.shared_knowledge.models",
    "apps.shared_sim.models",
    
    # Simulation
    "apps.simulation.models",
    "apps.simulation.runs.models",
    "apps.simulation.scenario.models",
    
    # API
    "apps.api.models.accounting",
    "apps.api.models.agriculture_school",
    "apps.api.models.education",
    "apps.api.models.library",
    "apps.api.models.community",
    "apps.api.models.games",
]
```

---

### T-10: اصلاح session.py

**اقدامات:**
1. ✅ قبلاً غیرفعال کردن `create_all()` در محیط غیر local پیاده‌سازی شده
2. ❌ نیاز به افزودن auto-run Alembic upgrade در startup
3. ❌ حذف `_sqlite_schema_patches()` بعد از یکپارچه‌سازی migration

```python
# افزودن به startup
async def run_alembic_upgrade():
    """Run Alembic migrations on startup (non-production)."""
    from alembic.config import Config
    from alembic import command
    
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
```

---

## برنامه زمان‌بندی

### هفته ۱: رفع بدهی‌های بحرانی (۲-۳ روز)

| روز | کار | فایل‌ها |
|-----|-----|---------|
| ۱ | اصلاح model_registry + رفع تعارض revisions | `model_registry.py`, `alembic/versions/` |
| ۲ | ایجاد migration یکپارچه | `alembic/versions/` |
| ۳ | CORS + Rate Limiting + SECRET_KEY | `main.py`, `config.py` |

### هفته ۲: رفع بدهی‌های بالا (۳-۴ روز)

| روز | کار | فایل‌ها |
|-----|-----|---------|
| ۴-۵ | استانداردسازی API responses | `shared_core/schemas.py`, routerها |
| ۶ | مهاجرت مدل‌های علمی | `scripts/` → `apps/simulation/` |
| ۷ | پاکسازی legacy code | حذف/مهاجرت فایل‌های قدیمی |

### هفته ۳: تست و تثبیت (۳-۴ روز)

| روز | کار | فایل‌ها |
|-----|-----|---------|
| ۸-۹ | نوشتن تست‌ها | `tests/`, `apps/conftest.py` |
| ۱۰ | تکمیل TypeScript types | `packages/types/` |
| ۱۱ | اتصال صفحات frontend | `apps/web/src/pages/` |

---

## معیارهای تکمیل

- [ ] تمام مدل‌ها در Alembic registry ثبت شده‌اند
- [ ] migration یکپارچه ایجاد و تست شده است
- [ ] `create_all()` در production غیرفعال شده است
- [ ] CORS origins محدود شده‌اند
- [ ] rate limiting فعال است
- [ ] SECRET_KEY قوی پیش‌فرض شده است
- [ ] API responses استاندارد شده‌اند
- [ ] مدل‌های علمی به `apps/simulation/` منتقل شده‌اند
- [ ] فایل‌های legacy پاکسازی شده‌اند
- [ ] تست coverage ≥ 70% backend
- [ ] TypeScript types کامل شده‌اند
- [ ] صفحات frontend اصلی به API متصل شده‌اند

---

## مستندات فنی اضافی

### ساختار Migration جدید

```python
"""Unified migration: all domain models for Econojin v2.

Revision ID: 20260730_0001
Revises: 20260727_0002_rbac
"""
```

### CORS Configuration در production

```python
# .env.production
BACKEND_CORS_ORIGINS=https://app.econojin.com,https://admin.econojin.com
```

### Rate Limiting Configuration

```python
# پیشنهادی
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=60/minute
RATE_LIMIT_AUTH=10/minute
RATE_LIMIT_SIMULATION=5/minute

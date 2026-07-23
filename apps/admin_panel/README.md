# admin_panel | پنل مدیریت Econojin

> **نکته:** این ماژول **پنل مدیریت** پلتفرم Econojin است.
> شامل مدیریت تنظیمات سیستمی، مشاهده لاگ‌های حسابرسی، گزارش‌های سیستمی و داشبورد مدیریتی.
> تمام endpointهای این ماژول **فقط برای superuser** قابل دسترسی هستند.

## مسئولیت‌ها

این ماژول چهار وظیفه‌ی اصلی دارد:

1. **داشبورد مدیریت** (`GET /admin/`)
   - نمایش خلاصه‌ای از وضعیت سیستم (تعداد کاربران، تنظیمات، لاگ‌ها، گزارش‌ها)

2. **مدیریت تنظیمات سیستمی** (`GET /admin/settings`, `PUT /admin/settings/{key}`)
   - مشاهده و بروزرسانی تنظیمات key-value سیستمی
   - مقداردهی `value`, `description`, `is_active`

3. **مشاهده لاگ‌های حسابرسی** (`GET /admin/audit-logs`)
   - مشاهده رویدادهای ثبت‌شده در سیستم
   - فیلتر بر اساس نوع رویداد (event_type)

4. **مشاهده گزارش‌های سیستمی** (`GET /admin/reports`)
   - مشاهده گزارش‌های تولیدشده توسط سیستم

## ساختار

```
admin_panel/
├── __init__.py                # Module init
├── router.py                  # ★ روتر پنل مدیریت (همه با /admin پیشوند)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # ★ Repositoryهای تخصصی
├── frontend/                  # ★ فرانت‌اند پنل مدیریت (Vite + React)
└── tests/                     # Pytest tests
    └── test_router.py         #   تست روترها
```

## Repositoryهای تخصصی (`repository.py`)

| Repository | مدل | توضیح |
|------------|------|--------|
| `AdminSettingRepository` | `AdminSetting` | جستجوی تنظیمات بر اساس کلید (`get_by_key`) |
| `AuditLogRepository` | `AuditLog` | فیلتر لاگ‌ها بر اساس نوع رویداد (`filter_by_event_type`) |
| `SystemReportRepository` | `SystemReport` | مدیریت گزارش‌های سیستمی (CRUD پایه) |

## Endpointهای API

> **توجه:** تمام endpointهای این ماژول نیاز به **احراز هویت superuser** دارند.

| Method | Path | توضیح | نیازمند |
|--------|------|--------|---------|
| GET | `/admin/` | داشبورد مدیریت | superuser |
| GET | `/admin/settings` | لیست تنظیمات سیستمی | superuser |
| PUT | `/admin/settings/{key}` | بروزرسانی/ایجاد تنظیم | superuser |
| GET | `/admin/audit-logs` | لاگ‌های حسابرسی | superuser |
| GET | `/admin/reports` | گزارش‌های سیستمی | superuser |

### 1. داشبورد مدیریت

```json
// GET /admin/
// Response 200
{
    "total_users": 42,
    "total_settings": 15,
    "total_audit_logs": 1280,
    "total_reports": 7
}
```

### 2. تنظیمات سیستمی

```json
// GET /admin/settings?limit=10&offset=0
// Response 200
[
    {
        "id": 1,
        "key": "site_name",
        "value": "Econojin",
        "description": "نام سایت",
        "is_active": true,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
    }
]
```

**بروزرسانی تنظیم:**
```json
// PUT /admin/settings/site_name
{
    "value": "Econojin Platform",
    "description": "نام رسمی پلتفرم",
    "is_active": true
}
// Response 200
{
    "id": 1,
    "key": "site_name",
    "value": "Econojin Platform",
    ...
}
```

### 3. لاگ‌های حسابرسی

```json
// GET /admin/audit-logs?event_type=login&limit=10
// Response 200
[
    {
        "id": 100,
        "actor": "user@example.com",
        "event_type": "login",
        "description": "ورود کاربر به سیستم",
        "ip_address": "192.168.1.1",
        "created_at": "2025-01-15T10:30:00Z"
    }
]
```

### 4. گزارش‌های سیستمی

```json
// GET /admin/reports?limit=10&offset=0
// Response 200
[
    {
        "id": 1,
        "title": "گزارش عملکرد هفتگی",
        "report_type": "performance",
        "status": "completed",
        "payload": {},
        "created_at": "2025-01-15T10:00:00Z"
    }
]
```

## مدل‌های داده

### AdminSetting
| فیلد | نوع | توضیح |
|------|------|--------|
| `id` | int | شناسه یکتا |
| `key` | str | کلید تنظیم (unique) |
| `value` | str | مقدار تنظیم |
| `description` | str | توضیحات |
| `is_active` | bool | وضعیت فعال بودن |
| `created_at` | datetime | تاریخ ایجاد |
| `updated_at` | datetime | تاریخ بروزرسانی |

### AuditLog
| فیلد | نوع | توضیح |
|------|------|--------|
| `id` | int | شناسه یکتا |
| `actor` | str | عامل رویداد (ایمیل کاربر) |
| `event_type` | str | نوع رویداد (login, logout, setting_change, ...) |
| `description` | str | توضیحات رویداد |
| `ip_address` | str | آدرس IP |
| `created_at` | datetime | تاریخ رویداد |

### SystemReport
| فیلد | نوع | توضیح |
|------|------|--------|
| `id` | int | شناسه یکتا |
| `title` | str | عنوان گزارش |
| `report_type` | str | نوع گزارش (performance, error, usage, ...) |
| `status` | str | وضعیت (pending, running, completed, failed) |
| `payload` | dict | محتوای گزارش |
| `created_at` | datetime | تاریخ ایجاد |

## نمونه درخواست با curl

```bash
# دریافت توکن superuser
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@econojin.com", "password": "changethis"}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# داشبورد
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/admin/

# تنظیمات
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/settings?limit=20"

# بروزرسانی تنظیم
curl -X PUT http://localhost:8000/admin/settings/site_name \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": "Econojin Platform", "description": "Official name", "is_active": true}'

# لاگ‌ها
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/audit-logs?event_type=login&limit=50"

# گزارش‌ها
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/reports?limit=10"
```

## استفاده در کد پایتون

```python
import httpx

# احراز هویت superuser
response = httpx.post("http://localhost:8000/api/v1/auth/login",
    json={"email": "admin@econojin.com", "password": "changethis"})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# دریافت داشبورد
dashboard = httpx.get("http://localhost:8000/admin/", headers=headers).json()
print(f"کاربران: {dashboard['total_users']}")
print(f"تنظیمات: {dashboard['total_settings']}")

# بروزرسانی تنظیم
httpx.put("http://localhost:8000/admin/settings/site_name",
    headers=headers,
    json={"value": "New Site Name"})
```

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/admin_panel/tests/ -v

# اجرای سرور توسعه
python apps/main.py
# یا
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

## متغیرهای محیطی مرتبط (`.env`)

```ini
# حساب superuser پیش‌فرض
FIRST_SUPERUSER=admin@econojin.com
FIRST_SUPERUSER_PASSWORD=changethis    # در production تغییر دهید
```

## تغییرات مهم

- **فاز ۲:** ایجاد پنل مدیریت با ۴ بخش اصلی (داشبورد، تنظیمات، لاگ‌ها، گزارش‌ها)
- **فاز ۲:** پیاده‌سازی repositoryهای تخصصی برای AdminSetting, AuditLog, SystemReport
- **فاز ۲:** اعمال محدودیت دسترسی superuser برای تمام endpointها
- **فاز ۲:** Validation سمت سرور برای بروزرسانی تنظیمات

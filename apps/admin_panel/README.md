# admin_panel | پنل مدیریت Econojin

> **نکته:** این ماژول **پنل مدیریت** پلتفرم Econojin است.
> شامل مدیریت تنظیمات سیستمی، مشاهده لاگ‌های حسابرسی، گزارش‌های سیستمی، مدیریت کاربران،
> پایش سلامت سیستم و داشبورد مدیریتی.
> تمام endpointهای این ماژول **فقط برای superuser** قابل دسترسی هستند.

## مسئولیت‌ها

این ماژول هفت وظیفه‌ی اصلی دارد:

1. **داشبورد مدیریت** (`GET /admin/`)
   - نمایش خلاصه‌ای از وضعیت سیستم (تعداد کاربران، تنظیمات، لاگ‌ها، گزارش‌ها)

2. **مدیریت تنظیمات سیستمی** (`GET /admin/settings`, `PUT /admin/settings/{key}`)
   - مشاهده و بروزرسانی تنظیمات key-value سیستمی
   - مقداردهی `value`, `description`, `is_active`

3. **مشاهده لاگ‌های حسابرسی** (`GET /admin/audit-logs`)
   - مشاهده رویدادهای ثبت‌شده در سیستم
   - فیلتر بر اساس نوع رویداد (event_type)، ایمیل کاربر (actor_email)، بازه زمانی (date_from, date_to)

4. **مشاهده و تولید گزارش‌های سیستمی** (`GET /admin/reports`, `POST /admin/reports`)
   - مشاهده گزارش‌های تولیدشده توسط سیستم
   - تولید گزارش جدید (CSV/JSON)

5. **مدیریت کاربران** (`GET/PATCH/DELETE /admin/users`)
   - لیست کاربران با جستجو و فیلتر (search, role, is_active, is_superuser)
   - مشاهده جزئیات کاربر
   - فعال/غیرفعال کردن کاربر
   - تغییر نقش (superuser/user)
   - حذف کاربر

6. **پایش سلامت سیستم** (`GET /admin/health`)
   - وضعیت دیتابیس و latency
   - تعداد کاربران و کاربران فعال ۲۴ ساعت گذشته
   - تعداد routeهای API
   - محیط اجرا و نسخه پایتون

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
    ├── test_router.py         #   تست روترها (29 تست)
    ├── test_service.py        #   تست سرویس
    ├── test_schemas.py        #   تست اسکیماها
    └── test_repository.py     #   تست ریپازیتوری
```

## Repositoryهای تخصصی (`repository.py`)

| Repository | مدل | توضیح |
|------------|------|--------|
| `AdminSettingRepository` | `AdminSetting` | جستجوی تنظیمات بر اساس کلید (`get_by_key`) |
| `AuditLogRepository` | `AuditLog` | فیلتر لاگ‌ها بر اساس نوع رویداد (`filter_by_event_type`) و پارامترهای چندگانه (`filter_by_params`) |
| `SystemReportRepository` | `SystemReport` | مدیریت گزارش‌های سیستمی (CRUD پایه) |

## Endpointهای API

> **توجه:** تمام endpointهای این ماژول نیاز به **احراز هویت superuser** دارند.

| Method | Path | توضیح | نیازمند |
|--------|------|--------|---------|
| GET | `/admin/` | داشبورد مدیریت | superuser |
| GET | `/admin/settings` | لیست تنظیمات سیستمی | superuser |
| PUT | `/admin/settings/{key}` | بروزرسانی/ایجاد تنظیم | superuser |
| GET | `/admin/audit-logs` | لاگ‌های حسابرسی (با فیلتر) | superuser |
| GET | `/admin/reports` | لیست گزارش‌های سیستمی | superuser |
| POST | `/admin/reports` | تولید گزارش جدید | superuser |
| GET | `/admin/users` | لیست کاربران (با جستجو و فیلتر) | superuser |
| GET | `/admin/users/{id}` | جزئیات کاربر | superuser |
| PATCH | `/admin/users/{id}/status` | فعال/غیرفعال کردن کاربر | superuser |
| PATCH | `/admin/users/{id}/role` | تغییر نقش کاربر | superuser |
| DELETE | `/admin/users/{id}` | حذف کاربر | superuser |
| GET | `/admin/health` | پایش سلامت سیستم | superuser |

### 1. داشبورد مدیریت

```json
// GET /admin/
// Response 200
{
    "user_count": 42,
    "active_user_count": 38,
    "superuser_count": 3,
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

### 3. لاگ‌های حسابرسی (پیشرفته)

```json
// GET /admin/audit-logs?event_type=login&actor_email=admin@example.com&date_from=2025-01-01T00:00:00Z&limit=10
// Response 200
[
    {
        "id": 100,
        "actor_id": 1,
        "actor_email": "admin@example.com",
        "event_type": "login",
        "event_data": "{\"ip\": \"192.168.1.1\"}",
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
        "report_name": "Weekly Performance",
        "status": "completed",
        "report_data": "{\"avg_response\": 120}",
        "created_at": "2025-01-15T10:00:00Z",
        "completed_at": "2025-01-15T10:05:00Z"
    }
]

// POST /admin/reports
// Request
{
    "report_name": "Monthly Summary",
    "report_type": "csv"
}
// Response 201
{
    "id": 2,
    "report_name": "Monthly Summary",
    "status": "completed",
    "message": "Report 'Monthly Summary' generated successfully."
}
```

### 5. مدیریت کاربران

```json
// GET /admin/users?search=ali&role=farmer&is_active=true&limit=20
// Response 200
[
    {
        "id": 1,
        "email": "ali@example.com",
        "full_name": "علی محمدی",
        "phone": "+989123456789",
        "organization": "مزرعه نمونه",
        "role": "farmer",
        "is_active": true,
        "is_superuser": false,
        "created_at": "2025-01-15T10:00:00Z",
        "updated_at": "2025-01-15T10:00:00Z"
    }
]

// PATCH /admin/users/1/status
// Request
{"is_active": false}
// Response 200 (کاربر غیرفعال شد)

// PATCH /admin/users/1/role
// Request
{"is_superuser": true}
// Response 200 (کاربر به superuser ارتقا یافت)

// DELETE /admin/users/1
// Response 204 (کاربر حذف شد)
```

### 6. پایش سلامت سیستم

```json
// GET /admin/health
// Response 200
{
    "database": "healthy",
    "database_latency_ms": 1.23,
    "redis": "not_configured",
    "redis_latency_ms": null,
    "uptime_seconds": 3600.5,
    "total_users": 42,
    "active_users_last_24h": 5,
    "total_api_routes": 15,
    "environment": "local",
    "python_version": "3.12"
}
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
| `actor_id` | int | شناسه کاربر عامل رویداد |
| `actor_email` | str | ایمیل کاربر عامل رویداد |
| `event_type` | str | نوع رویداد (login, logout, setting_change, ...) |
| `event_data` | str | داده‌های رویداد (JSON) |
| `created_at` | datetime | تاریخ رویداد |

### SystemReport
| فیلد | نوع | توضیح |
|------|------|--------|
| `id` | int | شناسه یکتا |
| `report_name` | str | عنوان گزارش |
| `status` | str | وضعیت (pending, running, completed, failed) |
| `report_data` | str | محتوای گزارش |
| `created_at` | datetime | تاریخ ایجاد |
| `completed_at` | datetime | تاریخ تکمیل |

## نمونه درخواست با curl

```bash
# دریافت توکن superuser
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@econojin.com", "password": "*****"}' \
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

# لاگ‌ها با فیلتر
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/audit-logs?event_type=login&limit=50"

# گزارش‌ها
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/reports?limit=10"

# تولید گزارش
curl -X POST http://localhost:8000/admin/reports \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"report_name": "Monthly Summary", "report_type": "csv"}'

# لیست کاربران
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/users?search=ali&is_active=true"

# جزئیات کاربر
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/users/1"

# فعال/غیرفعال کردن کاربر
curl -X PATCH http://localhost:8000/admin/users/2/status \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_active": false}'

# تغییر نقش کاربر
curl -X PATCH http://localhost:8000/admin/users/2/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_superuser": true}'

# حذف کاربر
curl -X DELETE http://localhost:8000/admin/users/3 \
  -H "Authorization: Bearer $TOKEN"

# سلامت سیستم
curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/admin/health"
```

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/admin_panel/tests/ -v

# اجرای تست‌های روتر (29 تست)
pytest apps/admin_panel/tests/test_router.py -v

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
- **فاز ۱ (تکمیل):** افزودن ۷ endpoint جدید (مدیریت کاربران، سلامت سیستم، تولید گزارش)
- **فاز ۱ (تکمیل):** فیلتر پیشرفته لاگ‌ها (event_type, actor_email, date_from, date_to)
- **فاز ۱ (تکمیل):** ۲۹ تست واقعی با پوشش کامل endpointها
- **فاز ۱ (تکمیل):** جلوگیری از حذف/غیرفعال کردن خود توسط superuser
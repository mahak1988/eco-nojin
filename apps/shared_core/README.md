# shared_core | مرجع رسمی لایه اشتراکی پلتفرم Econojin

> **نکته:** این ماژول **مرجع رسمی** لایه اشتراکی (shared) برای کل پلتفرم Econojin است.
> ماژول قدیمی `apps/shared` (قالب auto-scaffolded خالی) در تاریخ ۱۴۰۵/۰۴/۲۶ منسوخ و
> حذف شد. همه‌ی مدل‌ها، Base، session و repository مرکزی باید از همین‌جا تأمین شوند.

## مسئولیت‌ها

این ماژول سه وظیفه‌ی اصلی دارد:

1. **زیرساخت پایه‌ی دیتابیس** (`database/`)
   - `Base` (DeclarativeBase) که همه‌ی مدل‌های ORM از آن ارث می‌برند.
   - `engine` و `async_session_maker` برای SQLAlchemy 2.0 Async.
   - `get_db_session` Dependency برای FastAPI.
   - `init_db` / `close_db` برای lifespan اپلیکیشن.
2. **Repository عمومی** (`database/repository.py`)
   - `BaseRepository[T]` با CRUD کامل (get/get_multi/create/update/delete/count).
3. **مدل‌های مشترک** (`models.py`)
   - `SharedCore`, `AdminSetting`, `AuditLog`, `SystemReport`.

## ساختار

```
shared_core/
├── __init__.py                # Module init (version = 1.0.0)
├── models.py                  # ORM models مشترک
├── schemas.py                 # Pydantic schemas پایه
├── service.py                 # Business logic مشترک
├── repository.py              # (سطح بالا) - wrapper روی BaseRepository
├── router.py                  # FastAPI router مشترک (در صورت نیاز)
├── dependencies.py            # Dependencies مشترک
├── database/
│   ├── __init__.py
│   ├── session.py             # Engine, Base, get_db_session, init_db
│   └── repository.py          # BaseRepository[T] - CRUD عمومی
└── tests/                     # Pytest tests
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

## نحوه‌ی استفاده

### Dependency Injection در FastAPI

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared_core.database.session import get_db_session

async def my_endpoint(db: AsyncSession = Depends(get_db_session)):
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
```

## اجرای سرور توسعه

```bash
uvicorn apps.main:app --reload
```

## تغییرات مهم

- **۱۴۰۵/۰۴/۲۶:** ماژول `apps/shared` قدیمی حذف شد. این ماژول قالب خالی auto-scaffolded
  بود و هیچ کد واقعی نداشت. همه‌ی ارجاعات باید به `apps.shared_core` هدایت شوند.

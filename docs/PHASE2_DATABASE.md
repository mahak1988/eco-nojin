# فاز ۲ — دیتابیس local-first (SQLite)

**هدف:** `alembic upgrade head` بدون خطای `table already exists` روی دیتابیس‌هایی که با `create_all` ساخته شده‌اند.

## زنجیره revision

```
Branch A: 20260727_0001 ... -> 20260729_0001
Branch B: 0001_admin_models -> 0002_core_models
Merge:    20260729_0002 (0002_core_models + 20260729_0001)
```

مهاجرت‌های `0001` / `0002` و بسیاری از revisionهای 20260728+ **idempotent** هستند (اگر جدول باشد، skip).

## دستورات

```powershell
cd D:\econojin.com
git pull origin main

$env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
$env:PYTHONPATH = "D:\econojin.com"

.\scripts\alembic_upgrade_safe.ps1
# یا:
# .\.venv\Scripts\python.exe -m alembic upgrade head
```

اگر هنوز خطا:

```powershell
.\.venv\Scripts\python.exe -m alembic stamp heads
.\.venv\Scripts\python.exe -m alembic current
```

## معیار پذیرش فاز ۲

- [ ] `alembic heads` یک merge head واحد (`20260729_0002`) یا heads بدون error
- [ ] `alembic upgrade head` exit 0
- [ ] API `database: ok` بعد از restart
- [ ] جداول admin/users/courses بدون خطای runtime

## یادداشت

- Production/Postgres: فقط Alembic؛ `create_all` فقط در `ENVIRONMENT=local`.
- Schema drift ستون‌های crops/users: `session._sqlite_schema_patches`.

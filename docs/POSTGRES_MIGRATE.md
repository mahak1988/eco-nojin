# مهاجرت از SQLite به PostgreSQL

## چرا؟

SQLite برای توسعهٔ سریع local مناسب است. در production / multi-user باید **PostgreSQL 16** (+ در آینده PostGIS) استفاده شود.

## مراحل (خلاصه)

1. نصب Postgres و ساخت دیتابیس:

```sql
CREATE USER econojin WITH PASSWORD 'strong_password';
CREATE DATABASE econojin OWNER econojin;
```

2. در `.env`:

```env
ENVIRONMENT=local
DATABASE_URL=postgresql+asyncpg://econojin:strong_password@localhost:5432/econojin
```

3. نصب درایور:

```powershell
pip install asyncpg psycopg2-binary
```

4. Migration با Alembic (نه فقط create_all):

```powershell
alembic upgrade head
```

5. Seed:

```powershell
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/rbac/seed
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/seed-demo
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/accounting/seed-demo
```

## نکتهٔ مهم local فعلی

اگر `DATABASE_URL` به‌صورت `postgresql://` **بدون** `+asyncpg` باشد و `ENVIRONMENT=local`، کد فعلی عمداً به SQLite fallback می‌کند. برای اجبار Postgres:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/econojin
```

و `asyncpg` نصب باشد.

## SQLite schema drift

`create_all` ستون جدید به جدول موجود اضافه نمی‌کند. در local، `init_db` اکنون ستون‌های `phone` / `organization` / `role` را با `ALTER TABLE` روی SQLite وصله می‌کند. در Postgres همیشه از Alembic استفاده کنید.

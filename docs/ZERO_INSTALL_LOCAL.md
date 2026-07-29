# پشتهٔ محلی بدون Docker — استاندارد امن برای ایران

## چرا Docker را کنار می‌گذاریم؟

| مشکل Docker در ایران / ویندوز | اثر |
|------------------------------|-----|
| نصب سنگین (WSL2 + Hyper-V + Desktop) | زمان و رم زیاد |
| دانلود image از Docker Hub | قطع/کندی شبکه |
| سرویس پس‌زمینه همیشگی | مصرف منابع |
| خطای «docker is not recognized» | توقف کامل توسعه |

**جایگزین رسمی پروژه:** فقط **Python + venv + SQLite + npm** — بدون نرم‌افزار اضافه.

---

## معماری جایگزین (Local-First)

```
┌─────────────────────────────────────────────┐
│  شما (Windows)                              │
│  Python 3.11/3.12  →  .venv                 │
│  SQLite file: apps/econojin.db              │
│  uvicorn :8000                              │
│  Vite (npm) :5173                           │
│  Background jobs: sync / in-process (local) │
└─────────────────────────────────────────────┘
         ▲ بدون Postgres/Redis/Docker
```

| نقش در production | جایگزین محلی | نصب اضافه؟ |
|-------------------|--------------|------------|
| PostgreSQL + PostGIS | **SQLite** (`aiosqlite`) | خیر |
| Redis + Celery | اجرای sync در process یا صف سادهٔ حافظه | خیر |
| Docker Compose | `scripts/run_local.ps1` | خیر |
| TLS / COOKIE_SECURE | `COOKIE_SECURE=false` فقط local | — |

**امنیت local (حداقل قابل قبول):**
- `ENVIRONMENT=local` → docs باز، rate-limit سخت‌گیرانه کمتر
- CORS فقط `localhost:5173` / `127.0.0.1`
- Secret از `.env` — نه hardcode
- در production: Postgres + Redis + COOKIE_SECURE + RS256 اجباری می‌ماند

---

## پیش‌نیاز (فقط یک‌بار)

1. **Python 3.11 یا 3.12** از [python.org](https://www.python.org/downloads/)  
   تیک «Add python.exe to PATH» را بزنید.
2. **Node.js 18+** (برای فرانت) از nodejs.org یا نسخهٔ portable.
3. **Git** (احتمالاً دارید).

هیچ‌کدام Docker / WSL / Hyper-V نیستند.

---

## یک دستور اجرا (API)

از پوشه‌ای که `apps\main.py` در آن است:

```powershell
cd D:\econojin.com\eco-nojin   # یا مسیر واقعی مخزن
git pull origin main
.\scripts\run_local.ps1
```

اسکریپت:
1. ریشهٔ مخزن را پیدا می‌کند
2. `VIRTUAL_ENV` خراب را پاک می‌کند
3. `.venv` را می‌سازد یا تعمیر می‌کند
4. `requirements.txt` را نصب می‌کند
5. `DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db` می‌گذارد
6. `uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000` را اجرا می‌کند

**استفاده نکنید:** `uv run` مگر uv را عمداً برای همین ریشه تنظیم کرده باشید (خطای «no Python executable»).

### تعمیر فقط venv

```powershell
.\scripts\fix_venv.ps1
python -m uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

### فرانت

```powershell
cd apps\web
npm install
npm run dev
```

### سلامت

```powershell
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
# انتظار: "database":"ok"
```

---

## اگر schema قدیمی است (ستون کم)

خطاهایی مثل `no such column: users.phone` یا `crops.planting_method` یعنی فایل SQLite قدیمی‌تر از مدل ORM است.

**راه‌حل توسعه (سریع):**

```powershell
# بکاپ
Copy-Item .\apps\econojin.db .\apps\econojin.db.bak -ErrorAction SilentlyContinue
Remove-Item .\apps\econojin.db -ErrorAction SilentlyContinue
# restart uvicorn → create_all جداول جدید می‌سازد
# سپس seed:
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/seed-demo
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/rbac/seed
```

**راه‌حل استانداردتر:** `alembic upgrade head` وقتی migrationها با SQLite سازگارند (`ALEMBIC_USE_SQLITE=1`).

---

## Postgres اختیاری (بدون Docker)

اگر بعداً PostGIS لازم شد **بدون Docker**:

| گزینه | توضیح |
|--------|--------|
| [Neon](https://neon.tech) / Supabase رایگان | فقط `DATABASE_URL` در `.env` — نصب محلی صفر |
| Postgres portable ZIP | فقط برای ماشین قوی؛ اختیاری |

برای فاز ۱ کشاورزی، **SQLite کافی و توصیه‌شده** است.

---

## محدودیت صادقانه

| قابلیت | Local SQLite | Production Postgres |
|--------|--------------|---------------------|
| CRUD مزرعه/محصول/آب | ✅ | ✅ |
| Auth + cookie | ✅ | ✅ |
| PostGIS spatial index | ❌ (fallback بدون geom) | ✅ |
| Celery worker واقعی | ⚠️ sync/stub | ✅ |
| حجم دادهٔ بزرگ | محدود | مقیاس‌پذیر |

این محدودیت‌ها عمداً پذیرفته می‌شوند تا توسعه در ایران بدون Docker متوقف نشود.

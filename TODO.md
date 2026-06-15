# Econojin — TODO (وضعیت توسعه)

آخرین هم‌خوانی با مخزن: **خرداد ۱۴۰۵** · بک‌اند canonical: `api/main.py` · فرانت canonical: `apps/web`

---

## خلاصه پیشرفت

| فاز | وضعیت |
|-----|--------|
| P0 — یکپارچگی و DB پایه | تقریباً کامل |
| P1 — API/UI production | در حال انجام |
| P2 — علمی / بلاکچین / داده واقعی | آغاز شده |
| استقرار و مستندات | آماده اولیه (Vercel + Neon + Docker) |

---

## انجام‌شده (Done)

### بک‌اند (`api/`)
- [x] FastAPI یکپارچه در `api/main.py` (۱۵+ روتر ماژول)
- [x] Auth JWT + پروفایل + OTP (`/auth/otp/request`, `/auth/otp/verify`)
- [x] SMS: Kavenegar و Twilio (`api/services/sms.py`)
- [x] Farmer و Calendar و Store — ORM + CRUD async (SQLite/Postgres)
- [x] Dashboard stats، Simulation (RothC-full، AquaCrop، coupling)
- [x] AI chat با LLM اختیاری OpenAI/Azure + fallback
- [x] EcoCoin ماینر طبیعی (`api/services/eco_miner.py`)
- [x] امنیت: Security headers، Rate limit، `require_write_auth`
- [x] تست‌ها: `tests/test_api_core.py`, `tests/test_otp_sms.py`, `tests/conftest.py`

### فرانت (`apps/web`)
- [x] Next.js 14، مسیرهای `/fa` و `/en` (next-intl)
- [x] داشبورد زنده، `ModuleDashboard`، MediaHero، Logo
- [x] اتصال API: weather، accounting، calendar (فرم+حذف)، GIS (Leaflet)
- [x] farmers، store (فرم ثبت)، ecomining، simulation
- [x] ورود OTP، middleware محافظت مسیر، React Query (تقویم/فروشگاه)
- [x] چت‌بات شناور AI، Playwright e2e (`e2e/auth-farmers.spec.ts`)

### زیرساخت و مستندات
- [x] `.env.example`، `apps/web/.env.example`
- [x] `docker/Dockerfile.api`، `docker-compose.apps.yml`
- [x] CI: `.github/workflows/econojin-apps-ci.yml`
- [x] `README.md`، `docs/ROADMAP_FA.md`، `docs/SECURITY.md`
- [x] `docs/DEPLOY_VERCEL_NEON.md`، `docs/FREE_STACK.md`
- [x] پنل admin اولیه: داشبورد، ماژول‌ها، کشاورزان، AI، شبیه‌ساز

---

## P0 — باقی‌مانده (الزامی برای production پایدار)

- [ ] **Alembic migrations** برای Postgres/PostGIS (جایگزین `create_all` تنها)
- [ ] هماهنگ‌سازی یا حذف `scripts/main.py` و `backend/` legacy (یک entry point)
- [ ] تست‌های DB جامع: `tests/test_database.py` + پوشش OTP با `OTP_DEV_MODE=false` (mock SMS)
- [ ] `REQUIRE_AUTH_FOR_WRITES=true` در production + تست E2E با توکن واقعی

---

## P1 — پایداری API و UI

- [ ] Response/error schema یکنواخت در همه ماژول‌ها
- [ ] CRUD واقعی با DB برای: education، library، community، games، desktop، psychology
- [ ] CORS و `ALLOWED_ORIGINS` دقیق per-environment (بدون `*` در prod)
- [ ] صفحات stub → فرم create/edit/delete در هر ماژول
- [ ] Supabase: حذف یا یکپارچه‌سازی با JWT داخلی (فعلاً OTP/JWT اصلی است)
- [ ] PWA و service worker (آفلاین‌اول)

---

## P2 — علمی، داده و بلاکچین

- [ ] اتصال کامل AquaCrop از `scripts/` یا پکیج FAO (فراتر از stub)
- [ ] SWAT+ / coupling engine از `scripts/coupling_engine.py`
- [ ] Fetchers ERA5-Land، Sentinel-2، CHIRPS
- [ ] ذخیره نتایج simulation در DB + lineage
- [ ] PostGIS برای GIS و مختصات مزرعه
- [ ] قرارداد `contracts/ECO.sol` + oracle و ثبت on-chain
- [ ] Celery/Redis برای jobهای سنگین simulation

---

## شبیه‌ساز — نقشه تفصیلی

| مرحله | وضعیت | کار |
|--------|--------|-----|
| فاز 1 | جزئی | RothC-full در API؛ schemas رسمی برای همه مدل‌ها |
| فاز 2 | باز | Worker async، cache، batch، progress stream |
| فاز 3 | باز | داده ماهواره‌ای واقعی، PostGIS، تاریخچه نتایج |

---

## استقرار و DevOps

- [ ] استقرار واقعی Vercel (web) + Render (API) + Neon (DB) با env production
- [ ] Secrets در GitHub Actions (بدون commit)
- [ ] Health check و monitoring (Uptime / Sentry)
- [ ] `apps/cms` (Strapi) در صورت نیاز محتوا

---

## تست و کیفیت

- [x] `tests/test_api_core.py`
- [x] `tests/test_otp_sms.py`
- [ ] پوشش pytest > ۷۰٪ برای `api/modules`
- [ ] Playwright: calendar create، store CRUD، تغییر locale
- [ ] Load test (k6/Locust) برای `/health` و auth

---

## ثبت تاریخچه (Changelog خلاصه)

| تاریخ | مورد |
|--------|------|
| — | ایجاد TODO و یکپارچه‌سازی `api/main.py` |
| — | Auth/Farmer DB، calendar/weather API |
| — | ModuleDashboard، admin، امنیت چندلایه |
| — | OTP، GIS Leaflet، AI، simulation، i18n [locale] |
| — | SMS/LLM/RothC-full، store CRUD، Logo، docs استقرار |
| خرداد ۱۴۰۵ | بروزرسانی `README.md` و `TODO.md` |

---

## اولویت پیشنهادی هفته بعد

1. Alembic + Neon `DATABASE_URL` در staging  
2. CRUD DB برای ۲–۳ ماژول پرکاربرد (education، community)  
3. استقرار Vercel + Render با `DEPLOY_VERCEL_NEON.md`  
4. غیرفعال کردن `scripts/main.py` در مستندات به‌عنوان deprecated  
این پایان نیست، بلکه آغاز یک جنبش است. 🌱

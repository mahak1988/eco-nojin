# 📋 برنامه توسعه eco-nojin — نسخه ۲.۰

> **تاریخ:** ۱۴۰۵-۰۸-۱۱ (بهروزرسانی پس از استخراج فایلهای مخزن)  
> **مبنای شواهد:** بررسی فایلهای `docker-compose.dev.yml`، `Dockerfile`، `package.json`، `apps/main.py`، `requirements.txt`، مطالعه ۲۴ ماژول `apps/`، استخراج ۵ فایل از `fix/ecocoin-typescript-errors`  
> **اصل راهنما:** هزینه صفر (استفاده از ابزارهای open-source و رایگان)

---

## ۱. وضعیت فعلی پروژه (بر اساس شواهد بهروزرسانیشده)

| مؤلفه | وضعیت شناساییشده |
|---|---|
| زبان Backend | Python 3.12 (FastAPI + uvicorn) |
| زبان Frontend | Node 22 (Vite + pnpm + Turbo monorepo) |
| پایگاه داده | PostgreSQL 17 + PostGIS 17.3.5 (لوکال: SQLite) |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| احراز هویت | JWT (python-jose) + bcrypt + argon2 + passlib |
| کش/صف | Redis + Celery (sync stub در Zero-Install mode) |
| نظارت | Sentry (اختیاری) |
| تست | pytest + pytest-asyncio — **۱۰۵ passed، ۱۲ skipped** |
| API Routes | **۳۷۷ route** در ۵۲ روتر ثبتشده در `apps/main.py` |
| ماژولهای apps | **۲۴ ماژول** (admin_panel، ai_agents، api، cms، content، crops، dashboard، economics، farms، inventory، library، ml، monitoring، notifications، planting، risks، satellite، shared_ai، shared_core، shared_knowledge، shared_sim، simulation، spider_security، users، water، weather، web) |
| فایلهای استخراجشده | ۵ فایل از `fix/ecocoin-typescript-errors`: `test_education.py`، `test_games.py`، `Sidebar.tsx`، `ar.json`، `ur.json` |

---

## ۲. معماری شناساییشده

```
┌─────────────────────────────────────────────────────┐
│  Web (Vite/React — پورت ۵۱۷۳)                        │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/JSON
┌──────────────────────▼──────────────────────────────┐
│  API (FastAPI — پورت ۸۰۰۰)                           │
│  apps/main.py → ۵۰+ روتر                             │
│  ── users/auth ── farms/crops/water/planting         │
│  ── satellite/ml/weather/risks/economics/ecocoin     │
│  ── simulation/ai_agents/admin_panel/notifications   │
│  ── shared_core (security, database, config)         │
└──────────────────────┬──────────────────────────────┘
                       │ asyncpg
┌──────────────────────▼──────────────────────────────┐
│  PostgreSQL 17 + PostGIS (پورت ۵۴۳۲)                 │
│  ── Spatial data ── Farms ── MRV ── Ecocoin          │
└─────────────────────────────────────────────────────┘
```

**لایهها:**
1. **Presentation:** Web (port 5173) + Admin Panel + CMS
2. **Application:** FastAPI با روترهای ماژولار
3. **Domain:** shared_core, shared_ai, shared_sim, shared_knowledge
4. **Infrastructure:** PostgreSQL/PostGIS, Redis, Celery

---

## ۳. برنامه توسعه — فازبندی (بهروزرسانیشده)

### ✅ فاز ۰: راهاندازی و راستیآزمایی محیط لوکال (کامل شد)
**اهداف:** اجرای baseline و اطمینان از سالم بودن سیستم قبل از هر تغییری

| گام | اقدام | وضعیت |
|---|---|---|
| ۰.۱ | بررسی پیکربندیها (۱۲+ فایل کلیدی) | ✅ کامل |
| ۰.۲ | نصب وابستگیهای Python | ✅ کامل (۳۹+ پکیج موجود) |
| ۰.۳ | اجرای تستهای baseline | ✅ **۱۰۵ passed، ۱۲ skipped** |
| ۰.۴ | بررسی import اپ | ✅ ۵۲ روتر، ۳۷۷ route بدون خطا |
| ۰.۵ | اصلاح تست `test_transfer_success` | ✅ `pending` → `confirmed` |
| ۰.۶ | استخراج فایلهای مخزن به لوکال | ✅ ۵ فایل از `fix/ecocoin-typescript-errors` |
| ۰.۷ | مطالعه ۲۴ ماژول apps | ✅ satellite، ml، shared_core بررسی عمیق شد |
| ۰.۸ | Commit و Push به GitHub | ✅ `137381b` + `7f5e6ae` روی `feature/benchmark-first` |

**معیار پذیرش:** ✅ تحقق یافت — تمام ۵۲ روتر بارگذاری شد و `pytest` سبز است.

---

### ⬜ فاز ۱: تکمیل تستها و زیرساخت هسته
**اهداف:** افزایش پوشش تست، امنیت، یکپارچگی و قابلیت نگهداری

**یافتههای ساختاری (شواهدمحور):**
- `shared_core/` شامل: database، geo (PostGIS)، middleware (rate_limit، audit_log، security_middleware)، monitoring (Sentry)، rbac، websocket، zero_trust_security
- `satellite/` شامل: ۷ provider (GEE، Copernicus، Planetary، OpenTopo، SoilMoisture، Synthetic، Thermal)، ۳ processor (NDVI، indices، change_detection)، fetcher Sentinel-2
- `ml/` شامل: classical، features، sensitivity، global_sensitivity، synthetic_data
- `economics/` — **خالی** (فقط پوشه لوکال، نیازمند پیادهسازی)
- ۱۲ تست skip شده (stub) نیازمند جایگزینی با تستهای واقعی

| گام | اقدام |
|---|---|
| ۱.۱ | جایگزینی ۱۲ تست stub با تستهای واقعی (test_api.py، test_router.py، test_schemas.py، test_service.py) |
| ۱.۲ | افزودن تست برای ماژولهای فاقد پوشش: satellite، ml، farms، water، weather، risks |
| ۱.۳ | فعالسازی تستهای استخراجشده: `test_education.py`، `test_games.py` |
| ۱.۴ | بازبینی کامل ماژول `spider_security` (ضد XSS/CSRF/SQLi) |
| ۱.۵ | اطمینان از اعمال rate limiting روی همه روترها (middleware/rate_limit.py موجود است) |
| ۱.۶ | یکپارچهسازی audit log در تمام عملیات حساس (middleware/audit_log.py موجود است) |
| ۱.۷ | استانداردسازی پاسخ خطا (الگوی یکسان `error.code/message/details/request_id` — در main.py پیادهسازی شده) |
| ۱.۸ | بازبینی مدیریت secrets — حذف `SECRET_KEY=dev-secret...` از docker-compose و انتقال به vault |
| ۱.۹ | پیادهسازی `apps/economics/` (در حال حاضر خالی است) |
| ۱.۱۰ | اصلاح pre-commit hook (مسیر اشتباه `eco-nojin\.pre-commit-config.yaml`) |
| ۱.۱۱ | اصلاح هشدار `python-dotenv` (خطوط ۹۴-۹۵ `.env`) |

**معیار پذیرش:** پوشش تست > ۶۰٪؛ اسکن `bandit` بدون خطای high/critical؛ تست auth برای همه endpoint ها.

---

### ⬜ فاز ۲: توسعه ماژولهای تخصصی (parity با پلتفرمهای مرجع)
**اهداف:** رسیدن به همسطح یا فراتر از پلتفرمهای مشابه (با هزینه صفر)

**وضعیت فعلی ماژولها (شواهدمحور):**
- `satellite/` — ✅ زیرساخت قوی (۷ provider، ۳ processor، Sentinel-2 fetcher) — نیازمند فعالسازی provider های رایگان
- `ml/` — ✅ ساختار موجود (classical، features، sensitivity) — نیازمند مدلهای پیشبینی واقعی
- `economics/` — ❌ **خالی** — نیازمند پیادهسازی کامل
- `ecocoin` (در `apps/api/routes/`) — ✅ ۷۴۲ خط پیادهسازی (transfer، staking، mining، verify، challenges، burn)
- `weather/` — نیازمند بررسی عمیق
- `water/` — نیازمند بررسی عمیق
- `risks/` — نیازمند بررسی عمیق

| ماژول | اقدام | پلتفرم مشابه (مرجع) | منبع رایگان |
|---|---|---|---|
| `satellite` | فعالسازی provider های رایگان (Copernicus، Planetary Computer)، بهبود processors | Google Earth Engine, Sentinel Hub | Sentinel-2 (ESA)، Landsat (USGS)، Microsoft Planetary Computer |
| `ml` | پیادهسازی مدلهای پیشبینی بازده با دادههای FAO | IBM Watson Agriculture, FBN | scikit-learn + دادههای FAO رایگان |
| `economics` | **پیادهسازی کامل** (در حال حاضر خالی) — مدلهای هزینه-فایده، تحلیل اقتصادی | Regen Network, Toucan Protocol | استانداردهای Verra/GS (رایگان) |
| `ecocoin` | بهبود توکنومیک، یکپارچهسازی قراردادهای Solidity | Regen Network, Toucan Protocol | قراردادهای موجود در `contracts/` |
| `weather` | پیشبینی کوتاهمدت با دادههای رایگان | Climate FieldView, aWhere | Open-Meteo API (رایگان، بدون API key) |
| `water` | مدیریت بهینه مصرف آب، مدل هیدرولوژیک | Netafim, CropX | مدلهای FAO AquaCrop (مفهومی موجود) |
| `risks` | موتور هشدار زودهنگام چندعاملی | Descartes Labs | ترکیب داده EO + مدلهای آماری |

**اصل هزینه صفر:** استفاده از API های رایگان و open data (Sentinel, NOAA, Open-Meteo, USGS, Planetary Computer) بهجای سرویسهای پولی.

---

### ⬜ فاز ۳: تست، امنیت و بهینهسازی
**اهداف:** تضمین کیفیت و امنیت production-ready

| گام | اقدام |
|---|---|
| ۳.۱ | پوشش تست واحد + یکپارچهسازی برای هر ماژول (هدف: > ۶۰٪) |
| ۳.۲ | تست boundary/negative/edge-case برای محاسبات اقتصادی و پیشبینی |
| ۳.۳ | اجرای `bandit`، `safety check`، `pip-audit` |
| ۳.۴ | تحلیل performance با ابزارهای ماژول `monitoring/` |
| ۳.۵ | تست بار (همزمانی، رفتار تحت حجم بالا) |
| ۳.۶ | رفع ۲۴ هشدار pytest (StarletteDeprecationWarning، datetime.utcnow) |

---

### ⬜ فاز ۴: استقرار و انتشار
**اهداف:** استقرار لوکال + آپلود نهایی به GitHub

| گام | اقدام |
|---|---|
| ۴.۱ | تست کامل `docker-compose.prod.yml` بهصورت لوکال (یا Neon/Supabase رایگان) |
| ۴.۲ | بررسی `liara.json` (استقرار ابری ایرانی) |
| ۴.۳ | merge `feature/benchmark-first` به `main` |
| ۴.۴ | commit با پیامهای معنایی (Conventional Commits) |
| ۴.۵ | push نهایی به `origin` (تأیید شده: `https://github.com/mahak1988/eco-nojin.git`) |
| ۴.۶ | تنظیم GitHub Actions (فایل `ci-admin-panel.yml` موجود است) |

---

## ۴. تحلیل هزینه صفر

| نیازمندی | راهکار رایگان |
|---|---|
| پایگاه داده | PostgreSQL/PostGIS (open-source) |
| محاسبات ابری | رایانش لوکال + سرور Liara (pricing مناسب ایران) |
| تصاویر ماهوارهای | Sentinel-2 (رایگان، ESA)، Landsat (رایگان، USGS) |
| داده آبوهوا | Open-Meteo (رایگان) ، NOAA API (رایگان) |
| هوش مصنوعی | مدلهای open-source (llama, mistral) + LangChain |
| CI/CD | GitHub Actions (رایگان برای public repo) |
| نظارت | Prometheus + Grafana (self-hosted) |

---

## ۵. ریسکها و چالشها

| ریسک | شدت | راهکار |
|---|---|---|
| پیچیدگی monorepo (۱۵+ اپ) | متوسط | تفکیک واضح ماژولها + مستندسازی |
| همبستگی ماژولها | متوسط | تست یکپارچهسازی منظم |
| وابستگی به API خارجی | کم | لایه abstraction با fallback |
| مدیریت secrets | زیاد | انتقال به vault + غیرفعالسازی hard-coded secrets |

---

## ۶. معیارهای موفقیت نهایی

- [x] فاز ۰ کامل: تستها سبز (۱۰۵ passed)، ۵۲ روتر بدون خطا، push به GitHub
- [ ] پوشش تست > ۶۰٪ برای ماژولهای اصلی
- [ ] اسکن امنیتی بدون یافته critical
- [ ] همسطح بودن ماژولها با پلتفرمهای مرجع (جدول فاز ۲)
- [ ] پیادهسازی `apps/economics/` (در حال حاضر خالی)
- [ ] استقرار موفق لوکال
- [ ] merge به `main` و push نهایی به GitHub با تاریخچه تمیز

---

## ۷. خلاصه یافتههای استخراج (فاز ۰.۶)

### فایلهای استخراجشده از `fix/ecocoin-typescript-errors`:
| فایل | نوع | محتوا |
|---|---|---|
| `apps/api/tests/test_education.py` | تست | تستهای ماژول آموزش |
| `apps/api/tests/test_games.py` | تست | تستهای ماژول بازیها |
| `apps/web/src/components/Sidebar.tsx` | Frontend | کامپوننت Sidebar |
| `apps/web/src/i18n/locales/ar.json` | i18n | ترجمه عربی |
| `apps/web/src/i18n/locales/ur.json` | i18n | ترجمه اردو |

### وضعیت branch ها:
- `origin/main` و `HEAD` (feature/benchmark-first) از نظر فایلهای apps یکسان هستند
- `fix/ecocoin-typescript-errors` دارای ۵ فایل اضافی بود که استخراج شد
- سایر branch ها (ecocoin-full-p0-p4، ecocoin-p0-p3، ecocoin-p4، p21-e2e-ci-lighthouse) تفاوتی با HEAD نداشتند

---

*این سند بر اساس شواهد جمعآوریشده از مخزن تهیه شده و بهروزرسانی خواهد شد.*

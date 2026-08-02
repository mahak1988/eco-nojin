# 📋 برنامه توسعه eco-nojin — نسخه ۱.۰

> **تاریخ:** ۱۴۰۵-۰۸-۱۱  
> **مبنای شواهد:** بررسی فایلهای `docker-compose.dev.yml`، `Dockerfile`، `package.json`، `apps/main.py`، `requirements.txt`  
> **اصل راهنما:** هزینه صفر (استفاده از ابزارهای open-source و رایگان)

---

## ۱. وضعیت فعلی پروژه (بر اساس شواهد)

| مؤلفه | وضعیت شناساییشده |
|---|---|
| زبان Backend | Python 3.12 (FastAPI + uvicorn) |
| زبان Frontend | Node 22 (Vite + pnpm + Turbo monorepo) |
| پایگاه داده | PostgreSQL 17 + PostGIS 17.3.5 |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| احراز هویت | JWT (python-jose) + bcrypt + argon2 + passlib |
| کش/صف | Redis + Celery |
| نظارت | Sentry (اختیاری) |
| تست | pytest + pytest-asyncio |
| API Routes | بیش از ۵۰ روتر ثبتشده در `apps/main.py` |
| ماژولهای اصلی | satellite, ml, weather, crops, water, risks, ecocoin, simulation, economics, ai_agents |

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

## ۳. برنامه توسعه — فازبندی

### ✅ فاز ۰: راه اندازی و راستی آزمایی محیط لوکال
**اهداف:** اجرای baseline و اطمینان از سالم بودن سیستم قبل از هر تغییری

| گام | اقدام | ابزار |
|---|---|---|
| ۰.۱ | اجرای سرویس پایگاه داده | `docker compose -f docker-compose.dev.yml up -d db` |
| ۰.۲ | نصب وابستگیهای Python | `pip install -r requirements.txt` |
| ۰.۳ | نصب وابستگیهای Node | `pnpm install` |
| ۰.۴ | اجرای migrations | `alembic upgrade head` |
| ۰.۵ | اجرای تستهای baseline | `pytest` |
| ۰.۶ | راهاندازی سرویس API | `docker compose -f docker-compose.dev.yml up -d api` |
| ۰.۷ | بررسی Health endpoint | `GET /health` — انتظار `{"status": "healthy"}` |

**معیار پذیرش:** تمام ۵۰+ روتر در `/api/v1/debug/routers` بدون خطا بارگذاری شوند و `pytest` سبز باشد.

---

### ⬜ فاز ۱: زیرساخت هسته (shared_core)
**اهداف:** اطمینان از امنیت، یکپارچگی و قابلیت نگهداری

| گام | اقدام |
|---|---|
| ۱.۱ | بازبینی کامل ماژول `spider_security` (ضد XSS/CSRF/SQLi) |
| ۱.۲ | اطمینان از اعمال rate limiting روی همه روترها |
| ۱.۳ | یکپارچهسازی audit log در تمام عملیات حساس |
| ۱.۴ | استانداردسازی پاسخ خطا (الگوی یکسان `error.code/message/details/request_id`) |
| ۱.۵ | بازبینی مدیریت secrets — حذف از environment و انتقال به vault | 

**معیار پذیرش:** اسکن `bandit` بدون خطای high/critical؛ تست auth برای همه endpoint ها.

---

### ⬜ فاز ۲: توسعه ماژولهای تخصصی
**اهداف:** رسیدن به همسطح یا فراتر از پلتفرمهای مشابه (با هزینه صفر)

| ماژول | اقدام | پلتفرم مشابه (مرجع) |
|---|---|---|
| `satellite` | پردازش تصاویر Sentinel-2/Landsat، محاسبه NDVI/NDWI | Google Earth Engine, Sentinel Hub |
| `ml` | مدلهای پیشبینی بازده، تشخیص آفات | IBM Watson Agriculture, Farmers Business Network |
| `economics/ecocoin` | توکنومیک، کیف پول، یکپارچهسازی قراردادهای Solidity | Regen Network, Toucan Protocol |
| `weather` | پیشبینی کوتاهمدت با دادههای رایگان (Open-Meteo, NOAA) | Climate FieldView, aWhere |
| `water` | مدیریت بهینه مصرف آب، مدل هیدرولوژیک | Netafim, CropX |
| `risks` | موتور هشدار زودهنگام چندعاملی | Descartes Labs |

**اصل هزینه صفر:** استفاده از API های رایگان و open data (Sentinel, NOAA, Open-Meteo, USGS) بهجای سرویسهای پولی.

---

### ⬜ فاز ۳: تست، امنیت و بهینهسازی
**اهداف:** تضمین کیفیت و امنیت production-ready

| گام | اقدام |
|---|---|
| ۳.۱ | پوشش تست واحد + یکپارچهسازی برای هر ماژول |
| ۳.۲ | تست boundary/negative/edge-case برای محاسبات اقتصادی و پیشبینی |
| ۳.۳ | اجرای `bandit`، `safety check`، `pip-audit` |
| ۳.۴ | تحلیل performance با ابزارهای ماژول `monitoring/` |
| ۳.۵ | تست بار (همزمانی، رفتار تحت حجم بالا) |

---

### ⬜ فاز ۴: استقرار و انتشار
**اهداف:** استقرار لوکال + آپلود نهایی به GitHub

| گام | اقدام |
|---|---|
| ۴.۱ | تست کامل `docker-compose.prod.yml` بهصورت لوکال |
| ۴.۲ | بررسی `liara.json` (استقرار ابری ایرانی) |
| ۴.۳ | commit با پیامهای معنایی (Conventional Commits) |
| ۴.۴ | push نهایی به `origin` (تأیید شده: `https://github.com/mahak1988/eco-nojin.git`) |
| ۴.۵ | تنظیم GitHub Actions (فایل `ci-admin-panel.yml` موجود است) |

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

- [ ] تمام تستها سبز (pytest + CI در GitHub Actions)
- [ ] اسکن امنیتی بدون یافته critical
- [ ] همسطح بودن ماژولها با پلتفرمهای مرجع (جدول فاز ۲)
- [ ] استقرار موفق لوکال
- [ ] push نهایی به GitHub با تاریخچه تمیز

---

*این سند بر اساس شواهد جمعآوریشده از مخزن تهیه شده و بهروزرسانی خواهد شد.*
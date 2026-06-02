# نقشه راه تکمیل Econojin

## وضعیت فعلی (خرداد ۱۴۰۵)

| لایه | وضعیت | توضیح |
|------|--------|--------|
| بک‌اند `api/` | ~۶۰٪ | ۱۵ روتر ماژول؛ auth/farmer/calendar با DB؛ بقیه stub یا mock |
| فرانت `apps/web` | ~۴۰٪ | ۱۶ صفحه؛ calendar/weather به API وصل؛ بقیه mock |
| پنل ادمین `apps/admin` | ~۱۰٪ | اسکلت Next.js |
| یکپارچگی | ~۳۵٪ | `NEXT_PUBLIC_API_URL`؛ JWT auth آماده؛ Supabase ناقص |
| مدل‌های علمی / بلاکچین | ~۲۰٪ | در `scripts/`؛ جدا از `api/main.py` |

---

## فاز ۱ — یکپارچگی و زیرساخت (۲ هفته)

### بک‌اند
- [ ] استاندارد CRUD برای همه ماژول‌ها (schemas + models + crud)
- [ ] Alembic migrations و پشتیبانی PostgreSQL/PostGIS در production
- [ ] middleware خطای یکنواخت + pagination
- [ ] endpoint تجمیعی `/api/v1/dashboard/stats` برای داشبورد اصلی
- [ ] Swagger tags و نسخه‌گذاری API (`/api/v1`)

### فرانت‌اند
- [x] کامپوننت `ModuleDashboard` مشترک
- [x] رجیستری `lib/modules.ts` برای همه ماژول‌ها
- [ ] اتصال همه صفحات ماژول به API (الگوی accounting/weather)
- [ ] داشبورد اصلی با داده زنده از `/health` و `/modules`
- [ ] صفحه `/farmers` — پنل کشاورز
- [ ] ورود JWT (`/login`) جایگزین/مکمل Supabase
- [ ] React Query برای cache و invalidation

### پنل‌ها
| پنل | مسیر | نقش |
|-----|------|-----|
| کاربر | `apps/web` | داشبورد + ۱۳ ماژول + farmers |
| ادمین | `apps/admin` | مدیریت کاربران، ماژول‌ها، سلامت API |
| CMS | `apps/cms` | محتوا و مقالات (Strapi) — فاز ۳ |

---

## فاز ۲ — تکمیل ماژول‌های محصول (۳–۴ هفته)

### صفحات مورد نیاز (کاربر)

| ماژول | صفحات | API |
|--------|--------|-----|
| داشبورد | `/` | health, modules, dashboard/stats |
| هواشناسی | `/weather` | forecast, alerts |
| حسابداری | `/accounting` | summary, transactions |
| تقویم | `/calendar` | CRUD events |
| GIS | `/gis` | map, area, layers |
| آموزش | `/education` | courses, progress |
| روانشناسی | `/psychology` | tests, sessions |
| EcoCoin | `/ecomining` | balance, mine |
| فروشگاه | `/store` | products, cart |
| کتابخانه | `/library` | books, downloads |
| میزکار | `/desktop` | widgets, shortcuts |
| جامعه | `/community` | posts, groups |
| بازی | `/games` | scores, challenges |
| تنظیمات | `/settings` | profile, prefs |
| کشاورزان | `/farmers` | farmers CRUD |
| احراز هویت | `/login`, `/register` | auth JWT |

### صفحات ادمین (`apps/admin`)

| صفحه | مسیر |
|------|------|
| داشبورد | `/` |
| کاربران | `/users` |
| کشاورزان | `/farmers` |
| ماژول‌ها | `/modules` |
| سلامت سیستم | `/system` |
| لاگ / گزارش | `/logs` |

---

## فاز ۳ — داده واقعی و علمی (۴+ هفته)

- اتصال ERA5، Sentinel-2 به GIS/weather
- SimulationService (AquaCrop, RothC, SWAT+) از `scripts/` به `api/`
- قرارداد `ECO.sol` و oracle compliance
- Celery + Redis برای jobهای سنگین
- PWA و حالت آفلاین

---

## فاز ۴ — production

- Docker compose prod، CI/CD، تست e2e Playwright
- مانیتورینگ (Prometheus/Grafana)
- i18n کامل (fa/en) با next-intl
- امنیت: OTP، rate limit، secrets در vault

---

## ماتریس یکپارچگی (هدف)

```
apps/web  ──axios──►  api/main.py  ──SQLAlchemy──►  SQLite/Postgres
apps/admin ──axios──►  api/main.py
apps/cms   ──REST───►  Strapi (اختیاری)
```

---

## اولویت اجرای هفته جاری

1. تکمیل اتصال API برای ۱۱ صفحه mock
2. داشبورد اصلی زنده + پنل admin اولیه
3. login با JWT
4. تست‌های integration + مستند deploy

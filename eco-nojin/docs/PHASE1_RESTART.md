# فاز ۱ — راه‌اندازی مجدد روی پشتهٔ بدون Docker

**تاریخ:** ۱۴۰۵ / ۲۰۲۶  
**محیط هدف:** Local-First (Python venv + SQLite) — `docs/ZERO_INSTALL_LOCAL.md`

## واقعیت مخزن (صادقانه)

طبق ساختار فعلی `apps/`:

| ماژول | پوشه | وضعیت کد |
|--------|------|----------|
| Farms | `apps/farms/` | models/repo/service/router + spatial |
| Crops | `apps/crops/` | catalog + agronomy fields |
| Inventory | `apps/inventory/` | موجود |
| Water | `apps/water/` | موجود |
| Weather | `apps/weather/` | موجود |
| Notifications | `apps/notifications/` | موجود |
| Planting | `apps/planting/` | plans + tasks |
| Auth | `apps/users/` | register/login/refresh |

یعنی **اسکلت فاز ۱ در مخزن هست**؛ کار فاز ۱ از این نقطه یعنی:

1. اجرای پایدار بدون Docker  
2. هم‌ترازی schema SQLite با ORM  
3. اتصال واقعی FE ↔ API  
4. پر کردن شکاف‌های کیفیت (Loading/Error/Empty، RBAC روی write، seed)

نه «ساخت از صفر».

---

## مرحله ۰ — پایهٔ اجرا (همین الان)

```powershell
cd <repo-root>   # جایی که apps\main.py هست
git pull origin main
.\scripts\run_local.ps1
```

ترمینال دوم:

```powershell
cd apps\web
npm install
npm run dev
```

تأیید:

```powershell
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/farms?page=1&size=5"
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/crops?page=1&size=20"
```

اگر `no such column` دیدید → فایل DB را طبق `ZERO_INSTALL_LOCAL.md` ریست کنید.

---

## مرحله ۱ — Auth پایدار (F1.7)

هدف: ثبت‌نام → ورود → cookie → `/api/v1/auth/me`

```powershell
curl.exe -c cookies.txt -b cookies.txt -X POST `
  -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" `
  -d "{\"email\":\"farmer1@example.com\",\"password\":\"SecurePass123!\",\"full_name\":\"Test Farmer\"}" `
  http://localhost:8000/api/v1/auth/register

curl.exe -c cookies.txt -b cookies.txt -X POST `
  -H "Content-Type: application/json" -H "User-Agent: Mozilla/5.0" `
  -d "{\"email\":\"farmer1@example.com\",\"password\":\"SecurePass123!\"}" `
  http://localhost:8000/api/v1/auth/login

curl.exe -b cookies.txt -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/auth/me
```

معیار پذیرش: HTTP 200 روی `me` با cookie.

---

## مرحله ۲ — Farms + Crops (F1.10 / F1.11)

- لیست مزارع با pagination  
- ایجاد مزرعه (POST)  
- GeoJSON (اگر بدون PostGIS: پاسخ ساده بدون خطای ۵۰۰)  
- کاتالوگ محصول ≥ ۱۰۰ ردیف پس از seed  
- صفحهٔ FE `/farms` و `/crops` با Loading / Error / Empty

---

## مرحله ۳ — Water + Planting + Inventory (F1.12 / F1.13)

- dashboard آب + سیستم آبیاری + schedule  
- planting-plans + tasks  
- inventory items  
- فرمول آبیاری: `ETc = ET0 × Kc` ، حجم ناخالص با راندمان

---

## مرحله ۴ — Dashboard + Account (F1.8 / F1.9)

- `/dashboard` از API واقعی  
- profile / security / notifications  
- دکمه‌های ورود/خروج/زبان فعال

---

## معیار خروج فاز ۱ (قابل اندازه‌گیری)

| معیار | روش اثبات |
|--------|-----------|
| health database ok | curl `/health` |
| register + login + me | curl + cookies.txt |
| farms list 200 | curl |
| crops list بدون 500 | curl؛ در صورت نیاز seed |
| FE صفحات اصلی بدون mock اجباری | VITE_USE_MOCK=false |
| بدون نیاز به Docker | فقط run_local.ps1 |

---

## خارج از محدودهٔ این فاز (عمداً)

- Docker / Compose  
- GEE واقعی با Service Account  
- باینری رسمی FAO AquaCrop / SWAT+  
- ادعاهای coverage ۷۸٪ بدون pytest --cov  

این‌ها بعداً با Postgres ابری (Neon) یا سرور واقعی، نه با نصب Docker اجباری روی لپ‌تاپ.

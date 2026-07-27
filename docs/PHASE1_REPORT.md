# گزارش عملیاتی فاز ۱ — مراحل ۱ تا ۴

**تاریخ:** 2026-07-27  
**مخزن:** mahak1988/eco-nojin  
**وضعیت:** چهار مرحلهٔ تثبیت هسته (auth/RBAC/Education FE/Accounting) تکمیل شد. ماژول‌های کامل farms/crops/water (برنامهٔ بلندمدت فاز ۱) هنوز در صف توسعهٔ محصول هستند.

---

## خلاصه اجرایی

پس از بستن فاز ۰ (boot پایدار، Alembic، RBAC، JWT پایه)، چهار مرحلهٔ فاز ۱ روی **امنیت نشست، مجوز، Education واقعی، حسابداری demo و UX ناوبری** اجرا شد.

| مرحله | عنوان | وضعیت |
|-------|--------|--------|
| ۱ | HttpOnly cookie روی login/register/refresh/logout | ✅ |
| ۲ | `require_permission` روی writeهای education/accounting | ✅ |
| ۳ | صفحه Education → API + Loading/Error/Empty | ✅ |
| ۴ | Accounting seed + contract tests + Header auth/lang | ✅ |

---

## مرحله ۱ — HttpOnly cookies

- Cookieهای `access_token` و `refresh_token` (HttpOnly, SameSite, Secure در production)
- خواندن توکن از Bearer **یا** cookie در `/auth/me` و deps
- Refresh از body یا cookie
- FE: `credentials: "include"`

## مرحله ۲ — RBAC روی write

- Education: `education:write`
- Accounting: `accounting:write`
- Soft-gate local: `REQUIRE_AUTH_FOR_WRITES=false` + `ENVIRONMENT=local`

## مرحله ۳ — Education FE

- fetch واقعی `/api/v1/education/courses`
- حالات loading / error / empty / ready
- Seed demo از UI

## مرحله ۴ — تکمیل UX + seed حسابداری

### Backend
- `POST /api/v1/accounting/seed-demo` → حساب‌ها + journal با درآمد ۲۵۰۰ و هزینه ۸۰۰
- Contract tests: `tests/contract/test_phase0_endpoints.py`

### Frontend
- Header: LanguageSwitcher (fa/en/ar) + **Sign in / Logout / Profile**
- Login + **Register** صفحات با لینک متقابل و سوئیچ زبان
- `authApi` با `accessToken` camelCase API
- `useAuth`: login/register/logout + hydrate از `/auth/me`
- Home CTAها از قبل به `#cta` / ماژول‌ها لینک دارند؛ ورود از Header و `/login`

---

## دستورات تأیید

```powershell
git pull origin main
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

curl.exe -H "User-Agent: Mozilla/5.0" -X POST http://localhost:8000/api/v1/accounting/seed-demo
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/accounting/summary
# انتظار: total_income ≈ 2500، total_expense ≈ 800

pytest tests/contract/test_phase0_endpoints.py -q
```

FE:

```powershell
cd apps/web
npm run dev
# http://localhost:5173 — زبان، ورود، خروج، Education، Accounting
```

---

## باقی‌ماندهٔ نقشهٔ فاز ۱ (هسته کشاورزی کامل)

طبق منشور بخش ۴ هنوز باید ساخته شوند:

- `apps/farms`, `crops`, `inventory`, `water`, `weather`, `notifications`
- ۲۶ صفحه محصول (onboarding، wizard مزرعه، نقشه GeoJSON، …)
- ~۳۰ endpoint اختصاصی فاز ۱
- OTP / forgot-password کامل

**پیشنهاد مرحله بعد:** F1.1 `apps/farms` CRUD + صفحه list/new.

---

## ریسک‌ها

- localStorage هنوز fallback برای Bearer است (تا انتقال کامل به cookie-only)
- summary حسابداری به join JournalItem وابسته است؛ seed باید قبل از summary زده شود
- برخی کلیدهای i18n گروه‌های «بیشتر» ممکن است خام نمایش داده شوند (قابل تکمیل در i18n)

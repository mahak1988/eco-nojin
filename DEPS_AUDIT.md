# DEPS_AUDIT.md (Generated)
## Scope
این فایل بر اساس **مشاهده‌های فعلی از مستندات + چند فایل کلیدی کد** و **package/requirements** ساخته شده است. برای “کامل” شدن audit، باید importها از همه‌ی ماژول‌های `apps/api/app/**` و `apps/web/**` استخراج شوند (چون ابزار جستجوی ripgrep در محیط در دسترس نیست).

## 1) Backend (`apps/api`)
### 1.1 deps در `apps/api/requirements.txt` (حداقل‌های تعریف‌شده)
- fastapi (>=0.104.0)
- uvicorn[standard] (>=0.24.0)
- pydantic (>=2.0.0)
- httpx (>=0.25.0)
- numpy (>=1.24.0)
- python-dotenv (>=1.0.0)

### 1.2 deps که در کد دیده شد (از importهای واقعی)
از فایل `apps/api/app/core/security.py`:
- jose (python-jose) → `from jose import JWTError, jwt`
- bcrypt → `import bcrypt`
- fastapi.security → `OAuth2PasswordBearer`
- sqlalchemy.ext.asyncio → `AsyncSession`

از فایل `apps/api/app/core/database.py`:
- sqlalchemy (async engine, async_sessionmaker)

**جمع‌بندی فعلی backend deps:**
- پکیج‌هایی که *قطعاً لازم‌اند* اما در `requirements.txt` دیده نشدند: **sqlalchemy**, **python-jose**, **bcrypt**
- بنابراین احتمال mismatch بین requirements و کد وجود دارد.

> اقدام پیشنهادی (مرحله بعدی): بررسی کامل importها در `apps/api/app/**` و سپس افزودن dependecyهای missing به `apps/api/requirements.txt` یا اصلاح ساختار مدیریت وابستگی‌ها.

## 2) Frontend (`apps/web`)
### 2.1 deps در `apps/web/package.json`
dependencies:
- leaflet
- next
- next-intl
- react
- react-dom
- react-leaflet
- recharts
- fuse.js
- jspdf
- html2canvas
- xlsx
- @react-aria/button/focus/interactions

devDependencies:
- @tailwindcss/postcss
- @types/node
- @types/react
- @types/react-dom
- autoprefixer
- tailwindcss
- typescript

### 2.2 mismatch محتمل با کد/اسناد
در README/docs از موارد زیر نام برده شده ولی در `apps/web/package.json` مشاهده نشد:
- React Query (TanStack Query)
- Axios
- Zod
- React Hook Form

همچنین یک hook موجود است:
- `apps/web/lib/hooks/useApi.ts` از `fetch` استفاده می‌کند، پس axios/ReactQuery برای همین hook الزامی نیست؛ ولی ممکن است سایر کامپوننت‌ها نیاز داشته باشند.

> اقدام پیشنهادی (مرحله بعدی): استخراج importهای واقعی از `apps/web/**` برای تعیین اینکه کدام dependency واقعاً موردنیاز است و کدام‌ها در docs اشاره شده ولی حذف/عدم‌استفاده‌اند.

## 3) Root (`package.json` ریشه)
- dependencies:
  - zustand
- devDependencies:
  - turbo
  - @types/geojson و types react

### جمع‌بندی
برای monorepo-ready کردن یکپارچگی، باید:
- deps واقعی مورد استفاده در هر app را align کنیم
- missing deps را بدون “حذف چیزی” اضافه کنیم (فقط اصلاح/اضافه)

## وضعیت
- این audit “partial” است و برای “کامل” شدن نیاز به خواندن importها در کل سورس دارد.
- به محض تکمیل audit، یک سند `API_CONTRACT.md` نیز برای هم‌ترازی فرانت/بک‌اند تولید خواهد شد.

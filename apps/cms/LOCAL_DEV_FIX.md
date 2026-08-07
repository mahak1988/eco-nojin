# رفع خطاهای محلی (Windows + pnpm)

## ۱) Merge ناتمام

```powershell
cd D:\econojin.com
git status

# اگر All conflicts fixed but you are still merging:
$env:PRE_COMMIT_ALLOW_NO_CONFIG = "1"
git add -A
git commit --no-edit

# اگر conflict دارید و نمی‌خواهید ادامه دهید:
# git merge --abort

git pull origin main
```

## ۲) better-sqlite3 — build scripts نادیده گرفته شده

pnpm v10+ اسکریپت build را به‌طور پیش‌فرض بلاک می‌کند.

```powershell
cd D:\econojin.com

# اجازه build برای better-sqlite3
pnpm approve-builds
# در لیست better-sqlite3 را انتخاب و تأیید کنید

# یا یک‌بار با اجبار:
pnpm rebuild better-sqlite3

# نصب مجدد از ریشه
pnpm install

cd apps\cms
pnpm dev
```

اگر `approve-builds` تعاملی نبود:

```powershell
cd D:\econojin.com
$env:npm_config_build_from_source = "true"
pnpm --filter @econojin/cms rebuild better-sqlite3
cd apps\cms
pnpm exec strapi develop
```

## ۳) متغیرها

```powershell
cd D:\econojin.com\apps\cms
copy .env.example .env
```

در ریشه / FastAPI:

```env
CMS_BASE_URL=http://localhost:1337
CMS_API_TOKEN=<token-from-strapi-admin>
```

## ۴) نقش Editor

بعد از بالا آمدن Strapi، نقش `Editor` به‌صورت خودکار ساخته می‌شود (CRUD بدون delete).
در Admin → Users → نقش کاربر را Editor بگذارید.

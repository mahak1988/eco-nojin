# رفع better-sqlite3 روی Windows

## علت
pnpm به‌صورت پیش‌فرض اسکریپت build پکیج‌های native را اجرا نمی‌کند؛ فایل `better_sqlite3.node` ساخته نمی‌شود.

## روش ۱ — توصیه (از ریشه monorepo)

```powershell
cd D:\econojin.com
git pull origin main

pnpm config set ignore-scripts false

# حذف باینری ناقص و نصب مجدد
pnpm remove better-sqlite3 -r
pnpm add better-sqlite3@11.10.0 --filter @econojin/cms

# یا force:
pnpm install --force

cd apps\cms
pnpm dev
```

## روش ۲ — build مستقیم در پوشه پکیج

```powershell
cd D:\econojin.com
$bs = Get-ChildItem -Recurse -Directory -Filter "better-sqlite3" |
  Where-Object { $_.FullName -match 'node_modules\\better-sqlite3$' } |
  Select-Object -First 1

if ($bs) {
  cd $bs.FullName
  npm install --ignore-scripts=false
  npx prebuild-install || npm run build-release
}

cd D:\econojin.com\apps\cms
pnpm dev
```

## روش ۳ — Visual Studio Build Tools

1. نصب «Desktop development with C++»
2. سپس:

```powershell
cd D:\econojin.com
pnpm rebuild better-sqlite3 --force
```

## روش ۴ — Postgres به‌جای sqlite

در `apps/cms/.env`:

```env
DATABASE_CLIENT=postgres
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=strapi
DATABASE_USERNAME=strapi
DATABASE_PASSWORD=strapi
```

با Docker:

```powershell
docker run -d --name strapi-pg -e POSTGRES_USER=strapi -e POSTGRES_PASSWORD=strapi -e POSTGRES_DB=strapi -p 5432:5432 postgres:16
```

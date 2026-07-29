# استک رایگان Econojin

## هاست و استقرار

| سرویس | کاربرد | لینک |
|--------|--------|------|
| **Vercel** | فرانت Next.js (`apps/web`) | https://vercel.com |
| **Render** | API FastAPI (free tier) | https://render.com |
| **Railway** | API + Redis | https://railway.app |
| **Fly.io** | API container | https://fly.io |
| **GitHub Pages** | مستندات استاتیک | https://pages.github.com |

## دیتابیس رایگان

| سرویس | نوع | لینک |
|--------|-----|------|
| **Neon** | PostgreSQL serverless | https://neon.tech |
| **Supabase** | Postgres + Auth | https://supabase.com |
| **Turso** | SQLite edge | https://turso.tech |
| **MongoDB Atlas** | NoSQL (اختیاری) | https://www.mongodb.com/atlas |

تنظیم production:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/econojin
```

## SMS / OTP (تولید)

| سرویس | یادداشت |
|--------|---------|
| **Twilio** | trial رایگان محدود |
| **Kavenegar** | پنل ایران — tier رایگان محدود |
| **حالت dev** | `OTP_DEV_MODE=true` کد در پاسخ API |

## CI/CD

- GitHub Actions: `.github/workflows/econojin-apps-ci.yml`
- Docker محلی: `docker compose -f docker-compose.apps.yml up`

## CDN / تصاویر

- Unsplash (تصاویر هیرو — فعلی)
- OpenStreetMap tiles (GIS — رایگان)

## متغیرهای Vercel

```
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

## متغیرهای Render (API)

```
JWT_SECRET=<random-64>
DATABASE_URL=<neon-url>
OTP_DEV_MODE=false
REQUIRE_AUTH_FOR_WRITES=true
```

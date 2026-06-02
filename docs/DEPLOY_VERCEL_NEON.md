# استقرار رایگان: Vercel + Neon + Render

## ۱. دیتابیس Neon (رایگان)

1. ثبت‌نام: https://neon.tech
2. پروژه جدید → Connection string
3. در Render API:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASS@ep-xxx.neon.tech/neondb?sslmode=require
```

## ۲. API روی Render (رایگان)

1. https://render.com → Web Service
2. Root: repo root، Dockerfile: `docker/Dockerfile.api`
3. Env:

```env
JWT_SECRET=<random-64-chars>
OTP_DEV_MODE=false
SMS_PROVIDER=kavenegar
KAVENEGAR_API_KEY=...
LLM_ENABLED=true
OPENAI_API_KEY=sk-...
ALLOWED_ORIGINS=https://your-app.vercel.app
```

Health: `/api/v1/health`

## ۳. فرانت Vercel (رایگان)

1. Import repo → Root Directory: `apps/web`
2. Env:

```env
NEXT_PUBLIC_API_URL=https://your-api.onrender.com
```

3. Deploy

## ۴. GitHub Actions

Workflow: `.github/workflows/econojin-apps-ci.yml` — خودکار روی push

## ۵. SMS (Kavenegar ایران)

```env
SMS_PROVIDER=kavenegar
KAVENEGAR_API_KEY=...
KAVENEGAR_TEMPLATE=verify
OTP_DEV_MODE=false
```

## ۶. LLM

OpenAI:

```env
LLM_ENABLED=true
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

Azure:

```env
LLM_ENABLED=true
AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com
AZURE_OPENAI_KEY=...
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

## ۷. Twilio (بین‌المللی)

```env
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_FROM_NUMBER=+1...
```

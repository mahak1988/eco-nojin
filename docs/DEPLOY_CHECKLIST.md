# Deploy Checklist (Low-cost target)

## Target stack
- Web: Cloudflare Pages or Vercel (`apps/web`)
- API: Render or Fly (`apps.main:app`)
- DB: Neon Postgres
- Redis: Upstash (rate limit)
- Errors: Sentry

## Steps
1. Create Neon DB → set `DATABASE_URL`
2. Set `SECRET_KEY`, `ENVIRONMENT=production`, CORS origins
3. Run Alembic migrations
4. Deploy API container; verify `/health`
5. Build web with `VITE_API_BASE_URL=https://api.example.com`
6. Smoke: login, education list, accounting summary, one simulation
7. Confirm writes without token return 401

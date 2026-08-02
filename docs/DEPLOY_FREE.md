# Phase 6 — Free deployment guide

**Cost target:** $0 for MVP (free tiers).

## Recommended free stack

| Layer | Service | Notes |
|-------|---------|-------|
| Frontend | Vercel / Cloudflare Pages / Netlify | `apps/web` Vite build |
| API | Render free / Fly.io free / Railway trial | `uvicorn apps.main:app` |
| Database | Neon or Supabase free | Postgres (+ PostGIS on Neon if enabled) |
| Redis | Optional Upstash free | Celery/cache; skip offline |
| EO | Planetary Computer | No paid key |
| Models | AquaCrop-OSPy + pyRothC optional | Pure Python |

## Environment (production)

```bash
ENVIRONMENT=production
SECRET_KEY=<secrets.token_urlsafe(48)>
DATABASE_URL=postgresql+asyncpg://USER:PASS@HOST/db
FORCE_POSTGRES=true
COOKIE_SECURE=true
REQUIRE_AUTH_FOR_WRITES=true
ENABLE_RATE_LIMIT=true
BACKEND_CORS_ORIGINS=https://your-frontend.vercel.app
```

Never commit real secrets. Use platform secret stores.

## Local production-like

```bash
docker compose -f docker-compose.free.yml up --build
# API http://localhost:8000/health
```

Frontend:

```bash
cd apps/web
npm install   # or pnpm in monorepo root
npm run dev   # http://localhost:5173  — proxies /api to :8000
```

## Checklist

- [ ] `/health` returns healthy
- [ ] `/api/v1/science/e2e-mrv/isfahan-wheat` works
- [ ] Frontend opens Home + Site map (`/sitemap`)
- [ ] CORS matches frontend origin
- [ ] SECRET_KEY not a placeholder

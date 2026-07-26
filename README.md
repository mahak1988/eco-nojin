# Econojin (اکو نوژین)

**Integrated platform for smart agriculture, water, environment, green economy, and rural community.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB)](https://react.dev)
[![License](https://img.shields.io/badge/license-MIT-green)](License)

---

## Status (2026-07-27)

| Area | Status | Notes |
|------|--------|--------|
| API boot | ✅ | `uvicorn apps.main:app` loads 15+ routers |
| `/health` | ✅ | Reports `database: ok\|fail` |
| Education API | ✅ | List + seed-demo; fixed async relationship load |
| Accounting summary | ✅ | Live endpoint (data may be zero until seed) |
| FE ↔ BE local | ✅ | Vite proxies `/api` and `/health` |
| `requirements.txt` | ✅ fixed | Real package pins (was broken) |
| Alembic-first schema | ⚠️ | Local still uses `create_all` |
| Auth hardening | ⚠️ | JWT HS256; token often in localStorage |
| Celery / WS | ❌ | Planned in [docs/ROADMAP_TOBE.md](docs/ROADMAP_TOBE.md) |

Changelog: [CHANGELOG.md](CHANGELOG.md) · Connection guide: [docs/FE_BE_CONNECTION.md](docs/FE_BE_CONNECTION.md)

---

## Quickstart

```bash
git clone https://github.com/mahak1988/eco-nojin.git
cd eco-nojin
cp .env.example .env   # set SECRET_KEY, DATABASE_URL

# Backend
pip install -r requirements.txt
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd apps/web
pnpm install
pnpm dev
```

- API docs: http://localhost:8000/docs  
- Health: http://localhost:8000/health  
- Web: http://localhost:5173  

**Demo education data (once):**

```bash
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/seed-demo
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/courses
```

Leave `VITE_API_BASE_URL` **empty** so the Vite proxy is used.

---

## Architecture (monorepo)

```
apps/
  main.py              # FastAPI entry
  shared_core/         # config, security, middleware, database
  api/routes/          # domain routers (education, accounting, …)
  simulation/          # scientific simulators
  users/               # auth & users
  web/                 # React + Vite + TypeScript + Tailwind
  cms/                 # Strapi (optional)
security/middleware/   # request hardening
docs/                  # engineering standards & roadmaps
```

**i18n:** UI languages **fa** and **en** only until product stabilizes.  
**Code & technical documentation:** English.

---

## Security baseline

- Secrets from `.env` only
- `REQUIRE_AUTH_FOR_WRITES` for mutating routes
- `X-Request-ID` on responses
- Security headers middleware (no broken `headers.pop`)
- Production: disable `/docs` when `ENVIRONMENT=production`

Remaining work: httpOnly refresh flow, RBAC five roles, RS256 for multi-service JWT — see roadmap.

---

## Main API groups

| Prefix | Module |
|--------|--------|
| `/api/v1/auth` | Authentication |
| `/api/v1/users` | Users |
| `/api/v1/education` | Courses / lessons / enrollments |
| `/api/v1/accounting` | Accounts, summary |
| `/api/v1/simulation` | Scientific runs |
| `/api/v1/community` | Community |
| `/api/v1/admin` | Admin |
| `/health` | Liveness + DB probe |

---

## Tests

```bash
pytest apps/ -v
cd apps/web && pnpm type-check
```

---

## Deploy (low-cost target)

- Frontend: Vercel / Cloudflare Pages  
- API: Render / Fly.io  
- DB: Neon PostgreSQL  
- Cache: Upstash Redis  

See [docs/DEPLOY_CHECKLIST.md](docs/DEPLOY_CHECKLIST.md).

---

## License

MIT — see [License](License).

**Econojin** — sustainable, data-driven agriculture and community 🌱

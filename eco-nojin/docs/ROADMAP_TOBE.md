# EcoNojin — TO-BE roadmap (engineering charter)

**Languages:** UI fa/en only (other locales disabled until stable).
**Code & technical docs:** English.

## Target architecture

| Layer | Target |
|-------|--------|
| API | ~80 endpoint groups under `/api/v1`, OpenAPI-first |
| Web | ~80 functional pages wired to real API |
| Realtime | 3 WebSocket channels: monitoring, ai-chat, notifications |
| Auth | RBAC: superadmin, admin, expert, farmer, viewer + refresh tokens |
| Jobs | Celery + Redis for simulators |
| Data | PostgreSQL (+ optional Timescale), Alembic migrations |
| Quality | Contract tests per endpoint; TS types from OpenAPI |

## Priority waves

### Wave A — Foundation (now)
1. Fix `requirements.txt` / reproducible install ✅
2. Honest health + FE proxy + education serialization ✅
3. Alembic as default schema path (stop relying on `create_all` in staging+)
4. Expand `_import_models` + single metadata registry
5. httpOnly cookie session or short-lived access + refresh (replace pure localStorage)

### Wave B — Product surface
1. Wire remaining pages (community, games, satellite, MRV) with mappers + badges
2. Admin RBAC gates
3. Seed scripts for accounting/community demo

### Wave C — Scale & realtime
1. Celery workers for AquaCrop/RothC/SWAT
2. WebSocket gateway
3. Redis rate limit shared across instances

### Wave D — Hardening
1. RS256 optional for multi-service JWT
2. Audit log pipeline
3. Contract tests in CI
4. OpenAPI → TypeScript codegen

## AS-IS honesty (2026-07-27)

- Backend: many routers load; ~25–40% of product depth truly complete
- Frontend: many pages; partial live API (education path proven after seed)
- Critical fixed recently: middleware 500, health engine, education MissingGreenlet
- Still broken/weak: root `requirements.txt` was empty of real deps (fixed this commit); migrations discipline; auth storage

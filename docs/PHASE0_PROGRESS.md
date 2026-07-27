# Phase 0 — COMPLETE

Verified locally (2026-07-27):

- `GET /health` → healthy, database ok
- `POST /api/v1/rbac/seed` → 5 roles, 16 permissions
- `GET /api/v1/education/courses?page=1&size=5` → data + meta envelope
- `GET /api/v1/accounting/summary` → zeros OK

| Item | Status |
|------|--------|
| F0.1 pyproject | DONE |
| F0.2 Alembic baseline | DONE |
| F0.3 RBAC | DONE |
| F0.4 JWT HS256 + refresh helpers | DONE (RS256 keys optional later) |
| Boot hygiene | routers fixed; optional deps at DEBUG |

Deferred to Phase 1 / infra track: Celery, Redis WS, OpenAPI codegen, full Docker compose, RS256 production keys.

## Phase 1 entry

Focus: product modules (farms, education FE wiring, accounting seed, contract tests) while keeping Hard Rules R1–R23.

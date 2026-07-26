# Changelog

All notable changes to EcoNojin are documented here.

## [Unreleased]

### Fixed (2026-07-26 / 2026-07-27)
- Security middleware: Starlette `MutableHeaders` has no `.pop` — use `del` for `Server` header
- `/health`: export `get_engine()`; honest `database: ok|fail`
- Education list: `MissingGreenlet` — `selectinload(lessons, enrollments)` + safe response mapping
- Education seed: `POST /api/v1/education/seed-demo` (local/staging only)
- FE↔BE: Vite proxy for `/api`, `/health`; relative API base by default
- CORS: permissive in `ENVIRONMENT=local`
- Model registration on `init_db` (education, accounting, community, users)

### Added
- Frontend structure: `api/`, hooks, mappers, admin shell, login routes
- Docs: `FE_BE_CONNECTION.md`, `API_UI_MAP.md`, `ENGINEERING_STANDARDS.md`, `SECURITY_ARCHITECTURE.md`
- Restored usable `requirements.txt` (was broken local pip path)

### Known gaps (tracked in TO-BE)
- Alembic not yet primary path (still `create_all` in local)
- JWT HS256 + token in localStorage
- No Celery/Redis job queue for long simulations
- No production WebSocket channels
- RBAC 5 roles incomplete

# Changelog

## [Unreleased]

### 2026-07-27 — Constitution & Wave A
- Added `docs/CONSTITUTION.md` (hard rules R1–R23)
- Added `docs/RULES_GAP.md` (honest compliance matrix)
- **R10:** CORS no longer uses `*`; explicit localhost origins only
- **R20:** `DATABASE_URL` from Pydantic settings in `session.py`
- **R11 path:** `create_all` only when `ENVIRONMENT=local`; staging+ must use Alembic
- Central `model_registry.py` (education, accounting, community, users, …)
- Error handlers move toward **R17** nested `{ error: { code, message, details, request_id } }`
- Alembic `env.py` uses model registry + settings URL

### 2026-07-26
- Security middleware MutableHeaders fix
- Health get_engine, education MissingGreenlet, seed-demo, FE proxy
- Restored `requirements.txt`, README rewrite

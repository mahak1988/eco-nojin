# Phase 0 progress

| Item | Title | Status |
|------|-------|--------|
| F0.1 | pyproject.toml + real deps | DONE (license string fixed for editable install) |
| **F0.2** | Alembic + baseline migration | **DONE** |
| F0.3 | RBAC engine | pending |
| F0.4 | Auth RS256 + refresh + HttpOnly | pending |
| F0.5–F0.10 | Celery, WS, OpenAPI, Docker… | pending |

## F0.2 deliverables
- `alembic/versions/20260727_0001_baseline_education.py`
- `docs/DB_VERSIONING.md` (schema policy + key handling)
- `pyproject.toml` editable-install fix (`license = "MIT"`, no broken readme load)

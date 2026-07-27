# Phase 0 progress

| Item | Title | Status |
|------|-------|--------|
| **F0.1** | pyproject.toml + real deps | **DONE** (this delivery) |
| F0.2 | Alembic + baseline migration | pending |
| F0.3 | RBAC engine | pending |
| F0.4 | Auth RS256 + refresh + HttpOnly (= former F1.2) | pending |
| F0.5 | Celery + Redis | pending |
| F0.6 | WebSocket gateway | pending |
| F0.7 | OpenAPI → TS types | pending |
| F0.8 | Prism mock server | pending |
| F0.9 | main.py auto-discovery + JSON logs | pending |
| F0.10 | Full docker compose | pending |

## F0.1 notes

- Core runtime deps live in `[project].dependencies`
- Optional: `[worker]` (celery/redis), `[dev]` (pytest/ruff)
- `requirements.txt` kept for Windows/simple `pip install -r`
- Full lock file (`requirements.lock.txt`) should be generated on a machine with network:
  `pip install -e ".[dev,worker]" && pip freeze > requirements.lock.txt`

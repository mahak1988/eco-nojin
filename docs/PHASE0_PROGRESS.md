# Phase 0 progress

| Item | Status |
|------|--------|
| F0.1 pyproject | DONE |
| F0.2 Alembic | DONE |
| F0.3 RBAC | DONE |
| F0.4 JWT foundation | PARTIAL — access/refresh helpers + cookie kwargs; full RS256 + rotation list next wave |
| Hotfix boot | SQLite fallback, router syntax repairs, schemas package |

## After pull

```powershell
git pull
# Ensure .env has:
# DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db
# ENVIRONMENT=local
# SECRET_KEY=<long random>

uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/rbac/seed
curl.exe -H "User-Agent: Mozilla/5.0" "http://localhost:8000/api/v1/education/courses?page=1&size=5"
```

Routers that previously failed with invalid `Depends(...)` syntax were rewritten.
Remaining optional modules (satellite data, some simulation subrouters) may still warn — non-blocking.

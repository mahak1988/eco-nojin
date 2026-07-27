# Phase 0 progress

| Item | Status |
|------|--------|
| F0.1 pyproject | DONE |
| F0.2 Alembic baseline | DONE — fix sync URL if stamp failed on psycopg2 |
| F0.3 RBAC | pending |
| F0.4 Auth RS256 + cookies | pending |

## If `alembic` failed with psycopg2

Cause: `DATABASE_URL` pointed at Postgres and Alembic tried a sync Postgres driver.

Fix (local):

```env
DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db
ENVIRONMENT=local
```

Then:

```bash
git pull
alembic upgrade head
# or if tables already exist:
alembic stamp 20260727_0001
```

Postgres staging: `pip install "psycopg[binary]"` and use `postgresql+asyncpg://` in app URL (Alembic converts to `postgresql+psycopg://`).

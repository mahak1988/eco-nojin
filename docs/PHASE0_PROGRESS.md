# Phase 0 progress

| Item | Status |
|------|--------|
| F0.1 | DONE |
| F0.2 | DONE (use SQLite fallback if no Postgres driver) |
| **F0.3 RBAC** | **DONE** |
| F0.4 Auth RS256 + HttpOnly | next |

## F0.3 deliverables
- Tables: `roles`, `permissions`, `role_permissions`, `user_roles`
- Migration `20260727_0002`
- Roles: superadmin, admin, expert, farmer, viewer
- `require_permission("resource:action")` dependency
- `POST /api/v1/rbac/seed` (non-production)

## Alembic local

```powershell
$env:ALEMBIC_FORCE_SQLITE="1"
$env:ENVIRONMENT="local"
alembic upgrade head
```

Or set in `.env`:
```
DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db
ENVIRONMENT=local
```

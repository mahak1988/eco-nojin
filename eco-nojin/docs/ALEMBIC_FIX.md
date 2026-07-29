# Alembic chain fix (2026-07-28)

## Problem
- Two files shared revision id `20260727_0002` (rbac + users profile)
- Phase2 pointed at non-existent `20260727_0002_rbac`

## Fixed linear chain

```
20260727_0001  education baseline
    → 20260727_0002  rbac
    → 20260727_0003  users phone/org/role
    → 20260728_0001  farms/sensors/alerts
```

Legacy branch `0001_admin_models → 0002_core_models` remains separate (older).

## Without Docker (your case)

```powershell
git pull origin main
# delete broken duplicate if still present:
Remove-Item -Force alembic\versions\20260727_0002_users_profile_fields.py -ErrorAction SilentlyContinue

$env:ENVIRONMENT="local"
$env:ALEMBIC_USE_SQLITE="1"
$env:DATABASE_URL="sqlite+aiosqlite:///./apps/econojin.db"
alembic heads
alembic upgrade head
```

If DB already partially migrated and conflicts:

```powershell
# nuclear local reset (dev only — loses SQLite data)
Remove-Item -Force apps\econojin.db -ErrorAction SilentlyContinue
alembic upgrade head
```

## With Docker later

Install [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/), then:

```powershell
.\scripts\bootstrap_postgres.ps1
```

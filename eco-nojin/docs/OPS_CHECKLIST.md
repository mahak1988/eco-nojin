# Operator checklist — Postgres · GEE · RBAC

## A. Docker + Alembic (Postgres)

### Prerequisites
- Docker Desktop running
- Python venv with `pip install -r requirements.txt psycopg[binary]`

### Windows
```powershell
.\scripts\bootstrap_postgres.ps1
```

### Linux/macOS
```bash
chmod +x scripts/bootstrap_postgres.sh
./scripts/bootstrap_postgres.sh
```

### Manual
```bash
docker compose up --build -d
export ENVIRONMENT=staging
export ALEMBIC_USE_SQLITE=0
export DATABASE_URL=postgresql+asyncpg://econojin:econojin@localhost:5432/econojin
pip install 'psycopg[binary]'
alembic upgrade head
curl -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
```

If migration branch conflict (multiple heads):
```bash
alembic heads
alembic merge heads -m "merge"
alembic upgrade head
```

---

## B. Google Earth Engine Service Account

1. [Google Cloud Console](https://console.cloud.google.com/) → create project
2. Enable **Earth Engine API**
3. IAM → Service Accounts → Create → role: *Earth Engine Resource Viewer* (or Editor)
4. Keys → Add key → JSON → save as `secrets/gee-sa.json`
5. Open [code.earthengine.google.com](https://code.earthengine.google.com/) logged in as owner
6. Register the **service account email** (Users → add)
7. Optional: apply Partner tier for agri/climate quota

```env
GEE_SERVICE_ACCOUNT=sa-name@PROJECT.iam.gserviceaccount.com
GEE_CREDENTIALS_FILE=secrets/gee-sa.json
GEE_PROJECT_ID=PROJECT_ID
```

```bash
pip install earthengine-api
# restart api
curl "http://localhost:8000/api/v1/satellite/availability?lat=32.65&lon=51.67"
```

Without steps 1–6 the chain uses **synthetic** (safe for local).

---

## C. RBAC on POST writes

Protected when `REQUIRE_AUTH_FOR_WRITES=true` (default in `.env.docker` / staging):

| Permission | Example endpoints |
|------------|-------------------|
| `farms:write` | POST/PATCH/DELETE `/farms` |
| `crops:write` | POST `/crops/seed-demo` |
| `inventory:write` | POST `/inventory/items` |
| `monitoring:write` | POST sensors, readings, rules, seed |
| `simulation:write` | POST aquacrop/rothc/compare |
| `satellite:write` | heavy EO (change detection async) |

Local soft mode: `ENVIRONMENT=local` **and** `REQUIRE_AUTH_FOR_WRITES=false` skips the gate.

Seed roles:
```bash
curl -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/rbac/seed
```

Login as user with role `farmer`/`admin` then call writes with cookie or Bearer.

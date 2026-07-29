# Local deploy (no Docker)

Your machine currently has **no Docker**. Use SQLite + uvicorn.

## One shot (Windows)

```powershell
git pull origin main
.\scripts\deploy_local.ps1
```

## Manual

```powershell
$env:ENVIRONMENT="local"
$env:ALEMBIC_USE_SQLITE="1"
$env:DATABASE_URL="sqlite+aiosqlite:///./apps/econojin.db"
$env:REQUIRE_AUTH_FOR_WRITES="false"

pip install -r requirements.txt
alembic upgrade head
pytest tests/unit/test_indices.py tests/unit/test_weather_alerts.py tests/unit/test_sentinel_fetcher.py -q
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (second terminal):

```powershell
cd apps\web
npm install
npm run dev
```

Open: API http://localhost:8000/docs · UI http://localhost:5173

## When Docker is installed

```powershell
.\scripts\bootstrap_postgres.ps1
docker compose up --build -d
```

## Common failures

| Symptom | Fix |
|---------|-----|
| `docker` not recognized | Use SQLite path above |
| Alembic KeyError revision | `git pull` then `alembic heads` (expect `20260728_0002`) |
| Port 8000 in use | `netstat -ano \| findstr :8000` then kill PID |
| Module not found | activate `.venv` and `pip install -r requirements.txt` |

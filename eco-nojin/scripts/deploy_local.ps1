# Local deploy without Docker — API + optional FE notes
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> pull / deps"
if (Test-Path .git) { git pull origin main 2>$null }

if (-not (Test-Path .venv)) {
    python -m venv .venv
}
& .\.venv\Scripts\Activate.ps1
pip install -q -r requirements.txt

Write-Host "==> env"
$env:ENVIRONMENT = "local"
$env:ALEMBIC_USE_SQLITE = "1"
if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
}
$env:REQUIRE_AUTH_FOR_WRITES = "false"
$env:COOKIE_SECURE = "false"

Write-Host "==> migrations"
alembic upgrade head

Write-Host "==> smoke tests"
pytest tests/unit/test_indices.py tests/unit/test_weather_alerts.py tests/unit/test_sentinel_fetcher.py -q

Write-Host "==> starting API on :8000"
Write-Host "Stop with Ctrl+C. Frontend: cd apps/web && npm install && npm run dev"
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

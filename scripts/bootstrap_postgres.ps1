# Windows: Docker Postgres + Alembic
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> docker compose up"
docker compose up --build -d postgres redis
Start-Sleep -Seconds 8
docker compose up -d api worker beat

$env:ENVIRONMENT = "staging"
$env:ALEMBIC_USE_SQLITE = "0"
if (-not $env:DATABASE_URL) {
  $env:DATABASE_URL = "postgresql+asyncpg://econojin:econojin@localhost:5432/econojin"
}

Write-Host "==> pip psycopg (for alembic sync)"
pip install -q "psycopg[binary]>=3.1"

Write-Host "==> alembic upgrade head"
alembic upgrade head

Write-Host "==> health"
curl.exe -s -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
Write-Host ""
Write-Host "Done. http://localhost:8000/docs"

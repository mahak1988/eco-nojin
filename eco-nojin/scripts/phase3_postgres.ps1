# Phase 3 — Postgres path (requires Docker Desktop or local Postgres)
# Usage: .\scripts\phase3_postgres.ps1

$ErrorActionPreference = "Stop"

if (Get-Command docker -ErrorAction SilentlyContinue) {
  Write-Host "Starting postgres + redis..."
  docker compose up -d postgres redis
  Start-Sleep -Seconds 8
} else {
  Write-Host "Docker not found. Start Postgres manually on :5432 (user/pass/db: econojin)."
}

$env:FORCE_POSTGRES = "1"
$env:DATABASE_URL = "postgresql+asyncpg://econojin:econojin@127.0.0.1:5432/econojin"
$env:ENVIRONMENT = "local"

Write-Host "Installing asyncpg if needed..."
pip install "asyncpg>=0.30.0" "psycopg[binary]>=3.1.0" -q

Write-Host "Alembic upgrade head..."
alembic upgrade head

Write-Host "Done. Run API with:"
Write-Host '  $env:FORCE_POSTGRES="1"; $env:DATABASE_URL="postgresql+asyncpg://econojin:econojin@127.0.0.1:5432/econojin"'
Write-Host "  uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000"
Write-Host "Check: curl http://localhost:8000/api/v1/science/status"

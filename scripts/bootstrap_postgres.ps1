# Postgres via Docker if available; else SQLite Alembic path
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

$dockerOk = $false
try {
  docker --version | Out-Null
  $dockerOk = $true
} catch {
  $dockerOk = $false
}

if ($dockerOk) {
  Write-Host "==> docker compose up"
  docker compose up --build -d postgres redis
  Start-Sleep -Seconds 8
  docker compose up -d api worker beat
  $env:ENVIRONMENT = "staging"
  $env:ALEMBIC_USE_SQLITE = "0"
  if (-not $env:DATABASE_URL) {
    $env:DATABASE_URL = "postgresql+asyncpg://econojin:econojin@localhost:5432/econojin"
  }
  pip install -q "psycopg[binary]>=3.1"
} else {
  Write-Host "Docker not found — using local SQLite for Alembic"
  Write-Host "Install Docker Desktop later for Postgres: https://docs.docker.com/desktop/setup/install/windows-install/"
  $env:ENVIRONMENT = "local"
  $env:ALEMBIC_USE_SQLITE = "1"
  $env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
}

Write-Host "==> alembic upgrade head"
alembic upgrade head

Write-Host "==> done"
Write-Host "Chain: 20260727_0001 -> 0002 (rbac) -> 0003 (users) -> 20260728_0001 (phase2)"

#Requires -Version 5.1
# Safe alembic upgrade for local SQLite (idempotent migrations + stamp heads fallback)
$ErrorActionPreference = "Continue"
$Root = if (Test-Path ".\apps\main.py") { (Get-Location).Path } else { Split-Path $PSScriptRoot -Parent }
Set-Location $Root

$py = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

$env:DATABASE_URL = if ($env:DATABASE_URL) { $env:DATABASE_URL } else { "sqlite+aiosqlite:///./apps/econojin.db" }
$env:PYTHONPATH = $Root

Write-Host "==> Python: $py"
Write-Host "==> DATABASE_URL=$($env:DATABASE_URL)"
Write-Host "==> alembic heads"
& $py -m alembic heads

Write-Host "==> alembic upgrade head"
& $py -m alembic upgrade head
if ($LASTEXITCODE -ne 0) {
  Write-Host "==> upgrade failed; stamping all heads (tables may already exist via create_all)"
  & $py -m alembic stamp heads
  Write-Host "==> stamp done; re-run upgrade (should be no-op)"
  & $py -m alembic upgrade head
}

Write-Host "==> alembic current"
& $py -m alembic current
Write-Host "Done."

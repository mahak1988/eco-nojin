#Requires -Version 5.1
<#
.SYNOPSIS
  Run Econojin API locally WITHOUT Docker (SQLite).
#>
$ErrorActionPreference = "Stop"

function Find-RepoRoot {
  $candidates = @(
    (Get-Location).Path,
    (Join-Path (Get-Location).Path "eco-nojin"),
    (Split-Path $PSScriptRoot -Parent)
  )
  foreach ($c in $candidates) {
    if (Test-Path (Join-Path $c "apps\main.py")) {
      return (Resolve-Path $c).Path
    }
  }
  return (Resolve-Path (Split-Path $PSScriptRoot -Parent)).Path
}

function Find-Python {
  foreach ($c in @("python", "py", "python3")) {
    try {
      $p = Get-Command $c -ErrorAction SilentlyContinue
      if ($p) {
        $ver = & $c -c "import sys; print(sys.executable)" 2>$null
        if ($ver) { return $ver.Trim() }
      }
    } catch {}
  }
  throw "Python 3.11+ not found on PATH."
}

$Root = Find-RepoRoot
Set-Location $Root
Write-Host "==> Repo root: $Root"

if ($env:VIRTUAL_ENV) {
  Write-Host "==> Clearing VIRTUAL_ENV=$($env:VIRTUAL_ENV)"
  Remove-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue
}

$py = Find-Python
Write-Host "==> Python: $py"

$venvPath = Join-Path $Root ".venv"
$venvPy = Join-Path $venvPath "Scripts\python.exe"
$activate = Join-Path $venvPath "Scripts\Activate.ps1"

# Recreate venv if broken (no python.exe OR no Activate.ps1)
if (-not (Test-Path $venvPy)) {
  Write-Host "==> Creating/repairing .venv at $venvPath"
  if (Test-Path $venvPath) {
    Remove-Item -Recurse -Force $venvPath
  }
  & $py -m venv $venvPath
  if (-not (Test-Path $venvPy)) {
    throw "Failed to create venv at $venvPath"
  }
}

if (Test-Path $activate) {
  Write-Host "==> Activating .venv"
  try { & $activate } catch { Write-Host "    Activate.ps1 skip (using venv python directly)" }
} else {
  Write-Host "==> No Activate.ps1 — using $venvPy directly"
}

Write-Host "==> Installing dependencies"
& $venvPy -m pip install -U pip setuptools wheel
if (Test-Path (Join-Path $Root "requirements.txt")) {
  & $venvPy -m pip install -r (Join-Path $Root "requirements.txt")
}

$env:ENVIRONMENT = "local"
$env:ALEMBIC_USE_SQLITE = "1"
$env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
$env:REQUIRE_AUTH_FOR_WRITES = "false"
$env:COOKIE_SECURE = "false"
$env:ENABLE_RATE_LIMIT = "true"
$env:ENABLE_AUDIT_LOG = "true"
$env:ENABLE_SPIDERGUARD = "false"
$env:PYTHONPATH = $Root

Write-Host "==> DATABASE_URL=$($env:DATABASE_URL)"
Write-Host "==> alembic upgrade head (best-effort)"
try {
  & $venvPy -m alembic upgrade head 2>&1 | Out-Host
} catch {
  Write-Host "    alembic warning: $_ (continuing)"
}

Write-Host "==> API http://0.0.0.0:8000  (Ctrl+C to stop)"
Write-Host "    FE: cd apps\web; pnpm install; pnpm dev"
# Reload only apps/ — avoid node_modules noise under eco-nojin/
& $venvPy -m uvicorn apps.main:app --reload --reload-dir apps --host 0.0.0.0 --port 8000

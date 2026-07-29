#Requires -Version 5.1
<#
.SYNOPSIS
  Run Econojin API locally WITHOUT Docker (SQLite).
  Fixes nested path issues: D:\econojin.com vs D:\econojin.com\eco-nojin
  and broken .venv without python.exe
#>
$ErrorActionPreference = "Stop"

function Find-RepoRoot {
  $candidates = @(
    (Get-Location).Path,
    (Join-Path (Get-Location).Path "eco-nojin"),
    (Split-Path $PSScriptRoot -Parent)
  )
  foreach ($c in $candidates) {
    if ((Test-Path (Join-Path $c "apps\main.py")) -or (Test-Path (Join-Path $c "apps\main"))) {
      return (Resolve-Path $c).Path
    }
    if (Test-Path (Join-Path $c "pyproject.toml")) {
      if (Test-Path (Join-Path $c "apps")) { return (Resolve-Path $c).Path }
    }
  }
  return (Resolve-Path (Split-Path $PSScriptRoot -Parent)).Path
}

function Find-Python {
  $cmds = @("python", "py", "python3")
  foreach ($c in $cmds) {
    try {
      $p = Get-Command $c -ErrorAction SilentlyContinue
      if ($p) {
        $ver = & $c -c "import sys; print(sys.executable)" 2>$null
        if ($ver) { return $ver.Trim() }
      }
    } catch {}
  }
  throw "Python 3.11+ not found on PATH. Install from python.org and re-open PowerShell."
}

$Root = Find-RepoRoot
Set-Location $Root
Write-Host "==> Repo root: $Root"

# Clear bad VIRTUAL_ENV that confuses uv
if ($env:VIRTUAL_ENV) {
  Write-Host "==> Clearing VIRTUAL_ENV=$($env:VIRTUAL_ENV)"
  Remove-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue
}

$py = Find-Python
Write-Host "==> Python: $py"

$venvPath = Join-Path $Root ".venv"
$venvPy = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPy)) {
  Write-Host "==> Creating .venv at $venvPath"
  if (Test-Path $venvPath) {
    Write-Host "    Removing broken .venv (no python.exe)"
    Remove-Item -Recurse -Force $venvPath
  }
  & $py -m venv $venvPath
  if (-not (Test-Path $venvPy)) {
    throw "Failed to create venv at $venvPath"
  }
}

Write-Host "==> Activating .venv"
& (Join-Path $venvPath "Scripts\Activate.ps1")

Write-Host "==> Installing dependencies"
& $venvPy -m pip install -U pip
if (Test-Path (Join-Path $Root "requirements.txt")) {
  & $venvPy -m pip install -r (Join-Path $Root "requirements.txt")
} else {
  & $venvPy -m pip install -e ".[dev]"
}

$env:ENVIRONMENT = "local"
$env:ALEMBIC_USE_SQLITE = "1"
$env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
$env:REQUIRE_AUTH_FOR_WRITES = "false"
$env:COOKIE_SECURE = "false"
$env:PYTHONPATH = $Root

Write-Host "==> DATABASE_URL=$($env:DATABASE_URL)"
Write-Host "==> alembic upgrade head (best-effort)"
try {
  & $venvPy -m alembic upgrade head
} catch {
  Write-Host "    alembic warning: $_ (continuing; create_all may run on startup)"
}

Write-Host "==> API http://0.0.0.0:8000  (Ctrl+C to stop)"
Write-Host "    FE: cd apps\web; npm install; npm run dev"
& $venvPy -m uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

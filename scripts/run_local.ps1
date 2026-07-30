#Requires -Version 5.1
# Run Econojin API locally WITHOUT Docker (SQLite).
# ASCII-only script for Windows PowerShell 5.1 compatibility.
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
  # Prefer 3.11/3.12 over bleeding-edge 3.14 when available
  $candidates = @(
    @{ Cmd = "py"; Args = @("-3.12", "-c", "import sys; print(sys.executable)") },
    @{ Cmd = "py"; Args = @("-3.11", "-c", "import sys; print(sys.executable)") },
    @{ Cmd = "py"; Args = @("-3.13", "-c", "import sys; print(sys.executable)") },
    @{ Cmd = "python"; Args = @("-c", "import sys; print(sys.executable)") },
    @{ Cmd = "py"; Args = @("-3", "-c", "import sys; print(sys.executable)") }
  )
  foreach ($item in $candidates) {
    try {
      $cmd = Get-Command $item.Cmd -ErrorAction SilentlyContinue
      if (-not $cmd) { continue }
      $out = & $item.Cmd @($item.Args) 2>$null
      if ($out) {
        $path = ($out | Select-Object -First 1).ToString().Trim()
        if ($path -and (Test-Path $path)) { return $path }
      }
    } catch {}
  }
  throw "Python not found. Install Python 3.11 or 3.12 from python.org"
}

$Root = Find-RepoRoot
Set-Location $Root
Write-Host "==> Repo root: $Root"

if ($env:VIRTUAL_ENV) {
  Write-Host "==> Clearing VIRTUAL_ENV"
  Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
}

$py = Find-Python
Write-Host "==> System Python: $py"

$venvPath = Join-Path $Root ".venv"
$venvPy = Join-Path $venvPath "Scripts\python.exe"
$useVenv = $false

if (Test-Path $venvPy) {
  $useVenv = $true
  Write-Host "==> Using existing venv: $venvPy"
} else {
  Write-Host "==> Trying to create .venv ..."
  if (Test-Path $venvPath) {
    Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
  }
  try {
    & $py -m venv $venvPath
    if (Test-Path $venvPy) {
      $useVenv = $true
      Write-Host "==> venv OK"
    } else {
      Write-Host "==> venv incomplete (common on Python 3.14 Windows). Using system Python."
    }
  } catch {
    Write-Host "==> venv failed: $_. Using system Python."
  }
}

if ($useVenv) {
  $runPy = $venvPy
} else {
  $runPy = $py
}

Write-Host "==> Runtime Python: $runPy"
Write-Host "==> Installing dependencies (may take a few minutes)"
& $runPy -m pip install -U pip setuptools wheel
if (Test-Path (Join-Path $Root "requirements.txt")) {
  & $runPy -m pip install -r (Join-Path $Root "requirements.txt")
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
  & $runPy -m alembic upgrade head
} catch {
  Write-Host "    alembic warning (continuing with create_all on startup)"
}

Write-Host "==> API http://127.0.0.1:8000  (Ctrl+C to stop)"
Write-Host "    FE: cd apps\web; pnpm install; pnpm dev"
& $runPy -m uvicorn apps.main:app --reload --reload-dir apps --host 0.0.0.0 --port 8000

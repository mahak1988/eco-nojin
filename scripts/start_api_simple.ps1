#Requires -Version 5.1
# Minimal API start when run_local has issues. No venv required.
$ErrorActionPreference = "Stop"
$Root = if (Test-Path ".\apps\main.py") { (Get-Location).Path } else { "D:\econojin.com" }
Set-Location $Root
$env:PYTHONPATH = $Root
$env:ENVIRONMENT = "local"
$env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
$env:ENABLE_RATE_LIMIT = "true"
$env:ENABLE_AUDIT_LOG = "true"
$env:ENABLE_SPIDERGUARD = "false"
$env:REQUIRE_AUTH_FOR_WRITES = "false"

$py = $null
foreach ($c in @("py -3.12", "py -3.11", "python")) {
  # resolved below
}
try {
  $py = (py -3.12 -c "import sys; print(sys.executable)" 2>$null)
} catch {}
if (-not $py) {
  try { $py = (py -3.11 -c "import sys; print(sys.executable)" 2>$null) } catch {}
}
if (-not $py) {
  $py = (python -c "import sys; print(sys.executable)")
}
$py = $py.ToString().Trim()
Write-Host "Python: $py"
& $py -m pip install -r requirements.txt
& $py -m uvicorn apps.main:app --reload --reload-dir apps --host 0.0.0.0 --port 8000

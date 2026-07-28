# Fix broken .venv / uv VIRTUAL_ENV mismatch on Windows
$ErrorActionPreference = "Stop"

$here = (Get-Location).Path
$roots = @($here, (Join-Path $here "eco-nojin"))
$root = $null
foreach ($r in $roots) {
  if (Test-Path (Join-Path $r "apps")) { $root = $r; break }
}
if (-not $root) { throw "Run from D:\econojin.com or D:\econojin.com\eco-nojin" }

Set-Location $root
Remove-Item Env:\VIRTUAL_ENV -ErrorAction SilentlyContinue

$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = Get-Command py }
$python = if ($py.Name -eq "py") { "py -3.12" } else { $py.Source }

Write-Host "Root: $root"
if (Test-Path ".venv") {
  $exe = Join-Path $root ".venv\Scripts\python.exe"
  if (-not (Test-Path $exe)) {
    Write-Host "Removing broken .venv"
    Remove-Item -Recurse -Force ".venv"
  }
}
if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Write-Host "Creating fresh .venv"
  if ($py.Name -eq "py") { py -3.12 -m venv .venv } else { & $python -m venv .venv }
}

& .\.venv\Scripts\Activate.ps1
python -m pip install -U pip
if (Test-Path requirements.txt) { pip install -r requirements.txt } else { pip install -e ".[dev]" }
Write-Host "OK. Use: python -m uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000"
Write-Host "Do NOT use 'uv run' unless uv project is configured; prefer python -m uvicorn"

# Force-sync main and verify farms seed + FE exports
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "==> git fetch + reset to origin/main (keeps untracked)"
git fetch origin
git checkout main
git reset --hard origin/main

Write-Host "==> Verify seed_farms uses COUNT"
$line = Select-String -Path "apps\farms\router.py" -Pattern "func.count" | Select-Object -First 1
if (-not $line) { throw "apps/farms/router.py still missing func.count — pull failed" }
Write-Host "OK farms router"

Write-Host "==> Verify simulationApi exports"
$exp = Select-String -Path "apps\web\src\lib\simulationApi.ts" -Pattern "export const API_BASE"
if (-not $exp) { throw "API_BASE export missing" }
Write-Host "OK simulationApi"

Write-Host "Done. Restart API: .\scripts\run_local.ps1"
Write-Host "Then: curl.exe -X POST -H `"User-Agent: Mozilla/5.0`" http://127.0.0.1:8000/api/v1/farms/seed-demo"

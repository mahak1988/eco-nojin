# Smoke-test Phase3 science API (PowerShell-safe JSON)
$ua = "User-Agent: Mozilla/5.0"
$base = "http://localhost:8000"

Write-Host "=== status ==="
curl.exe -H $ua "$base/api/v1/science/status"
Write-Host "`n=== runs ==="
curl.exe -H $ua "$base/api/v1/science/runs"
Write-Host "`n=== ndvi-canopy ==="
curl.exe -H $ua "$base/api/v1/science/ndvi-canopy?lat=32.65&lon=51.67&days=60"
Write-Host "`n=== aquacrop ==="
curl.exe -X POST -H $ua -H "Content-Type: application/json" -d '{"days":20,"persist":true}' "$base/api/v1/science/aquacrop-advanced"
Write-Host "`n=== swat ==="
curl.exe -X POST -H $ua -H "Content-Type: application/json" -d '{"area_km2":10}' "$base/api/v1/science/swat"

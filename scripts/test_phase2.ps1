#Requires -Version 5.1
# Phase 2 smoke tests — no Docker
$ErrorActionPreference = "Continue"
$base = "http://localhost:8000"

Write-Host "=== login ==="
'{"email":"farmer1@example.com","password":"SecurePass123!"}' | Set-Content -Encoding utf8 login.json
try {
  $login = Invoke-RestMethod -Uri "$base/api/v1/auth/login" -Method POST -ContentType "application/json" -InFile login.json
  $token = $login.accessToken
  Write-Host "token ok"
} catch {
  Write-Host "login failed: $_"
  exit 1
}
$H = @{ Authorization = "Bearer $token"; "User-Agent" = "Mozilla/5.0" }

function Hit($path, $method = "GET") {
  Write-Host "=== $method $path ==="
  try {
    if ($method -eq "POST") {
      Invoke-RestMethod -Method POST -Uri "$base$path" -Headers $H | ConvertTo-Json -Depth 4 -Compress
    } else {
      Invoke-RestMethod -Uri "$base$path" -Headers $H | ConvertTo-Json -Depth 3 -Compress
    }
  } catch {
    Write-Host "FAIL: $($_.Exception.Message)"
  }
}

Hit "/health"
Hit "/api/v1/monitoring/overview"
Hit "/api/v1/monitoring/seed-demo" "POST"
Hit "/api/v1/sensors?page=1&size=5"
Hit "/api/v1/alerts?page=1&size=5"
Hit "/api/v1/satellite/ndvi?lat=32.65&lon=51.67"
Hit "/api/v1/satellite/timeseries?lat=32.65&lon=51.67&days=30"
Hit "/api/v1/satellite/indices?lat=32.65&lon=51.67&days=30"
Hit "/api/v1/satellite/change-detection?lat=32.65&lon=51.67&days=90" "POST"
Hit "/api/v1/science/status"
Hit "/api/v1/debug/routers"

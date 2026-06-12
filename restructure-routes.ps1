# ============================================================
# Restructure Routes with Route Groups - Phase 4
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Restructure Routes with Route Groups - Phase 4" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# Helper function for safe git mv
function Safe-GitMove {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (-not (Test-Path $Source)) {
        Write-Host "  [SKIP] $Source (not found)" -ForegroundColor Yellow
        return $false
    }
    
    $destDir = Split-Path $Destination -Parent
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    try {
        git mv $Source $Destination 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [OK]   $Source -> $Destination" -ForegroundColor Green
            return $true
        } else {
            Move-Item -Path $Source -Destination $Destination -Force
            Write-Host "  [OK]   $Source -> $Destination (fallback)" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "  [ERR]  Failed: $Source - $_" -ForegroundColor Red
        return $false
    }
}

# ============================================================
# Step 1: Create route groups
# ============================================================
Write-Host "[Step 1/5] Creating route groups..." -ForegroundColor Cyan
Write-Host ""

$routeGroups = @(
    "apps\web\src\app\(auth)",
    "apps\web\src\app\(marketing)",
    "apps\web\src\app\(dashboard)",
    "apps\web\src\app\(modules)"
)

foreach ($group in $routeGroups) {
    if (-not (Test-Path $group)) {
        New-Item -ItemType Directory -Path $group -Force | Out-Null
        Write-Host "  [CREATED] $group" -ForegroundColor Green
    } else {
        Write-Host "  [EXISTS]  $group" -ForegroundColor DarkGray
    }
}

Write-Host ""

# ============================================================
# Step 2: Move auth pages
# ============================================================
Write-Host "[Step 2/5] Moving auth pages to (auth)/..." -ForegroundColor Cyan
Write-Host ""

$authPages = @("login", "register", "forgot-password", "reset-password", "auth")

$successCount = 0
$failCount = 0
$skipCount = 0

foreach ($page in $authPages) {
    $source = "apps\web\src\app\$page"
    $destination = "apps\web\src\app\(auth)\$page"
    
    if (Test-Path $source) {
        $result = Safe-GitMove -Source $source -Destination $destination
        if ($result) { $successCount++ } else { $failCount++ }
    } else {
        Write-Host "  [SKIP] $source (not found)" -ForegroundColor Yellow
        $skipCount++
    }
}

Write-Host ""

# ============================================================
# Step 3: Move marketing pages
# ============================================================
Write-Host "[Step 3/5] Moving marketing pages to (marketing)/..." -ForegroundColor Cyan
Write-Host ""

$marketingPages = @(
    "about", "blog", "contact", "academy", "policy", "privacy", "terms",
    "education", "community", "newsletter", "games", "library", "maintenance"
)

foreach ($page in $marketingPages) {
    $source = "apps\web\src\app\$page"
    $destination = "apps\web\src\app\(marketing)\$page"
    
    if (Test-Path $source) {
        $result = Safe-GitMove -Source $source -Destination $destination
        if ($result) { $successCount++ } else { $failCount++ }
    } else {
        Write-Host "  [SKIP] $source (not found)" -ForegroundColor Yellow
        $skipCount++
    }
}

Write-Host ""

# ============================================================
# Step 4: Move dashboard pages
# ============================================================
Write-Host "[Step 4/5] Moving dashboard pages to (dashboard)/..." -ForegroundColor Cyan
Write-Host ""

$dashboardPages = @(
    "profile", "shop", "ecocoin", "ecomining", "inventory", "financial",
    "accounting", "store", "desktop"
)

foreach ($page in $dashboardPages) {
    $source = "apps\web\src\app\$page"
    $destination = "apps\web\src\app\(dashboard)\$page"
    
    if (Test-Path $source) {
        $result = Safe-GitMove -Source $source -Destination $destination
        if ($result) { $successCount++ } else { $failCount++ }
    } else {
        Write-Host "  [SKIP] $source (not found)" -ForegroundColor Yellow
        $skipCount++
    }
}

Write-Host ""

# ============================================================
# Step 5: Move module pages
# ============================================================
Write-Host "[Step 5/5] Moving module pages to (modules)/..." -ForegroundColor Cyan
Write-Host ""

$modulePages = @(
    "gis", "analysis", "soil-water", "iot", "satellite", "weather",
    "drought", "forest", "carbon", "mrv", "hydrology", "erosion",
    "crop", "sentinel", "structures", "psychology"
)

foreach ($page in $modulePages) {
    $source = "apps\web\src\app\$page"
    $destination = "apps\web\src\app\(modules)\$page"
    
    if (Test-Path $source) {
        $result = Safe-GitMove -Source $source -Destination $destination
        if ($result) { $successCount++ } else { $failCount++ }
    } else {
        Write-Host "  [SKIP] $source (not found)" -ForegroundColor Yellow
        $skipCount++
    }
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 4 COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Moved:       $successCount" -ForegroundColor White
Write-Host "  Failed:      $failCount" -ForegroundColor White
Write-Host "  Skipped:     $skipCount" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'phase4: restructure routes with route groups'" -ForegroundColor White
Write-Host "  3. Proceed to Phase 5: Integrate econojin-library" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
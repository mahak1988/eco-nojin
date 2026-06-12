# ============================================================
# Restructure Routes v2 - Phase 4 (Corrected)
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Restructure Routes v2 - Phase 4 (Corrected)" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# Helper function for safe git mv
function Safe-GitMove {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (-not (Test-Path $Source)) {
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

$successCount = 0
$failCount = 0
$skipCount = 0

# ============================================================
# Step 1: Move [locale] pages to (modules)
# ============================================================
Write-Host "[Step 1/5] Moving [locale] pages to (modules)/..." -ForegroundColor Cyan
Write-Host ""

$localeMoves = @(
    @{ Source = "apps\web\src\app\[locale]\analysis"; Destination = "apps\web\src\app\(modules)\analysis" },
    @{ Source = "apps\web\src\app\[locale]\land-soil-water"; Destination = "apps\web\src\app\(modules)\land-soil-water" },
    @{ Source = "apps\web\src\app\[locale]\admin\land-soil-water"; Destination = "apps\web\src\app\(modules)\admin-land-soil-water" }
)

foreach ($move in $localeMoves) {
    if (Test-Path $move.Source) {
        $result = Safe-GitMove -Source $move.Source -Destination $move.Destination
        if ($result) { $successCount++ } else { $failCount++ }
    } else {
        Write-Host "  [SKIP] $($move.Source) (not found)" -ForegroundColor Yellow
        $skipCount++
    }
}

# Move [locale]/page.tsx to root if exists
if (Test-Path "apps\web\src\app\[locale]\page.tsx") {
    if (-not (Test-Path "apps\web\src\app\page.tsx")) {
        Safe-GitMove -Source "apps\web\src\app\[locale]\page.tsx" -Destination "apps\web\src\app\page.tsx"
        $successCount++
    } else {
        Write-Host "  [SKIP] [locale]/page.tsx (root page.tsx already exists)" -ForegroundColor Yellow
        $skipCount++
    }
}

# Remove empty [locale] folder
$localeRemaining = Get-ChildItem -Path "apps\web\src\app\[locale]" -ErrorAction SilentlyContinue
if ($null -eq $localeRemaining -or $localeRemaining.Count -eq 0) {
    Remove-Item -Path "apps\web\src\app\[locale]" -Force -Recurse
    Write-Host "  [DEL]  Removed empty [locale] folder" -ForegroundColor Gray
}

Write-Host ""

# ============================================================
# Step 2: Move admin to (admin)
# ============================================================
Write-Host "[Step 2/5] Moving admin/ to (admin)/..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "apps\web\src\app\admin") {
    if (-not (Test-Path "apps\web\src\app\(admin)")) {
        New-Item -ItemType Directory -Path "apps\web\src\app\(admin)" -Force | Out-Null
    }
    
    $adminItems = Get-ChildItem -Path "apps\web\src\app\admin" -Force
    
    foreach ($item in $adminItems) {
        $destPath = Join-Path "apps\web\src\app\(admin)" $item.Name
        
        if (Test-Path $destPath) {
            Write-Host "  [SKIP] $($item.Name) (already exists)" -ForegroundColor Yellow
            $skipCount++
            continue
        }
        
        try {
            git mv $item.FullName $destPath 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK]   admin/$($item.Name) -> (admin)/$($item.Name)" -ForegroundColor Green
                $successCount++
            } else {
                Move-Item -Path $item.FullName -Destination $destPath -Force
                Write-Host "  [OK]   admin/$($item.Name) -> (admin)/$($item.Name) (fallback)" -ForegroundColor Green
                $successCount++
            }
        } catch {
            Write-Host "  [ERR]  Failed: $($item.Name)" -ForegroundColor Red
            $failCount++
        }
    }
    
    # Remove empty admin folder
    $adminRemaining = Get-ChildItem -Path "apps\web\src\app\admin" -ErrorAction SilentlyContinue
    if ($null -eq $adminRemaining -or $adminRemaining.Count -eq 0) {
        Remove-Item -Path "apps\web\src\app\admin" -Force
        Write-Host "  [DEL]  Removed empty admin folder" -ForegroundColor Gray
    }
}

Write-Host ""

# ============================================================
# Step 3: Move ai and test-dashboard
# ============================================================
Write-Host "[Step 3/5] Moving ai/ and test-dashboard/..." -ForegroundColor Cyan
Write-Host ""

# Move ai to (modules)
if (Test-Path "apps\web\src\app\ai") {
    $result = Safe-GitMove -Source "apps\web\src\app\ai" -Destination "apps\web\src\app\(modules)\ai"
    if ($result) { $successCount++ } else { $failCount++ }
}

# Move test-dashboard to (dashboard)
if (Test-Path "apps\web\src\app\test-dashboard") {
    $result = Safe-GitMove -Source "apps\web\src\app\test-dashboard" -Destination "apps\web\src\app\(dashboard)\test-dashboard"
    if ($result) { $successCount++ } else { $failCount++ }
}

Write-Host ""

# ============================================================
# Step 4: Move component files from app/ root to components/
# ============================================================
Write-Host "[Step 4/5] Moving component files to components/..." -ForegroundColor Cyan
Write-Host ""

# These are components, not pages - should be in components/ folder
$componentFiles = @(
    "ActivityCard.tsx",
    "ChartsPanel.tsx",
    "CommentsSection.tsx",
    "Footer.tsx",
    "HydraulicConductivityChart.tsx",
    "LanguageSwitcher.tsx",
    "LoadingSpinner.tsx",
    "Logo.tsx",
    "MapPanel.tsx",
    "MoistureProfileChart.tsx",
    "Navbar.tsx",
    "RecommendedResources.tsx",
    "ResultsDashboard.tsx",
    "SimulationControls.tsx",
    "SimulationResultsTable.tsx",
    "SimulatorPanel.tsx",
    "SoilParametersForm.tsx",
    "StarRating.tsx",
    "StatCard.tsx",
    "UploadModal.tsx",
    "WalletButton.tsx",
    "WaterBalanceChart.tsx",
    "WishlistButton.tsx"
)

# Create components folder if not exists
if (-not (Test-Path "apps\web\src\components\app")) {
    New-Item -ItemType Directory -Path "apps\web\src\components\app" -Force | Out-Null
}

foreach ($file in $componentFiles) {
    $source = "apps\web\src\app\$file"
    $destination = "apps\web\src\components\app\$file"
    
    if (Test-Path $source) {
        $result = Safe-GitMove -Source $source -Destination $destination
        if ($result) { $successCount++ } else { $failCount++ }
    }
}

Write-Host ""

# ============================================================
# Step 5: Move provider files
# ============================================================
Write-Host "[Step 5/5] Moving provider files to providers/..." -ForegroundColor Cyan
Write-Host ""

$providerFiles = @(
    @{ Source = "apps\web\src\app\AuthProvider.tsx"; Destination = "apps\web\src\components\providers\AuthProvider.tsx" },
    @{ Source = "apps\web\src\app\ThemeProvider.tsx"; Destination = "apps\web\src\components\providers\ThemeProvider.tsx" },
    @{ Source = "apps\web\src\app\layout-providers.tsx"; Destination = "apps\web\src\components\providers\layout-providers.tsx" },
    @{ Source = "apps\web\src\app\providers.tsx"; Destination = "apps\web\src\components\providers\providers.tsx" },
    @{ Source = "apps\web\src\app\useAuth.tsx"; Destination = "apps\web\src\components\providers\useAuth.tsx" }
)

# Create providers folder if not exists
if (-not (Test-Path "apps\web\src\components\providers")) {
    New-Item -ItemType Directory -Path "apps\web\src\components\providers" -Force | Out-Null
}

foreach ($file in $providerFiles) {
    if (Test-Path $file.Source) {
        $result = Safe-GitMove -Source $file.Source -Destination $file.Destination
        if ($result) { $successCount++ } else { $failCount++ }
    }
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 4 (v2) COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Moved:       $successCount" -ForegroundColor White
Write-Host "  Failed:      $failCount" -ForegroundColor White
Write-Host "  Skipped:     $skipCount" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'phase4: restructure routes with route groups (v2)'" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
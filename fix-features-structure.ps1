# ============================================================
# Fix Features Double Nesting - Phase 3b Fix
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "   Fix Features Double Nesting - Phase 3b Fix" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# Helper function to move files up one level
function Fix-NestedFolder {
    param(
        [string]$BasePath
    )
    
    # Get the folder name (last part of path)
    $folderName = Split-Path $BasePath -Leaf
    $nestedPath = Join-Path $BasePath $folderName
    
    if (Test-Path $nestedPath) {
        Write-Host "Fixing: $nestedPath" -ForegroundColor Cyan
        
        # Move all contents from nested to base
        $items = Get-ChildItem -Path $nestedPath -Force
        
        foreach ($item in $items) {
            $destPath = Join-Path $BasePath $item.Name
            
            # Skip if destination already exists
            if (Test-Path $destPath) {
                Write-Host "  [SKIP] $($item.Name) (already exists)" -ForegroundColor Yellow
                continue
            }
            
            try {
                git mv $item.FullName $destPath 2>$null
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  [OK]   $($item.Name)" -ForegroundColor Green
                } else {
                    Move-Item -Path $item.FullName -Destination $destPath -Force
                    Write-Host "  [OK]   $($item.Name) (fallback)" -ForegroundColor Green
                }
            } catch {
                Write-Host "  [ERR]  Failed: $($item.Name) - $_" -ForegroundColor Red
            }
        }
        
        # Remove empty nested folder
        $remaining = Get-ChildItem -Path $nestedPath -Force -ErrorAction SilentlyContinue
        if ($null -eq $remaining -or $remaining.Count -eq 0) {
            Remove-Item -Path $nestedPath -Force
            Write-Host "  [DEL]  Removed empty folder: $nestedPath" -ForegroundColor Gray
        } else {
            Write-Host "  [WARN] Folder not empty after move: $nestedPath" -ForegroundColor Yellow
        }
        
        return $true
    } else {
        Write-Host "No nesting found: $nestedPath" -ForegroundColor DarkGray
        return $false
    }
}

# ============================================================
# Step 1: Fix nested folders
# ============================================================
Write-Host "[Step 1/2] Fixing nested folders..." -ForegroundColor Cyan
Write-Host ""

$foldersToFix = @(
    "packages\features\src\analysis",
    "packages\features\src\iot",
    "packages\features\src\blockchain",
    "packages\features\src\weather",
    "packages\features\src\satellite",
    "packages\features\src\drought",
    "packages\features\src\forest",
    "packages\features\src\soil-water"
)

$fixedCount = 0
foreach ($folder in $foldersToFix) {
    if (Fix-NestedFolder -BasePath $folder) {
        $fixedCount++
    }
    Write-Host ""
}

# Special case: soil-water/soil -> soil-water
$soilNestedPath = "packages\features\src\soil-water\soil"
if (Test-Path $soilNestedPath) {
    Write-Host "Fixing special case: soil-water/soil -> soil-water" -ForegroundColor Cyan
    
    $items = Get-ChildItem -Path $soilNestedPath -Force
    
    foreach ($item in $items) {
        $destPath = Join-Path "packages\features\src\soil-water" $item.Name
        
        if (Test-Path $destPath) {
            Write-Host "  [SKIP] $($item.Name) (already exists)" -ForegroundColor Yellow
            continue
        }
        
        try {
            git mv $item.FullName $destPath 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK]   $($item.Name)" -ForegroundColor Green
            } else {
                Move-Item -Path $item.FullName -Destination $destPath -Force
                Write-Host "  [OK]   $($item.Name) (fallback)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [ERR]  Failed: $($item.Name)" -ForegroundColor Red
        }
    }
    
    # Remove empty soil folder
    $remaining = Get-ChildItem -Path $soilNestedPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $remaining -or $remaining.Count -eq 0) {
        Remove-Item -Path $soilNestedPath -Force
        Write-Host "  [DEL]  Removed empty folder: $soilNestedPath" -ForegroundColor Gray
    }
}

# ============================================================
# Step 2: Verify structure
# ============================================================
Write-Host "[Step 2/2] Verifying structure..." -ForegroundColor Cyan
Write-Host ""

$expectedStructure = @(
    "packages\features\src\analysis\AnalysisDashboard.tsx",
    "packages\features\src\analysis\AnalysisForm.tsx",
    "packages\features\src\iot\IoTDashboard.tsx",
    "packages\features\src\blockchain\BlockchainDashboard.tsx",
    "packages\features\src\weather\WeatherDashboard.tsx",
    "packages\features\src\satellite\SatelliteDashboard.tsx",
    "packages\features\src\drought\DroughtDashboard.tsx",
    "packages\features\src\forest\ForestDashboard.tsx",
    "packages\features\src\soil-water\SoilDashboard.tsx"
)

$allCorrect = $true
foreach ($path in $expectedStructure) {
    if (Test-Path $path) {
        Write-Host "  [OK]   $path" -ForegroundColor Green
    } else {
        Write-Host "  [MISS] $path" -ForegroundColor Red
        $allCorrect = $false
    }
}

# Check for remaining nested folders
$nestedCheck = @(
    "packages\features\src\analysis\analysis",
    "packages\features\src\iot\iot",
    "packages\features\src\blockchain\blockchain",
    "packages\features\src\weather\weather",
    "packages\features\src\satellite\satellite",
    "packages\features\src\drought\drought",
    "packages\features\src\forest\forest",
    "packages\features\src\soil-water\soil"
)

Write-Host ""
Write-Host "Checking for nested folders:" -ForegroundColor Cyan
foreach ($nested in $nestedCheck) {
    if (Test-Path $nested) {
        Write-Host "  [WARN] Still exists: $nested" -ForegroundColor Yellow
        $allCorrect = $false
    } else {
        Write-Host "  [OK]   Removed: $nested" -ForegroundColor Green
    }
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  FEATURES STRUCTURE FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Fixed folders:  $fixedCount" -ForegroundColor White
Write-Host "  Structure:      $(if ($allCorrect) { 'CORRECT ✓' } else { 'NEEDS REVIEW ⚠' })" -ForegroundColor $(if ($allCorrect) { 'Green' } else { 'Yellow' })
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'fix(phase3b): correct double nesting in packages/features'" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
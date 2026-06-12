# ============================================================
# Move Feature Components to Packages - Phase 3b
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Move Feature Components - Phase 3b" -ForegroundColor Magenta
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
# Define what to move
# ============================================================

$moves = @(
    # GIS Components
    @{ Source = "apps\web\src\components\gis"; Destination = "packages\features\src\gis"; Type = "dir" },
    
    # Analysis Components
    @{ Source = "apps\web\src\components\analysis"; Destination = "packages\features\src\analysis"; Type = "dir" },
    
    # IoT Components
    @{ Source = "apps\web\src\components\iot"; Destination = "packages\features\src\iot"; Type = "dir" },
    
    # Blockchain Components
    @{ Source = "apps\web\src\components\blockchain"; Destination = "packages\features\src\blockchain"; Type = "dir" },
    
    # Weather Components
    @{ Source = "apps\web\src\components\weather"; Destination = "packages\features\src\weather"; Type = "dir" },
    
    # Satellite Components
    @{ Source = "apps\web\src\components\satellite"; Destination = "packages\features\src\satellite"; Type = "dir" },
    
    # Drought Components
    @{ Source = "apps\web\src\components\drought"; Destination = "packages\features\src\drought"; Type = "dir" },
    
    # Forest Components
    @{ Source = "apps\web\src\components\forest"; Destination = "packages\features\src\forest"; Type = "dir" },
    
    # Carbon Components (if exists)
    @{ Source = "apps\web\src\components\carbon"; Destination = "packages\features\src\carbon"; Type = "dir" },
    
    # Soil Components -> soil-water
    @{ Source = "apps\web\src\components\soil"; Destination = "packages\features\src\soil-water"; Type = "dir" }
)

# ============================================================
# Preview
# ============================================================

Write-Host "Planned moves:" -ForegroundColor Cyan
Write-Host ""

foreach ($move in $moves) {
    $exists = Test-Path $move.Source
    $icon = if ($exists) { "[FOUND]" } else { "[SKIP] " }
    $color = if ($exists) { "White" } else { "DarkYellow" }
    Write-Host "  $icon $($move.Source)" -ForegroundColor $color -NoNewline
    Write-Host " -> " -ForegroundColor DarkGray -NoNewline
    Write-Host "$($move.Destination)" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "This will move feature components to packages/features for reusability." -ForegroundColor Yellow
Write-Host "Git history will be preserved using 'git mv'." -ForegroundColor Yellow
Write-Host ""
Write-Host "Continue? (y/N): " -ForegroundColor Yellow -NoNewline
$confirm = Read-Host

if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "Cancelled." -ForegroundColor Cyan
    exit 0
}

# ============================================================
# Execute moves
# ============================================================

Write-Host ""
Write-Host "Executing moves..." -ForegroundColor Cyan
Write-Host ""

$successCount = 0
$failCount = 0
$skipCount = 0

foreach ($move in $moves) {
    if (-not (Test-Path $move.Source)) {
        $skipCount++
        continue
    }
    
    $result = Safe-GitMove -Source $move.Source -Destination $move.Destination
    
    if ($result) {
        $successCount++
    } else {
        $failCount++
    }
}

# ============================================================
# Update features index.ts
# ============================================================

Write-Host ""
Write-Host "Updating packages/features/src/index.ts..." -ForegroundColor Cyan

$featuresIndexContent = @(
    '// @econojin/features - Main entry point'
    ''
    '// GIS Components'
    'export * from "./gis";'
    ''
    '// Analysis Components'
    'export * from "./analysis";'
    ''
    '// IoT Components'
    'export * from "./iot";'
    ''
    '// Blockchain Components'
    'export * from "./blockchain";'
    ''
    '// Weather Components'
    'export * from "./weather";'
    ''
    '// Satellite Components'
    'export * from "./satellite";'
    ''
    '// Drought Components'
    'export * from "./drought";'
    ''
    '// Forest Components'
    'export * from "./forest";'
    ''
    '// Carbon Components'
    'export * from "./carbon";'
    ''
    '// Soil-Water Components'
    'export * from "./soil-water";'
)

$featuresIndexContent -join "`n" | Out-File -FilePath "packages\features\src\index.ts" -Encoding UTF8 -NoNewline
Write-Host "  Updated: packages/features/src/index.ts" -ForegroundColor Green

# ============================================================
# Final Report
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 3b COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Moved:       $successCount" -ForegroundColor White
Write-Host "  Failed:      $failCount" -ForegroundColor White
Write-Host "  Skipped:     $skipCount" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review moved files: git status" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'phase3b: move feature components'" -ForegroundColor White
Write-Host "  3. Proceed to Phase 4: Restructure apps/web routes" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
# ============================================================
# Move lib Code to Packages - Phase 3a
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Move lib Code to Packages - Phase 3a" -ForegroundColor Magenta
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
            # Fallback to regular move if git mv fails
            Move-Item -Path $Source -Destination $Destination -Force
            Write-Host "  [OK]   $Source -> $Destination (fallback)" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "  [ERR]  Failed to move $Source : $_" -ForegroundColor Red
        return $false
    }
}

# ============================================================
# Define what to move
# ============================================================

$moves = @(
    @{ Source = "apps\web\src\lib\api"; Destination = "packages\lib\src\api"; Type = "dir" },
    @{ Source = "apps\web\src\lib\utils.ts"; Destination = "packages\lib\src\utils\utils.ts"; Type = "file" },
    @{ Source = "apps\web\src\lib\utils"; Destination = "packages\lib\src\utils"; Type = "dir" },
    @{ Source = "apps\web\src\hooks"; Destination = "packages\lib\src\hooks"; Type = "dir" },
    @{ Source = "apps\web\src\lib\validation"; Destination = "packages\lib\src\validation"; Type = "dir" },
    @{ Source = "apps\web\src\lib\types.ts"; Destination = "packages\lib\src\types.ts"; Type = "file" },
    @{ Source = "apps\web\src\lib\api-client.ts"; Destination = "packages\lib\src\api\api-client.ts"; Type = "file" },
    @{ Source = "apps\web\src\lib\api-types.ts"; Destination = "packages\lib\src\api\api-types.ts"; Type = "file" },
    @{ Source = "apps\web\src\lib\auth.ts"; Destination = "packages\lib\src\auth.ts"; Type = "file" }
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
Write-Host "This will move shared code to packages/lib for reusability." -ForegroundColor Yellow
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
# Update lib index.ts to export moved files
# ============================================================

Write-Host ""
Write-Host "Updating packages/lib/src/index.ts..." -ForegroundColor Cyan

$libIndexContent = @(
    '// @econojin/lib - Main entry point'
    ''
    '// API Client'
    'export * from "./api";'
    ''
    '// Utils'
    'export * from "./utils";'
    ''
    '// Hooks'
    'export * from "./hooks";'
    ''
    '// Validation'
    'export * from "./validation";'
    ''
    '// Auth'
    'if (await import("./auth").then(() => true).catch(() => false)) {'
    '  export * from "./auth";'
    '}'
    ''
    '// Types'
    'export * from "./types";'
)

$libIndexContent -join "`n" | Out-File -FilePath "packages\lib\src\index.ts" -Encoding UTF8 -NoNewline
Write-Host "  Updated: packages/lib/src/index.ts" -ForegroundColor Green

# Update utils/index.ts to export from utils.ts if exists
if (Test-Path "packages\lib\src\utils\utils.ts") {
    $utilsIndex = @(
        '// Utils exports'
        'export * from "./utils";'
    )
    $utilsIndex -join "`n" | Out-File -FilePath "packages\lib\src\utils\index.ts" -Encoding UTF8 -NoNewline
    Write-Host "  Updated: packages/lib/src/utils/index.ts" -ForegroundColor Green
}

# ============================================================
# Final Report
# ============================================================

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 3a COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Moved:       $successCount" -ForegroundColor White
Write-Host "  Failed:      $failCount" -ForegroundColor White
Write-Host "  Skipped:     $skipCount" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review moved files: git status" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'phase3a: move lib code'" -ForegroundColor White
Write-Host "  3. Proceed to Phase 3b: Move features" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
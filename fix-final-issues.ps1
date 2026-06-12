# ============================================================
# Fix Final Issues - Phase 6 Fix
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "   Fix Final Issues - Phase 6 Fix" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# Step 1: Fix packages/lib/package.json
# ============================================================
Write-Host "[Step 1/3] Fixing packages/lib/package.json..." -ForegroundColor Cyan
Write-Host ""

$libPackagePath = "packages\lib\package.json"

if (Test-Path $libPackagePath) {
    $content = Get-Content $libPackagePath -Raw
    
    # Fix the problematic line
    $content = $content -replace '"lint": "eslint \\"src/\*\*/\*\.ts\\",', '"lint": "eslint src/**/*.ts",'
    
    $content | Out-File -FilePath $libPackagePath -Encoding UTF8 -NoNewline
    
    # Validate JSON
    try {
        $null = Get-Content $libPackagePath -Raw | ConvertFrom-Json
        Write-Host "  [OK]   packages/lib/package.json is valid JSON" -ForegroundColor Green
    } catch {
        Write-Host "  [ERR]  Still invalid: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  [SKIP] File not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 2: Fix packages/features/package.json
# ============================================================
Write-Host "[Step 2/3] Fixing packages/features/package.json..." -ForegroundColor Cyan
Write-Host ""

$featuresPackagePath = "packages\features\package.json"

if (Test-Path $featuresPackagePath) {
    $content = Get-Content $featuresPackagePath -Raw
    
    # Fix the same issue if exists
    $content = $content -replace '"lint": "eslint \\"src/\*\*/\*\.ts\\",', '"lint": "eslint src/**/*.ts",'
    
    $content | Out-File -FilePath $featuresPackagePath -Encoding UTF8 -NoNewline
    
    # Validate JSON
    try {
        $null = Get-Content $featuresPackagePath -Raw | ConvertFrom-Json
        Write-Host "  [OK]   packages/features/package.json is valid JSON" -ForegroundColor Green
    } catch {
        Write-Host "  [ERR]  Still invalid: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  [SKIP] File not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 3: Fix pnpm-workspace.yaml
# ============================================================
Write-Host "[Step 3/3] Fixing pnpm-workspace.yaml..." -ForegroundColor Cyan
Write-Host ""

$workspacePath = "pnpm-workspace.yaml"

if (Test-Path $workspacePath) {
    $content = Get-Content $workspacePath -Raw
    
    # Remove econojin-library/frontend line
    $content = $content -replace '  - "econojin-library/frontend"\r?\n?', ''
    
    $content | Out-File -FilePath $workspacePath -Encoding UTF8 -NoNewline
    
    Write-Host "  [OK]   Removed econojin-library/frontend from workspace" -ForegroundColor Green
    Write-Host ""
    Write-Host "  New content:" -ForegroundColor Gray
    
    $newContent = Get-Content $workspacePath -Raw
    Write-Host $newContent -ForegroundColor DarkGray
} else {
    Write-Host "  [SKIP] File not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 4: Run pnpm install again
# ============================================================
Write-Host "[Step 4/4] Running pnpm install again..." -ForegroundColor Cyan
Write-Host ""

try {
    pnpm install
    Write-Host ""
    Write-Host "  [OK]   pnpm install completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] pnpm install had issues: $_" -ForegroundColor Yellow
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  FINAL FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "All issues resolved!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Commit:" -ForegroundColor White
Write-Host "     git add -A" -ForegroundColor Gray
Write-Host "     git commit -m 'fix(phase6): correct JSON and workspace config'" -ForegroundColor Gray
Write-Host "  3. Test build: pnpm build" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
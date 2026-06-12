# ============================================================
# Fix Double Nesting Structure - Phase 3a Fix
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "   Fix Double Nesting Structure - Phase 3a Fix" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# Helper function to move files up one level
function Fix-NestedFolder {
    param(
        [string]$BasePath  # e.g., "packages/lib/src/api"
    )
    
    $nestedPath = Join-Path $BasePath (Split-Path $BasePath -Leaf)
    
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
Write-Host "[Step 1/3] Fixing nested folders..." -ForegroundColor Cyan
Write-Host ""

$foldersToFix = @(
    "packages\lib\src\api",
    "packages\lib\src\hooks",
    "packages\lib\src\utils",
    "packages\lib\src\validation"
)

$fixedCount = 0
foreach ($folder in $foldersToFix) {
    if (Fix-NestedFolder -BasePath $folder) {
        $fixedCount++
    }
    Write-Host ""
}

# ============================================================
# Step 2: Remove Python files (__init__.py)
# ============================================================
Write-Host "[Step 2/3] Removing Python files..." -ForegroundColor Cyan
Write-Host ""

$pythonFiles = Get-ChildItem -Path "packages\lib\src" -Recurse -Filter "__init__.py"

if ($pythonFiles.Count -gt 0) {
    foreach ($file in $pythonFiles) {
        try {
            git rm $file.FullName 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [DEL]  $($file.FullName)" -ForegroundColor Green
            } else {
                Remove-Item -Path $file.FullName -Force
                Write-Host "  [DEL]  $($file.FullName) (fallback)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [ERR]  Failed to delete: $($file.FullName)" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  No Python files found" -ForegroundColor DarkGray
}

Write-Host ""

# ============================================================
# Step 3: Verify structure
# ============================================================
Write-Host "[Step 3/3] Verifying structure..." -ForegroundColor Cyan
Write-Host ""

$expectedStructure = @(
    "packages\lib\src\api\client.ts",
    "packages\lib\src\api\endpoints.ts",
    "packages\lib\src\hooks\useApi.ts",
    "packages\lib\src\hooks\index.ts",
    "packages\lib\src\utils\storage.ts",
    "packages\lib\src\validation\auth.schema.ts"
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
    "packages\lib\src\api\api",
    "packages\lib\src\hooks\hooks",
    "packages\lib\src\utils\utils",
    "packages\lib\src\validation\validation"
)

foreach ($nested in $nestedCheck) {
    if (Test-Path $nested) {
        Write-Host "  [WARN] Nested folder still exists: $nested" -ForegroundColor Yellow
        $allCorrect = $false
    }
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  STRUCTURE FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Fixed folders:  $fixedCount" -ForegroundColor White
Write-Host "  Python files:   $($pythonFiles.Count) removed" -ForegroundColor White
Write-Host "  Structure:      $(if ($allCorrect) { 'CORRECT' } else { 'NEEDS REVIEW' })" -ForegroundColor $(if ($allCorrect) { 'Green' } else { 'Yellow' })
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Commit: git add -A && git commit -m 'fix: correct double nesting in packages/lib'" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
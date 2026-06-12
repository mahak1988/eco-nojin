# ============================================================
# Fix Remaining Issues - Phase 3a Final Fix
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "   Fix Remaining Issues - Phase 3a Final Fix" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# Step 1: Remove Python __init__.py files (force delete)
# ============================================================
Write-Host "[Step 1/4] Removing Python __init__.py files..." -ForegroundColor Cyan
Write-Host ""

$pythonFiles = Get-ChildItem -Path "packages\lib\src" -Recurse -Filter "__init__.py" -ErrorAction SilentlyContinue

if ($pythonFiles.Count -gt 0) {
    foreach ($file in $pythonFiles) {
        try {
            # Force remove (not git rm, just delete)
            Remove-Item -Path $file.FullName -Force
            Write-Host "  [DEL]  $($file.FullName)" -ForegroundColor Green
        } catch {
            Write-Host "  [ERR]  Failed: $($file.FullName) - $_" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  No Python files found" -ForegroundColor DarkGray
}

Write-Host ""

# ============================================================
# Step 2: Handle hooks/hooks/index.ts
# ============================================================
Write-Host "[Step 2/4] Handling hooks/hooks/index.ts..." -ForegroundColor Cyan
Write-Host ""

$hooksIndexPath = "packages\lib\src\hooks\index.ts"
$nestedHooksIndexPath = "packages\lib\src\hooks\hooks\index.ts"

if (Test-Path $nestedHooksIndexPath) {
    # Read content of nested index.ts
    $nestedContent = Get-Content $nestedHooksIndexPath -Raw
    
    # Check if main index.ts exists
    if (Test-Path $hooksIndexPath) {
        # Append nested content to main index.ts
        $mainContent = Get-Content $hooksIndexPath -Raw
        
        # Only append if content is different
        if ($nestedContent -ne $mainContent) {
            $combinedContent = $mainContent + "`n`n// Additional exports from nested index`n" + $nestedContent
            $combinedContent | Out-File -FilePath $hooksIndexPath -Encoding UTF8 -NoNewline
            Write-Host "  [MERGE] Combined index.ts files" -ForegroundColor Green
        } else {
            Write-Host "  [SKIP] Content is identical" -ForegroundColor DarkGray
        }
    } else {
        # Just move it
        Move-Item -Path $nestedHooksIndexPath -Destination $hooksIndexPath -Force
        Write-Host "  [MOVE] Moved nested index.ts to hooks/index.ts" -ForegroundColor Green
    }
    
    # Remove nested file if still exists
    if (Test-Path $nestedHooksIndexPath) {
        Remove-Item -Path $nestedHooksIndexPath -Force
        Write-Host "  [DEL]  Removed nested index.ts" -ForegroundColor Green
    }
} else {
    Write-Host "  Nested index.ts not found" -ForegroundColor DarkGray
}

Write-Host ""

# ============================================================
# Step 3: Remove empty hooks/hooks/gis folder
# ============================================================
Write-Host "[Step 3/4] Removing empty folders..." -ForegroundColor Cyan
Write-Host ""

$emptyFolders = @(
    "packages\lib\src\hooks\hooks\gis",
    "packages\lib\src\hooks\hooks"
)

foreach ($folder in $emptyFolders) {
    if (Test-Path $folder) {
        # Check if folder is empty
        $items = Get-ChildItem -Path $folder -Force -ErrorAction SilentlyContinue
        
        if ($null -eq $items -or $items.Count -eq 0) {
            Remove-Item -Path $folder -Force -Recurse
            Write-Host "  [DEL]  Removed empty folder: $folder" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] Folder not empty: $folder ($($items.Count) items)" -ForegroundColor Yellow
            
            # Try to remove anyway if it's the nested hooks folder
            if ($folder -like "*\hooks\hooks") {
                # Move remaining items up
                foreach ($item in $items) {
                    $destPath = Join-Path "packages\lib\src\hooks" $item.Name
                    
                    if (-not (Test-Path $destPath)) {
                        try {
                            Move-Item -Path $item.FullName -Destination $destPath -Force
                            Write-Host "    [MOVE] $($item.Name)" -ForegroundColor Green
                        } catch {
                            Write-Host "    [ERR]  Failed: $($item.Name)" -ForegroundColor Red
                        }
                    }
                }
                
                # Now try to remove
                $remaining = Get-ChildItem -Path $folder -Force -ErrorAction SilentlyContinue
                if ($null -eq $remaining -or $remaining.Count -eq 0) {
                    Remove-Item -Path $folder -Force -Recurse
                    Write-Host "  [DEL]  Removed folder after moving contents: $folder" -ForegroundColor Green
                }
            }
        }
    } else {
        Write-Host "  [OK]   Folder not found: $folder" -ForegroundColor DarkGray
    }
}

Write-Host ""

# ============================================================
# Step 4: Final verification
# ============================================================
Write-Host "[Step 4/4] Final verification..." -ForegroundColor Cyan
Write-Host ""

$checks = @(
    @{ Path = "packages\lib\src\api\client.ts"; Desc = "API client" },
    @{ Path = "packages\lib\src\api\endpoints.ts"; Desc = "API endpoints" },
    @{ Path = "packages\lib\src\hooks\useApi.ts"; Desc = "useApi hook" },
    @{ Path = "packages\lib\src\hooks\index.ts"; Desc = "Hooks index" },
    @{ Path = "packages\lib\src\utils\storage.ts"; Desc = "Storage utils" },
    @{ Path = "packages\lib\src\validation\auth.schema.ts"; Desc = "Auth validation" }
)

$allCorrect = $true
foreach ($check in $checks) {
    if (Test-Path $check.Path) {
        Write-Host "  [OK]   $($check.Desc): $($check.Path)" -ForegroundColor Green
    } else {
        Write-Host "  [MISS] $($check.Desc): $($check.Path)" -ForegroundColor Red
        $allCorrect = $false
    }
}

# Check for nested folders
$nestedPaths = @(
    "packages\lib\src\api\api",
    "packages\lib\src\hooks\hooks",
    "packages\lib\src\utils\utils",
    "packages\lib\src\validation\validation"
)

Write-Host ""
Write-Host "Checking for nested folders:" -ForegroundColor Cyan
foreach ($nested in $nestedPaths) {
    if (Test-Path $nested) {
        Write-Host "  [WARN] Still exists: $nested" -ForegroundColor Yellow
        $allCorrect = $false
    } else {
        Write-Host "  [OK]   Removed: $nested" -ForegroundColor Green
    }
}

# Check for Python files
$remainingPython = Get-ChildItem -Path "packages\lib\src" -Recurse -Filter "__init__.py" -ErrorAction SilentlyContinue
Write-Host ""
Write-Host "Checking for Python files:" -ForegroundColor Cyan
if ($remainingPython.Count -eq 0) {
    Write-Host "  [OK]   No __init__.py files found" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Found $($remainingPython.Count) __init__.py files:" -ForegroundColor Yellow
    foreach ($file in $remainingPython) {
        Write-Host "         $($file.FullName)" -ForegroundColor Yellow
    }
    $allCorrect = $false
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  FINAL FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Structure: $(if ($allCorrect) { 'CORRECT ✓' } else { 'NEEDS MANUAL REVIEW ⚠' })" -ForegroundColor $(if ($allCorrect) { 'Green' } else { 'Yellow' })
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

if ($allCorrect) {
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Review: git status" -ForegroundColor White
    Write-Host "  2. Stage all: git add -A" -ForegroundColor White
    Write-Host "  3. Commit: git commit -m 'fix(phase3a): correct structure and remove Python files'" -ForegroundColor White
} else {
    Write-Host "Manual review needed. Check the warnings above." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
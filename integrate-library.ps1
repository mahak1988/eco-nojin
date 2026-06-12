# ============================================================
# Integrate econojin-library - Phase 5
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Integrate econojin-library - Phase 5" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Check if econojin-library exists
# ============================================================
Write-Host "[Step 1/6] Checking econojin-library..." -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path "econojin-library\frontend")) {
    Write-Host "  [ERROR] econojin-library/frontend not found!" -ForegroundColor Red
    exit 1
}

Write-Host "  [OK]   econojin-library/frontend exists" -ForegroundColor Green

# Show current structure
$libFiles = Get-ChildItem -Path "econojin-library\frontend" -Recurse -File | Measure-Object
Write-Host "  [INFO] Found $($libFiles.Count) files in econojin-library/frontend" -ForegroundColor Cyan

Write-Host ""

# ============================================================
# Step 2: Create apps/library directory
# ============================================================
Write-Host "[Step 2/6] Creating apps/library..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "apps\library") {
    Write-Host "  [WARN] apps/library already exists" -ForegroundColor Yellow
    Write-Host "  Continue anyway? (y/N): " -ForegroundColor Yellow -NoNewline
    $confirm = Read-Host
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Cancelled." -ForegroundColor Cyan
        exit 0
    }
} else {
    New-Item -ItemType Directory -Path "apps\library" -Force | Out-Null
    Write-Host "  [CREATED] apps/library" -ForegroundColor Green
}

Write-Host ""

# ============================================================
# Step 3: Move econojin-library/frontend to apps/library
# ============================================================
Write-Host "[Step 3/6] Moving econojin-library/frontend to apps/library..." -ForegroundColor Cyan
Write-Host ""

try {
    # Get all items from frontend
    $items = Get-ChildItem -Path "econojin-library\frontend" -Force
    
    foreach ($item in $items) {
        $destPath = Join-Path "apps\library" $item.Name
        
        if (Test-Path $destPath) {
            Write-Host "  [SKIP] $($item.Name) (already exists in apps/library)" -ForegroundColor Yellow
            continue
        }
        
        try {
            git mv $item.FullName $destPath 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK]   $($item.Name) -> apps/library/$($item.Name)" -ForegroundColor Green
            } else {
                Move-Item -Path $item.FullName -Destination $destPath -Force
                Write-Host "  [OK]   $($item.Name) -> apps/library/$($item.Name) (fallback)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [ERR]  Failed: $($item.Name) - $_" -ForegroundColor Red
        }
    }
    
    # Remove empty frontend folder
    $remaining = Get-ChildItem -Path "econojin-library\frontend" -Force -ErrorAction SilentlyContinue
    if ($null -eq $remaining -or $remaining.Count -eq 0) {
        Remove-Item -Path "econojin-library\frontend" -Force
        Write-Host "  [DEL]  Removed empty econojin-library/frontend" -ForegroundColor Gray
    }
    
    # Check if econojin-library is now empty
    $libRemaining = Get-ChildItem -Path "econojin-library" -Force -ErrorAction SilentlyContinue
    if ($null -eq $libRemaining -or $libRemaining.Count -eq 0) {
        Remove-Item -Path "econojin-library" -Force
        Write-Host "  [DEL]  Removed empty econojin-library" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "  [ERROR] Failed to move: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================
# Step 4: Update apps/library/package.json
# ============================================================
Write-Host "[Step 4/6] Updating apps/library/package.json..." -ForegroundColor Cyan
Write-Host ""

$libraryPackageJsonPath = "apps\library\package.json"

if (Test-Path $libraryPackageJsonPath) {
    # Read current package.json
    $packageJson = Get-Content $libraryPackageJsonPath -Raw | ConvertFrom-Json
    
    # Update name
    $packageJson.name = "@econojin/library"
    
    # Add workspace dependencies
    if (-not $packageJson.dependencies) {
        $packageJson | Add-Member -NotePropertyName "dependencies" -NotePropertyValue @{} -Force
    }
    
    # Save back
    $packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $libraryPackageJsonPath -Encoding UTF8 -NoNewline
    
    Write-Host "  [OK]   Updated package.json name to @econojin/library" -ForegroundColor Green
} else {
    Write-Host "  [WARN] package.json not found in apps/library" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 5: Update pnpm-workspace.yaml
# ============================================================
Write-Host "[Step 5/6] Updating pnpm-workspace.yaml..." -ForegroundColor Cyan
Write-Host ""

$workspaceYamlPath = "pnpm-workspace.yaml"

if (Test-Path $workspaceYamlPath) {
    $content = Get-Content $workspaceYamlPath -Raw
    
    # Remove old econojin-library/frontend entry if exists
    $content = $content -replace '  - "econojin-library/frontend"\r?\n?', ''
    
    # Ensure apps/* is present (it should already include apps/library)
    if ($content -notmatch 'apps/\*') {
        $content = "packages:`n  - `"apps/*`"`n  - `"packages/*`"`n"
    }
    
    $content | Out-File -FilePath $workspaceYamlPath -Encoding UTF8 -NoNewline
    
    Write-Host "  [OK]   Updated pnpm-workspace.yaml" -ForegroundColor Green
    Write-Host "       Removed: econojin-library/frontend" -ForegroundColor Gray
    Write-Host "       apps/* now includes apps/library" -ForegroundColor Gray
} else {
    Write-Host "  [WARN] pnpm-workspace.yaml not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 6: Verify structure
# ============================================================
Write-Host "[Step 6/6] Verifying structure..." -ForegroundColor Cyan
Write-Host ""

$expectedFiles = @(
    "apps\library\package.json",
    "apps\library\next.config.js",
    "apps\library\app\layout.tsx",
    "apps\library\app\[locale]\page.tsx"
)

$allCorrect = $true
foreach ($file in $expectedFiles) {
    if (Test-Path $file) {
        Write-Host "  [OK]   $file" -ForegroundColor Green
    } else {
        Write-Host "  [MISS] $file" -ForegroundColor Red
        $allCorrect = $false
    }
}

# Check that old location is gone
if (Test-Path "econojin-library") {
    Write-Host "  [WARN] econojin-library still exists" -ForegroundColor Yellow
    $allCorrect = $false
} else {
    Write-Host "  [OK]   econojin-library removed" -ForegroundColor Green
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 5 COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Structure: $(if ($allCorrect) { 'CORRECT ✓' } else { 'NEEDS REVIEW ⚠' })" -ForegroundColor $(if ($allCorrect) { 'Green' } else { 'Yellow' })
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Install: pnpm install" -ForegroundColor White
Write-Host "  3. Commit: git add -A && git commit -m 'phase5: integrate econojin-library'" -ForegroundColor White
Write-Host "  4. Proceed to Phase 6: Update imports and test build" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
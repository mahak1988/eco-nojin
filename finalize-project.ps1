# ============================================================
# Finalize Project - Phase 6 (FIXED)
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Finalize Project - Phase 6" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Verify apps/library structure
# ============================================================
Write-Host "[Step 1/6] Verifying apps/library structure..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "apps\library") {
    Write-Host "  [OK]   apps/library exists" -ForegroundColor Green
    
    $libFiles = Get-ChildItem -Path "apps\library" -Recurse -File | Measure-Object
    Write-Host "  [INFO] Found $($libFiles.Count) files in apps/library" -ForegroundColor Cyan
    
    $keyFiles = @("package.json", "next.config.js", "app\layout.tsx")
    foreach ($file in $keyFiles) {
        $path = Join-Path "apps\library" $file
        if (Test-Path $path) {
            Write-Host "  [OK]   $file" -ForegroundColor Green
        } else {
            Write-Host "  [MISS] $file" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  [WARN] apps/library not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 2: Update root package.json
# ============================================================
Write-Host "[Step 2/6] Updating root package.json..." -ForegroundColor Cyan
Write-Host ""

$rootPackageJsonPath = "package.json"

if (Test-Path $rootPackageJsonPath) {
    $packageJson = Get-Content $rootPackageJsonPath -Raw | ConvertFrom-Json
    
    if (-not $packageJson.scripts) {
        $packageJson | Add-Member -NotePropertyName "scripts" -NotePropertyValue @{} -Force
    }
    
    $scriptsToAdd = @{
        "build" = "turbo run build"
        "dev" = "turbo run dev"
        "lint" = "turbo run lint"
        "type-check" = "turbo run type-check"
        "clean" = "turbo run clean"
    }
    
    foreach ($key in $scriptsToAdd.Keys) {
        if (-not $packageJson.scripts.$key) {
            $packageJson.scripts | Add-Member -NotePropertyName $key -NotePropertyValue $scriptsToAdd[$key] -Force
            Write-Host "  [ADD]  script: $key" -ForegroundColor Green
        } else {
            Write-Host "  [SKIP] script: $key (already exists)" -ForegroundColor DarkGray
        }
    }
    
    if (-not $packageJson.devDependencies) {
        $packageJson | Add-Member -NotePropertyName "devDependencies" -NotePropertyValue @{} -Force
    }
    
    if (-not $packageJson.devDependencies.turbo) {
        $packageJson.devDependencies | Add-Member -NotePropertyName "turbo" -NotePropertyValue "^1.10.0" -Force
        Write-Host "  [ADD]  devDependency: turbo" -ForegroundColor Green
    }
    
    $packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath $rootPackageJsonPath -Encoding UTF8 -NoNewline
    
    Write-Host "  [OK]   Updated root package.json" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Root package.json not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 3: Verify pnpm-workspace.yaml
# ============================================================
Write-Host "[Step 3/6] Verifying pnpm-workspace.yaml..." -ForegroundColor Cyan
Write-Host ""

$workspaceYamlPath = "pnpm-workspace.yaml"

if (Test-Path $workspaceYamlPath) {
    $content = Get-Content $workspaceYamlPath -Raw
    Write-Host "  Current content:" -ForegroundColor Gray
    Write-Host $content -ForegroundColor DarkGray
    
    if ($content -match 'apps/\*') {
        Write-Host "  [OK]   apps/* is in workspace" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] apps/* not found in workspace" -ForegroundColor Yellow
    }
    
    if ($content -match 'packages/\*') {
        Write-Host "  [OK]   packages/* is in workspace" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] packages/* not found in workspace" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [ERROR] pnpm-workspace.yaml not found!" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# Step 4: Verify turbo.json
# ============================================================
Write-Host "[Step 4/6] Verifying turbo.json..." -ForegroundColor Cyan
Write-Host ""

if (Test-Path "turbo.json") {
    Write-Host "  [OK]   turbo.json exists" -ForegroundColor Green
} else {
    Write-Host "  [WARN] turbo.json not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 5: Run pnpm install
# ============================================================
Write-Host "[Step 5/6] Running pnpm install..." -ForegroundColor Cyan
Write-Host ""

try {
    pnpm install
    Write-Host ""
    Write-Host "  [OK]   pnpm install completed" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] pnpm install failed: $_" -ForegroundColor Yellow
    Write-Host "  You may need to run it manually: pnpm install" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 6: Final structure report
# ============================================================
Write-Host "[Step 6/6] Final structure report..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Monorepo Structure:" -ForegroundColor White
Write-Host "  apps/" -ForegroundColor Cyan
Get-ChildItem -Path "apps" -Directory | ForEach-Object {
    Write-Host "    - $($_.Name)/" -ForegroundColor White
}

Write-Host "  packages/" -ForegroundColor Cyan
Get-ChildItem -Path "packages" -Directory | ForEach-Object {
    Write-Host "    - $($_.Name)/" -ForegroundColor White
}

Write-Host ""
Write-Host "Root config files:" -ForegroundColor White
Get-ChildItem -Path . -File | Where-Object { $_.Extension -in '.json','.yaml','.js','.ts' } | ForEach-Object {
    Write-Host "  - $($_.Name)" -ForegroundColor White
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 6 COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Project is now fully restructured!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review: git status" -ForegroundColor White
Write-Host "  2. Commit:" -ForegroundColor White
Write-Host "     git add -A" -ForegroundColor Gray
Write-Host "     git commit -m 'phase6: finalize project structure'" -ForegroundColor Gray
Write-Host "  3. Test: pnpm build" -ForegroundColor White
Write-Host "  4. Optional: Update import paths to use @econojin/lib" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
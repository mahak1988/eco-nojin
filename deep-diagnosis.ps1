$ErrorActionPreference = "Continue"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   DEEP DIAGNOSIS - Finding the Ghost Route" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

$root = (Get-Location).Path

# ====================================================================
# TEST 1: Search for ANY login/page.tsx in entire project
# ====================================================================
Write-Host "[TEST 1] Searching for ANY 'login' directory in project..." -ForegroundColor Cyan
Write-Host ""

$loginDirs = Get-ChildItem -Path . -Recurse -Directory -Filter "login" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*node_modules*" -and $_.FullName -notlike "*_QUARANTINE*" -and $_.FullName -notlike "*.backup*" -and $_.FullName -notlike "*.venv*" }

Write-Host "  Found $($loginDirs.Count) 'login' directories:" -ForegroundColor Gray
foreach ($dir in $loginDirs) {
    $rel = $dir.FullName.Substring($root.Length + 1)
    Write-Host "    - $rel" -ForegroundColor White
}
Write-Host ""

# ====================================================================
# TEST 2: Search for ANY register directory
# ====================================================================
Write-Host "[TEST 2] Searching for ANY 'register' directory..." -ForegroundColor Cyan
Write-Host ""

$registerDirs = Get-ChildItem -Path . -Recurse -Directory -Filter "register" -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*node_modules*" -and $_.FullName -notlike "*_QUARANTINE*" -and $_.FullName -notlike "*.backup*" -and $_.FullName -notlike "*.venv*" }

Write-Host "  Found $($registerDirs.Count) 'register' directories:" -ForegroundColor Gray
foreach ($dir in $registerDirs) {
    $rel = $dir.FullName.Substring($root.Length + 1)
    Write-Host "    - $rel" -ForegroundColor White
}
Write-Host ""

# ====================================================================
# TEST 3: Check apps/web/app (WITHOUT src)
# ====================================================================
Write-Host "[TEST 3] Checking apps/web/app (WITHOUT src)..." -ForegroundColor Cyan
Write-Host ""

$appNoSrc = "apps\web\app"
if (Test-Path -LiteralPath $appNoSrc) {
    Write-Host "  [FOUND] apps/web/app EXISTS! This is the problem!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Contents:" -ForegroundColor Gray
    Get-ChildItem -LiteralPath $appNoSrc -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($root.Length + 1)
        Write-Host "    - $rel" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [OK] apps/web/app does not exist" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# TEST 4: Check apps/web/pages
# ====================================================================
Write-Host "[TEST 4] Checking apps/web/pages..." -ForegroundColor Cyan
Write-Host ""

$pagesDir = "apps\web\pages"
if (Test-Path -LiteralPath $pagesDir) {
    Write-Host "  [FOUND] apps/web/pages EXISTS!" -ForegroundColor Red
    Get-ChildItem -LiteralPath $pagesDir -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($root.Length + 1)
        Write-Host "    - $rel" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [OK] apps/web/pages does not exist" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# TEST 5: Show current apps/web/src/app structure
# ====================================================================
Write-Host "[TEST 5] Current apps/web/src/app structure..." -ForegroundColor Cyan
Write-Host ""

$appSrcPath = "apps\web\src\app"
if (Test-Path -LiteralPath $appSrcPath) {
    Get-ChildItem -LiteralPath $appSrcPath -Recurse | ForEach-Object {
        $rel = $_.FullName.Substring($root.Length + 1)
        if ($_.PSIsContainer) {
            Write-Host "  [DIR]  $rel" -ForegroundColor Cyan
        } else {
            Write-Host "  [FILE] $rel" -ForegroundColor White
        }
    }
} else {
    Write-Host "  [NOT FOUND] $appSrcPath" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# TEST 6: Read next.config.js
# ====================================================================
Write-Host "[TEST 6] Reading next.config.js..." -ForegroundColor Cyan
Write-Host ""

$nextConfigPath = "apps\web\next.config.js"
if (Test-Path -LiteralPath $nextConfigPath) {
    $content = [System.IO.File]::ReadAllText((Join-Path $root $nextConfigPath))
    Write-Host "  Content:" -ForegroundColor Gray
    $content.Split("`n") | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  [NOT FOUND] $nextConfigPath" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# TEST 7: Read apps/web/package.json
# ====================================================================
Write-Host "[TEST 7] Reading apps/web/package.json..." -ForegroundColor Cyan
Write-Host ""

$webPackagePath = "apps\web\package.json"
if (Test-Path -LiteralPath $webPackagePath) {
    $content = [System.IO.File]::ReadAllText((Join-Path $root $webPackagePath))
    
    # Check for BOM
    if ($content.Length -gt 0 -and [int]$content[0] -eq 65279) {
        Write-Host "  [WARN] BOM detected!" -ForegroundColor Yellow
        $content = $content.Substring(1)
    }
    
    try {
        $pkg = $content | ConvertFrom-Json
        Write-Host "  name: $($pkg.name)" -ForegroundColor White
        Write-Host "  scripts.build: $($pkg.scripts.build)" -ForegroundColor White
        Write-Host "  next: $($pkg.dependencies.next)" -ForegroundColor White
        Write-Host "  react: $($pkg.dependencies.react)" -ForegroundColor White
        
        if ($pkg.PSObject.Properties.Name -contains 'experimental') {
            Write-Host "  [FOUND] experimental: $($pkg.experimental | ConvertTo-Json -Compress)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "  [ERROR] Failed to parse: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  [NOT FOUND] $webPackagePath" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# TEST 8: Check for .next cache
# ====================================================================
Write-Host "[TEST 8] Checking .next cache..." -ForegroundColor Cyan
Write-Host ""

$nextDir = "apps\web\.next"
if (Test-Path -LiteralPath $nextDir) {
    Write-Host "  [FOUND] .next exists!" -ForegroundColor Yellow
    $cacheFiles = Get-ChildItem -LiteralPath $nextDir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "*login*" -or $_.Name -like "*register*" }
    
    if ($cacheFiles.Count -gt 0) {
        Write-Host "  Cache files with 'login' or 'register':" -ForegroundColor Gray
        $cacheFiles | ForEach-Object {
            $rel = $_.FullName.Substring($root.Length + 1)
            Write-Host "    - $rel" -ForegroundColor White
        }
    } else {
        Write-Host "  No 'login' or 'register' in cache" -ForegroundColor Gray
    }
} else {
    Write-Host "  [OK] .next does not exist" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# TEST 9: Check for turbo cache
# ====================================================================
Write-Host "[TEST 9] Checking .turbo cache..." -ForegroundColor Cyan
Write-Host ""

$turboDir = ".turbo"
if (Test-Path -LiteralPath $turboDir) {
    Write-Host "  [FOUND] .turbo exists!" -ForegroundColor Yellow
    $turboFiles = Get-ChildItem -LiteralPath $turboDir -Recurse -File -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -like "*login*" -or $_.Name -like "*register*" }
    
    if ($turboFiles.Count -gt 0) {
        Write-Host "  Turbo cache files:" -ForegroundColor Gray
        $turboFiles | ForEach-Object {
            $rel = $_.FullName.Substring($root.Length + 1)
            Write-Host "    - $rel" -ForegroundColor White
        }
    }
} else {
    Write-Host "  [OK] .turbo does not exist" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# TEST 10: Check apps/admin for login/register
# ====================================================================
Write-Host "[TEST 10] Checking apps/admin for login/register..." -ForegroundColor Cyan
Write-Host ""

$adminLogin = Get-ChildItem -Path "apps\admin" -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like "*login*" -or $_.Name -like "*register*" }

if ($adminLogin.Count -gt 0) {
    Write-Host "  [FOUND] Login/Register files in apps/admin:" -ForegroundColor Yellow
    $adminLogin | ForEach-Object {
        $rel = $_.FullName.Substring($root.Length + 1)
        Write-Host "    - $rel" -ForegroundColor White
    }
} else {
    Write-Host "  [OK] No login/register in apps/admin" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# FINAL REPORT
# ====================================================================
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  DIAGNOSIS COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  Send the FULL output above for analysis." -ForegroundColor Yellow
Write-Host "  This will reveal exactly where Next.js is finding the ghost route." -ForegroundColor Yellow
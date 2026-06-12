$ErrorActionPreference = "Stop"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   BINARY SEARCH FOR BUILD ISSUE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# ====================================================================
# STEP 1: Backup (auth) folder
# ====================================================================
Write-Host "[STEP 1] Backing up (auth) folder..." -ForegroundColor Cyan

$authPath = "apps\web\src\app\(auth)"
$authBackup = "apps\web\src\app\(auth).backup"

if (Test-Path -LiteralPath $authBackup) {
    Remove-Item -LiteralPath $authBackup -Recurse -Force
}

Copy-Item -LiteralPath $authPath -Destination $authBackup -Recurse -Force
Write-Host "  [OK]   (auth) backed up to (auth).backup" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 2: Remove (auth) completely
# ====================================================================
Write-Host "[STEP 2] Removing (auth) folder..." -ForegroundColor Cyan

Remove-Item -LiteralPath $authPath -Recurse -Force
Write-Host "  [OK]   (auth) removed" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 3: Clear cache
# ====================================================================
Write-Host "[STEP 3] Clearing cache..." -ForegroundColor Cyan

if (Test-Path "apps\web\.next") {
    Remove-Item "apps\web\.next" -Recurse -Force
    Write-Host "  [OK]   .next cache cleared" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# STEP 4: Test build WITHOUT (auth)
# ====================================================================
Write-Host "[STEP 4] Building WITHOUT (auth)..." -ForegroundColor Cyan
Write-Host ""

$buildWithoutAuth = $false
try {
    pnpm build 2>&1 | ForEach-Object { Write-Host "  $_" }
    
    if ($LASTEXITCODE -eq 0) {
        $buildWithoutAuth = $true
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL WITHOUT (auth)!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  This PROVES the issue is in (auth) folder!" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "  BUILD FAILED EVEN WITHOUT (auth)!" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Issue is NOT in (auth) folder." -ForegroundColor Yellow
        Write-Host "  Need to check other files..." -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Build failed with exception" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 5: If build succeeded, restore (auth) and test files one by one
# ====================================================================
if ($buildWithoutAuth) {
    Write-Host "[STEP 5] Restoring (auth) and testing files one by one..." -ForegroundColor Cyan
    Write-Host ""
    
    # Restore (auth)
    Copy-Item -LiteralPath $authBackup -Destination $authPath -Recurse -Force
    Write-Host "  [RESTORED] (auth) folder" -ForegroundColor Yellow
    Write-Host ""
    
    # List all page.tsx files in (auth)
    $pageFiles = Get-ChildItem -LiteralPath $authPath -Recurse -Filter "page.tsx"
    
    Write-Host "  Testing each page.tsx file..." -ForegroundColor Gray
    Write-Host ""
    
    $problematicFiles = @()
    
    foreach ($pageFile in $pageFiles) {
        $relativePath = $pageFile.FullName.Replace("$PWD\", "")
        $tempBackup = "$($pageFile.FullName).temp"
        
        Write-Host "  Testing: $relativePath" -ForegroundColor White -NoNewline
        
        # Backup and remove this file
        Copy-Item -LiteralPath $pageFile.FullName -Destination $tempBackup -Force
        Remove-Item -LiteralPath $pageFile.FullName -Force
        
        # Clear cache
        if (Test-Path "apps\web\.next") {
            Remove-Item "apps\web\.next" -Recurse -Force
        }
        
        # Try build
        $buildSuccess = $false
        try {
            $output = pnpm build 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0) {
                $buildSuccess = $true
            }
        } catch {
            # Build failed
        }
        
        # Restore file
        Copy-Item -LiteralPath $tempBackup -Destination $pageFile.FullName -Force
        Remove-Item -LiteralPath $tempBackup -Force
        
        if ($buildSuccess) {
            Write-Host " [OK - file is GOOD]" -ForegroundColor Green
        } else {
            Write-Host " [FAIL - file is BAD]" -ForegroundColor Red
            $problematicFiles += $relativePath
        }
    }
    
    Write-Host ""
    
    if ($problematicFiles.Count -gt 0) {
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "  FOUND PROBLEMATIC FILES!" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "  These files cause build to fail:" -ForegroundColor Yellow
        $problematicFiles | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
        Write-Host ""
        Write-Host "  Next step: Check imports in these files" -ForegroundColor Cyan
    } else {
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host "  ALL FILES ARE GOOD!" -ForegroundColor Yellow
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Issue might be with combination of files" -ForegroundColor Yellow
        Write-Host "  Or with layout.tsx in (auth)" -ForegroundColor Yellow
    }
} else {
    Write-Host "[STEP 5] Issue is NOT in (auth). Checking other areas..." -ForegroundColor Cyan
    Write-Host ""
    
    # Restore (auth)
    Copy-Item -LiteralPath $authBackup -Destination $authPath -Recurse -Force
    Write-Host "  [RESTORED] (auth) folder" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "  Need to check:" -ForegroundColor Yellow
    Write-Host "  - Root layout.tsx" -ForegroundColor White
    Write-Host "  - Root page.tsx" -ForegroundColor White
    Write-Host "  - next.config.js" -ForegroundColor White
    Write-Host "  - tsconfig.json" -ForegroundColor White
    Write-Host "  - Other route groups" -ForegroundColor White
}

# ====================================================================
# STEP 6: Cleanup
# ====================================================================
Write-Host ""
Write-Host "[STEP 6] Cleanup..." -ForegroundColor Cyan

if (Test-Path -LiteralPath $authBackup) {
    Remove-Item -LiteralPath $authBackup -Recurse -Force
    Write-Host "  [OK]   Backup removed" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  BINARY SEARCH COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
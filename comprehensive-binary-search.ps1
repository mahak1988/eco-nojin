$ErrorActionPreference = "Stop"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   COMPREHENSIVE BINARY SEARCH" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# ====================================================================
# STEP 1: Test with ONLY root layout and page
# ====================================================================
Write-Host "[STEP 1] Testing with ONLY root files..." -ForegroundColor Cyan
Write-Host ""

$appPath = "apps\web\src\app"
$backupRoot = "apps\web\src\app.backup-root"

# Backup entire app folder
if (Test-Path $backupRoot) {
    Remove-Item $backupRoot -Recurse -Force
}
Copy-Item $appPath $backupRoot -Recurse -Force
Write-Host "  [BACKUP] app folder backed up" -ForegroundColor Green

# Remove everything except layout.tsx, page.tsx, globals.css
Get-ChildItem $appPath -Force | Where-Object { 
    $_.Name -notin @("layout.tsx", "page.tsx", "globals.css") 
} | ForEach-Object {
    if ($_.PSIsContainer) {
        Remove-Item $_.FullName -Recurse -Force
        Write-Host "  [DEL]  $($_.Name)/" -ForegroundColor Yellow
    } else {
        Remove-Item $_.FullName -Force
        Write-Host "  [DEL]  $($_.Name)" -ForegroundColor Yellow
    }
}

# Clear cache
if (Test-Path "apps\web\.next") {
    Remove-Item "apps\web\.next" -Recurse -Force
}

Write-Host ""
Write-Host "  Building with ONLY root files..." -ForegroundColor Gray
Write-Host ""

$buildSuccess = $false
try {
    $output = pnpm build 2>&1 | Out-String
    Write-Host $output
    
    if ($LASTEXITCODE -eq 0) {
        $buildSuccess = $true
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL WITH ONLY ROOT FILES!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Problem is in one of the subfolders/route groups" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  Build failed" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 2: If success, add route groups one by one
# ====================================================================
if ($buildSuccess) {
    Write-Host "[STEP 2] Adding route groups one by one..." -ForegroundColor Cyan
    Write-Host ""
    
    # Restore all folders
    Get-ChildItem $backupRoot -Directory | ForEach-Object {
        $destPath = Join-Path $appPath $_.Name
        if (-not (Test-Path -LiteralPath $destPath)) {
            Copy-Item $_.FullName $destPath -Recurse -Force
        }
    }
    
    # Get all route groups
    $routeGroups = Get-ChildItem $appPath -Directory | Where-Object { 
        $_.Name -notin @("layout.tsx", "page.tsx", "globals.css") -and $_.Name -match '^\(' 
    }
    
    Write-Host "  Found route groups:" -ForegroundColor Gray
    $routeGroups | ForEach-Object { Write-Host "    - $($_.Name)" -ForegroundColor White }
    Write-Host ""
    
    $problematicGroups = @()
    
    foreach ($group in $routeGroups) {
        Write-Host "  Testing with $($group.Name)..." -ForegroundColor White -NoNewline
        
        # Temporarily remove this group
        $tempBackup = "$($group.FullName).temp"
        Move-Item -LiteralPath $group.FullName -Destination $tempBackup -Force
        
        # Clear cache
        if (Test-Path "apps\web\.next") {
            Remove-Item "apps\web\.next" -Recurse -Force
        }
        
        # Try build
        $groupBuildSuccess = $false
        try {
            $null = pnpm build 2>&1 | Out-String
            if ($LASTEXITCODE -eq 0) {
                $groupBuildSuccess = $true
            }
        } catch {
            # Build failed
        }
        
        # Restore group
        Move-Item -LiteralPath $tempBackup -Destination $group.FullName -Force
        
        if ($groupBuildSuccess) {
            Write-Host " [OK - group is GOOD]" -ForegroundColor Green
        } else {
            Write-Host " [FAIL - group is BAD]" -ForegroundColor Red
            $problematicGroups += $group.Name
        }
    }
    
    Write-Host ""
    
    if ($problematicGroups.Count -gt 0) {
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "  FOUND PROBLEMATIC ROUTE GROUPS!" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "  These route groups cause build to fail:" -ForegroundColor Yellow
        $problematicGroups | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
        Write-Host ""
        Write-Host "  Next step: Check files in these groups" -ForegroundColor Cyan
    } else {
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host "  ALL ROUTE GROUPS ARE GOOD!" -ForegroundColor Yellow
        Write-Host "================================================================" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Issue might be with combination of groups" -ForegroundColor Yellow
    }
} else {
    Write-Host "[STEP 2] Build failed even with only root files!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Problem is in root files:" -ForegroundColor Yellow
    Write-Host "  - layout.tsx" -ForegroundColor White
    Write-Host "  - page.tsx" -ForegroundColor White
    Write-Host "  - globals.css" -ForegroundColor White
    Write-Host "  - OR tsconfig.json / next.config.js" -ForegroundColor White
}

# ====================================================================
# STEP 3: Restore everything
# ====================================================================
Write-Host ""
Write-Host "[STEP 3] Restoring everything..." -ForegroundColor Cyan

Remove-Item $appPath -Recurse -Force
Copy-Item $backupRoot $appPath -Recurse -Force
Remove-Item $backupRoot -Recurse -Force

Write-Host "  [OK]   All files restored" -ForegroundColor Green

# Clear cache
if (Test-Path "apps\web\.next") {
    Remove-Item "apps\web\.next" -Recurse -Force
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  BINARY SEARCH COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
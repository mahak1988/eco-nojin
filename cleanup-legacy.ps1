# ============================================================
# Legacy Cleanup Script - Phase 1 (FIXED VERSION)
# Project: econojin.com
# ============================================================

param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Legacy Files Cleanup - Phase 1" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# Legacy files to delete
$legacyFiles = @(
    @{ Path = ".\index.html"; Reason = "Duplicate - exists in apps/web/app/" },
    @{ Path = ".\ProductionGIS.tsx"; Reason = "Duplicate - exists in apps/web/src/components/gis/" },
    @{ Path = ".\Untitled-1.js"; Reason = "Temporary/test file - unused" },
    @{ Path = ".\api\test_client.html"; Reason = "Old test file" }
)

# Legacy directories to delete
$legacyDirs = @(
    @{ Path = ".\src"; Reason = "Duplicate of apps/web/src/ - contains App.tsx, components/, hooks/, store/" },
    @{ Path = ".\lib"; Reason = "Duplicate of apps/web/src/lib/ - contains api/client.ts, validation/" }
)

Write-Host "Checking for legacy files..." -ForegroundColor Cyan
Write-Host ""

$itemsToDelete = @()

# Check individual files
foreach ($file in $legacyFiles) {
    if (Test-Path $file.Path) {
        $size = (Get-Item $file.Path).Length
        $itemsToDelete += [PSCustomObject]@{
            Type = "File"
            Path = $file.Path
            Reason = $file.Reason
            Size = $size
            FileCount = 1
        }
        Write-Host "  [FILE] $($file.Path)" -ForegroundColor White -NoNewline
        Write-Host " ($([math]::Round($size/1KB, 2)) KB)" -ForegroundColor Gray
        Write-Host "         Reason: $($file.Reason)" -ForegroundColor DarkGray
    } else {
        Write-Host "  [SKIP] $($file.Path) (not found)" -ForegroundColor DarkYellow
    }
}

Write-Host ""

# Check directories
foreach ($dir in $legacyDirs) {
    if (Test-Path $dir.Path) {
        $fileCount = (Get-ChildItem $dir.Path -Recurse -File | Measure-Object).Count
        $totalSize = (Get-ChildItem $dir.Path -Recurse -File | Measure-Object -Property Length -Sum).Sum
        $itemsToDelete += [PSCustomObject]@{
            Type = "Directory"
            Path = $dir.Path
            Reason = $dir.Reason
            FileCount = $fileCount
            Size = $totalSize
        }
        Write-Host "  [DIR] $($dir.Path)/" -ForegroundColor White -NoNewline
        Write-Host " ($fileCount files, $([math]::Round($totalSize/1KB, 2)) KB)" -ForegroundColor Gray
        Write-Host "         Reason: $($dir.Reason)" -ForegroundColor DarkGray
    } else {
        Write-Host "  [SKIP] $($dir.Path)/ (not found)" -ForegroundColor DarkYellow
    }
}

Write-Host ""

if ($itemsToDelete.Count -eq 0) {
    Write-Host "No legacy files found. Project is clean!" -ForegroundColor Green
    exit 0
}

# Calculate totals using simple loop
$totalSize = 0
$totalFiles = 0
foreach ($item in $itemsToDelete) {
    $totalSize += $item.Size
    $totalFiles += $item.FileCount
}

Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "                     SUMMARY" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "  Items to delete:  $($itemsToDelete.Count)" -ForegroundColor White
Write-Host "  Total files:      $totalFiles" -ForegroundColor White
Write-Host "  Total size:       $([math]::Round($totalSize/1KB, 2)) KB" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

if (-not $Force) {
    Write-Host "This will move files to Windows Recycle Bin." -ForegroundColor Yellow
    Write-Host "Are you sure? (y/N): " -ForegroundColor Yellow -NoNewline
    $confirm = Read-Host
    if ($confirm -ne 'y' -and $confirm -ne 'Y') {
        Write-Host "Operation cancelled." -ForegroundColor Cyan
        exit 0
    }
}

# Create backup
$backupDir = ".\_QUARANTINE\legacy_cleanup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Write-Host "Creating backup in: $backupDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

# Function to send to Recycle Bin
function Send-ToRecycleBin {
    param([string]$Path)
    
    try {
        $fullPath = (Resolve-Path $Path).Path
        $shell = New-Object -ComObject Shell.Application
        $folder = $shell.Namespace((Split-Path $fullPath -Parent))
        $item = $folder.ParseName((Split-Path $fullPath -Leaf))
        $item.InvokeVerb("delete")
        Start-Sleep -Milliseconds 500
        
        if (-not (Test-Path $fullPath)) {
            return $true
        } else {
            return $false
        }
    } catch {
        return $false
    }
}

# Execute deletion
$logFile = "$backupDir\cleanup-log.txt"
$logContent = "Legacy Cleanup Log - Phase 1`n"
$logContent += "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n"
$logContent += "Project: $projectRoot`n"
$logContent += "==================================================`n`n"

$successCount = 0
$failCount = 0

foreach ($item in $itemsToDelete) {
    Write-Host ""
    Write-Host "Processing: $($item.Path)" -ForegroundColor Cyan
    
    # Backup
    try {
        $backupPath = Join-Path $backupDir (Split-Path $item.Path -Leaf)
        if ($item.Type -eq "Directory") {
            Copy-Item -Path $item.Path -Destination $backupPath -Recurse -Force
        } else {
            Copy-Item -Path $item.Path -Destination $backupPath -Force
        }
        Write-Host "  Backup created: $backupPath" -ForegroundColor Green
    } catch {
        Write-Host "  Backup failed: $_" -ForegroundColor Red
    }
    
    # Send to Recycle Bin
    try {
        $result = Send-ToRecycleBin -Path $item.Path
        if ($result) {
            Write-Host "  Moved to Recycle Bin: $($item.Path)" -ForegroundColor Green
            $logContent += "[OK] $($item.Path) - $($item.Reason)`n"
            $successCount++
            
            # Remove parent if empty
            $parentDir = Split-Path $item.Path -Parent
            if ($parentDir -ne "." -and (Test-Path $parentDir)) {
                $remaining = Get-ChildItem $parentDir -ErrorAction SilentlyContinue
                if ($null -eq $remaining -or $remaining.Count -eq 0) {
                    Remove-Item $parentDir -Force
                    Write-Host "  Empty parent removed: $parentDir" -ForegroundColor Cyan
                }
            }
        } else {
            Write-Host "  Failed to move: $($item.Path)" -ForegroundColor Red
            $logContent += "[FAIL] $($item.Path)`n"
            $failCount++
        }
    } catch {
        Write-Host "  Error: $_" -ForegroundColor Red
        $logContent += "[ERROR] $($item.Path) - $_`n"
        $failCount++
    }
}

# Save log
$logContent += "`n==================================================`n"
$logContent += "Summary: Success=$successCount, Failed=$failCount`n"
$logContent | Out-File -FilePath $logFile -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  FINAL REPORT" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Success:     $successCount" -ForegroundColor White
Write-Host "  Failed:      $failCount" -ForegroundColor White
Write-Host "  Backup:      $backupDir" -ForegroundColor White
Write-Host "  Log:         $logFile" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""

if ($failCount -eq 0) {
    Write-Host "Phase 1 completed successfully!" -ForegroundColor Green
    Write-Host "Next step: Phase 2 (Create standard packages structure)" -ForegroundColor Cyan
} else {
    Write-Host "$failCount items failed. Check the log." -ForegroundColor Yellow
}
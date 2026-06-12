$ErrorActionPreference = "Stop"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   COMPREHENSIVE BUILD DIAGNOSIS AND FIX" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# ====================================================================
# STEP 1: Clear all caches
# ====================================================================
Write-Host "[STEP 1] Clearing all caches..." -ForegroundColor Cyan

$cacheDirs = @(
    "apps\web\.next",
    "apps\web\.turbo",
    "apps\admin\.next",
    "apps\library\.next",
    "node_modules\.cache"
)

foreach ($dir in $cacheDirs) {
    if (Test-Path -LiteralPath $dir) {
        Remove-Item -LiteralPath $dir -Recurse -Force
        Write-Host "  [DEL]  $dir" -ForegroundColor Green
    }
}
Write-Host ""

# ====================================================================
# STEP 2: Check tsconfig.json paths
# ====================================================================
Write-Host "[STEP 2] Checking tsconfig.json path aliases..." -ForegroundColor Cyan

$tsconfigPath = "apps\web\tsconfig.json"
if (Test-Path $tsconfigPath) {
    $tsconfig = Get-Content $tsconfigPath -Raw
    Write-Host "  [OK]   tsconfig.json exists" -ForegroundColor Green
    
    if ($tsconfig -match '"@/\*"') {
        Write-Host "  [OK]   @/ alias is defined" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] @/ alias NOT found!" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "  Content:" -ForegroundColor Gray
    Get-Content $tsconfigPath | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
} else {
    Write-Host "  [ERR]  tsconfig.json NOT FOUND!" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# STEP 3: Verify critical files
# ====================================================================
Write-Host "[STEP 3] Verifying critical files..." -ForegroundColor Cyan

$criticalFiles = @{
    "Root Layout" = "apps\web\src\app\layout.tsx"
    "Root Page" = "apps\web\src\app\page.tsx"
    "Globals CSS" = "apps\web\src\app\globals.css"
    "Auth Layout" = "apps\web\src\app\(auth)\layout.tsx"
    "Login Page" = "apps\web\src\app\(auth)\login\page.tsx"
    "next.config" = "apps\web\next.config.js"
    "package.json" = "apps\web\package.json"
}

foreach ($name in $criticalFiles.Keys) {
    $path = $criticalFiles[$name]
    if (Test-Path -LiteralPath $path) {
        $size = (Get-Item -LiteralPath $path).Length
        Write-Host "  [OK]   $name : $path ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  [MISS] $name : $path" -ForegroundColor Red
    }
}
Write-Host ""

# ====================================================================
# STEP 4: Show root layout.tsx content
# ====================================================================
Write-Host "[STEP 4] Root layout.tsx content:" -ForegroundColor Cyan
Write-Host ""

$rootLayoutPath = "apps\web\src\app\layout.tsx"
if (Test-Path $rootLayoutPath) {
    $content = Get-Content $rootLayoutPath -Raw
    
    # Check for BOM
    $bytes = [System.IO.File]::ReadAllBytes("$PWD\$rootLayoutPath")
    if ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "  [WARN] UTF-8 BOM detected! This can cause issues." -ForegroundColor Yellow
        Write-Host "  [FIX]  Removing BOM..." -ForegroundColor Yellow
        $utf8NoBom = New-Object System.Text.UTF8Encoding $false
        [System.IO.File]::WriteAllText("$PWD\$rootLayoutPath", $content, $utf8NoBom)
        Write-Host "  [OK]   BOM removed" -ForegroundColor Green
    }
    
    Write-Host "  File content:" -ForegroundColor Gray
    Get-Content $rootLayoutPath | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  [ERR]  File not found!" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# STEP 5: Recreate root layout.tsx (clean, no BOM, minimal)
# ====================================================================
Write-Host "[STEP 5] Recreating root layout.tsx (clean version)..." -ForegroundColor Cyan

$backupPath = "$rootLayoutPath.backup-$(Get-Date -Format 'yyyyMMddHHmmss')"
if (Test-Path $rootLayoutPath) {
    Copy-Item $rootLayoutPath $backupPath -Force
    Write-Host "  [BACKUP] $backupPath" -ForegroundColor Yellow
}

$cleanLayout = @"
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Econojin',
  description: 'Econojin Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
"@

# Write without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$PWD\$rootLayoutPath", $cleanLayout, $utf8NoBom)

Write-Host "  [OK]   Clean layout.tsx created (no BOM)" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 6: Check (auth) folder structure
# ====================================================================
Write-Host "[STEP 6] Checking (auth) folder structure..." -ForegroundColor Cyan

$authPath = "apps\web\src\app\(auth)"
if (Test-Path -LiteralPath $authPath) {
    Write-Host "  Contents of (auth):" -ForegroundColor Gray
    Get-ChildItem -LiteralPath $authPath -Recurse | ForEach-Object {
        $rel = $_.FullName.Replace("$PWD\$authPath\", "")
        if ($_.PSIsContainer) {
            Write-Host "    [DIR]  $rel" -ForegroundColor Cyan
        } else {
            Write-Host "    [FILE] $rel" -ForegroundColor White
        }
    }
    
    # Check for any leftover 'auth' subfolder
    $doubleAuthPath = "apps\web\src\app\(auth)\auth"
    if (Test-Path -LiteralPath $doubleAuthPath) {
        Write-Host ""
        Write-Host "  [WARN] Double 'auth' folder detected!" -ForegroundColor Yellow
        Write-Host "  [FIX]  Removing..." -ForegroundColor Yellow
        Remove-Item -LiteralPath $doubleAuthPath -Recurse -Force
        Write-Host "  [OK]   Removed" -ForegroundColor Green
    }
} else {
    Write-Host "  [ERR]  (auth) folder NOT FOUND!" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# STEP 7: Check (auth)/layout.tsx
# ====================================================================
Write-Host "[STEP 7] Checking (auth)/layout.tsx..." -ForegroundColor Cyan

$authLayoutPath = "apps\web\src\app\(auth)\layout.tsx"
if (Test-Path -LiteralPath $authLayoutPath) {
    Write-Host "  [OK]   (auth)/layout.tsx exists" -ForegroundColor Green
    Write-Host "  Content:" -ForegroundColor Gray
    Get-Content -LiteralPath $authLayoutPath | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  [MISS] (auth)/layout.tsx not found - creating..." -ForegroundColor Yellow
    
    $authLayout = @"
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}
"@
    
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText("$PWD\$authLayoutPath", $authLayout, $utf8NoBom)
    Write-Host "  [OK]   Created minimal (auth)/layout.tsx" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# STEP 8: Verify all page.tsx files in (auth) are valid
# ====================================================================
Write-Host "[STEP 8] Verifying page.tsx files in (auth)..." -ForegroundColor Cyan

$pageFiles = Get-ChildItem -LiteralPath $authPath -Recurse -Filter "page.tsx"
foreach ($page in $pageFiles) {
    $relPath = $page.FullName.Replace("$PWD\", "")
    $content = Get-Content -LiteralPath $page.FullName -Raw
    
    # Check for 'use client' or 'export default'
    if ($content -match 'export default') {
        Write-Host "  [OK]   $relPath (has export default)" -ForegroundColor Green
    } else {
        Write-Host "  [ERR]  $relPath (MISSING export default!)" -ForegroundColor Red
    }
}
Write-Host ""

# ====================================================================
# STEP 9: Check for stale register references
# ====================================================================
Write-Host "[STEP 9] Checking for stale 'register' references..." -ForegroundColor Cyan

$registerPath = "apps\web\src\app\(auth)\register"
if (Test-Path -LiteralPath $registerPath) {
    Write-Host "  [FOUND] register folder exists" -ForegroundColor Yellow
} else {
    Write-Host "  [OK]   No register folder (as expected)" -ForegroundColor Green
}

# Check .next cache for stale references
$nextCachePath = "apps\web\.next"
if (Test-Path -LiteralPath $nextCachePath) {
    Write-Host "  [WARN] .next cache still exists (should be deleted)" -ForegroundColor Yellow
} else {
    Write-Host "  [OK]   .next cache cleared" -ForegroundColor Green
}
Write-Host ""

# ====================================================================
# STEP 10: Try build
# ====================================================================
Write-Host "[STEP 10] Attempting build..." -ForegroundColor Cyan
Write-Host ""

try {
    pnpm build
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED - See error above" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Next diagnostic step:" -ForegroundColor Yellow
    Write-Host "  Try temporarily moving (auth) folder out and rebuild:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Move-Item -LiteralPath 'apps\web\src\app\(auth)' -Destination 'apps\web\src\app\(auth).disabled'" -ForegroundColor Gray
    Write-Host "  pnpm build" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  DIAGNOSIS COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
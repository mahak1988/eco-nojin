# ============================================================
# Fix Build Errors - Phase 7
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Fix Build Errors - Phase 7" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Check root package.json validity
# ============================================================
Write-Host "[Step 1/6] Checking root package.json..." -ForegroundColor Cyan
Write-Host ""

$rootPackagePath = "package.json"

if (Test-Path $rootPackagePath) {
    $content = Get-Content $rootPackagePath -Raw
    
    # Check for BOM (Byte Order Mark) which causes JSON parse errors
    if ($content.Length -gt 0 -and [int]$content[0] -eq 65279) {
        Write-Host "  [WARN] UTF-8 BOM detected! Removing..." -ForegroundColor Yellow
        $content = $content.Substring(1)
        [System.IO.File]::WriteAllText("$PWD\package.json", $content, [System.Text.UTF8Encoding]::new($false))
        Write-Host "  [OK]   BOM removed" -ForegroundColor Green
    }
    
    # Try to parse
    try {
        $null = $content | ConvertFrom-Json
        Write-Host "  [OK]   package.json is valid JSON" -ForegroundColor Green
    } catch {
        Write-Host "  [ERR]  Invalid JSON: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "  First 200 chars of file:" -ForegroundColor Gray
        Write-Host $content.Substring(0, [Math]::Min(200, $content.Length)) -ForegroundColor DarkGray
    }
} else {
    Write-Host "  [ERR]  package.json not found!" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# Step 2: Check apps structure for layout.tsx
# ============================================================
Write-Host "[Step 2/6] Checking layouts..." -ForegroundColor Cyan
Write-Host ""

$rootLayout = "apps\web\src\app\layout.tsx"
if (Test-Path $rootLayout) {
    Write-Host "  [OK]   Root layout exists: $rootLayout" -ForegroundColor Green
} else {
    Write-Host "  [ERR]  Root layout MISSING: $rootLayout" -ForegroundColor Red
}

$authLayout = "apps\web\src\app\(auth)\layout.tsx"
if (Test-Path $authLayout) {
    Write-Host "  [OK]   Auth layout exists: $authLayout" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Auth layout missing: $authLayout" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 3: Fix double auth in route (auth)/auth/login -> (auth)/login
# ============================================================
Write-Host "[Step 3/6] Fixing double 'auth' in route..." -ForegroundColor Cyan
Write-Host ""

$doubleAuthPath = "apps\web\src\app\(auth)\auth"
$authGroupPath = "apps\web\src\app\(auth)"

if (Test-Path $doubleAuthPath) {
    Write-Host "  [FOUND] Double auth structure detected:" -ForegroundColor Yellow
    Get-ChildItem -Path $doubleAuthPath -Recurse | ForEach-Object {
        Write-Host "    - $($_.FullName)" -ForegroundColor Gray
    }
    Write-Host ""
    
    # Move contents up one level
    $items = Get-ChildItem -Path $doubleAuthPath -Force
    
    foreach ($item in $items) {
        $destPath = Join-Path $authGroupPath $item.Name
        
        if (Test-Path $destPath) {
            Write-Host "  [SKIP] $($item.Name) (already exists at destination)" -ForegroundColor Yellow
            continue
        }
        
        try {
            git mv $item.FullName $destPath 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [OK]   Moved: $($item.Name)" -ForegroundColor Green
            } else {
                Move-Item -Path $item.FullName -Destination $destPath -Force
                Write-Host "  [OK]   Moved: $($item.Name) (fallback)" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [ERR]  Failed: $($item.Name) - $_" -ForegroundColor Red
        }
    }
    
    # Remove empty double-auth folder
    $remaining = Get-ChildItem -Path $doubleAuthPath -Force -ErrorAction SilentlyContinue
    if ($null -eq $remaining -or $remaining.Count -eq 0) {
        Remove-Item -Path $doubleAuthPath -Force -Recurse
        Write-Host "  [DEL]  Removed empty double-auth folder" -ForegroundColor Gray
    }
} else {
    Write-Host "  [OK]   No double auth structure found" -ForegroundColor Green
}

Write-Host ""

# ============================================================
# Step 4: Create auth layout if missing
# ============================================================
Write-Host "[Step 4/6] Creating (auth)/layout.tsx if missing..." -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $authLayout)) {
    $authLayoutContent = @(
        'export default function AuthLayout({'
        '  children,'
        '}: {'
        '  children: React.ReactNode'
        '}) {'
        '  return ('
        '    <div className="min-h-screen flex items-center justify-center bg-gray-50">'
        '      <div className="w-full max-w-md px-4">'
        '        {children}'
        '      </div>'
        '    </div>'
        '  )'
        '}'
    )
    
    $authLayoutContent -join "`n" | Out-File -FilePath $authLayout -Encoding UTF8 -NoNewline
    Write-Host "  [CREATED] $authLayout" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] Auth layout already exists" -ForegroundColor DarkGray
}

Write-Host ""

# ============================================================
# Step 5: Check and fix all route group layouts
# ============================================================
Write-Host "[Step 5/6] Checking all route group layouts..." -ForegroundColor Cyan
Write-Host ""

$routeGroups = @("(auth)", "(admin)", "(dashboard)", "(marketing)", "(modules)")

foreach ($group in $routeGroups) {
    $groupPath = "apps\web\src\app\$group"
    $layoutPath = Join-Path $groupPath "layout.tsx"
    
    if (Test-Path $groupPath) {
        if (Test-Path $layoutPath) {
            Write-Host "  [OK]   $group has layout" -ForegroundColor Green
        } else {
            Write-Host "  [WARN] $group missing layout - will use root layout" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# ============================================================
# Step 6: Verify and summarize
# ============================================================
Write-Host "[Step 6/6] Final verification..." -ForegroundColor Cyan
Write-Host ""

Write-Host "Structure of apps/web/src/app:" -ForegroundColor White
Get-ChildItem -Path "apps\web\src\app" -Force | ForEach-Object {
    if ($_.PSIsContainer) {
        Write-Host "  [DIR]  $($_.Name)/" -ForegroundColor Cyan
    } else {
        Write-Host "  [FILE] $($_.Name)" -ForegroundColor White
    }
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  BUILD FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git status" -ForegroundColor White
Write-Host "  2. git add -A" -ForegroundColor White
Write-Host "  3. git commit -m 'fix: resolve build errors and auth route structure'" -ForegroundColor White
Write-Host "  4. pnpm build (to verify)" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
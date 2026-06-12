# ============================================================
# Fix Final Build Issues v2 - Phase 8
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Fix Final Build Issues v2 - Phase 8" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Check root layout.tsx content
# ============================================================
Write-Host "[Step 1/5] Checking root layout.tsx..." -ForegroundColor Cyan
Write-Host ""

$rootLayoutPath = "apps\web\src\app\layout.tsx"

if (Test-Path $rootLayoutPath) {
    $content = Get-Content $rootLayoutPath -Raw
    
    Write-Host "  [OK]   Root layout exists ($($content.Length) chars)" -ForegroundColor Green
    
    # Check if it has proper export default
    if ($content -match 'export default function RootLayout') {
        Write-Host "  [OK]   Has 'export default function RootLayout'" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Missing 'export default function RootLayout'" -ForegroundColor Yellow
    }
    
    # Check if it returns html/body
    if ($content -match '<html' -and $content -match '<body') {
        Write-Host "  [OK]   Returns <html> and <body>" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] Missing <html> or <body> tags" -ForegroundColor Yellow
    }
    
    # Show full content
    Write-Host ""
    Write-Host "  Full content:" -ForegroundColor Gray
    $lines = Get-Content $rootLayoutPath
    $lines | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
} else {
    Write-Host "  [ERR]  Root layout NOT FOUND!" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# Step 2: Fix [locale]/layout.tsx using -LiteralPath
# ============================================================
Write-Host "[Step 2/5] Creating [locale]/layout.tsx..." -ForegroundColor Cyan
Write-Host ""

$localePath = "apps\web\src\app\[locale]"
$localeLayoutPath = "apps\web\src\app\[locale]\layout.tsx"

if (Test-Path -LiteralPath $localePath) {
    Write-Host "  [OK]   [locale] folder exists" -ForegroundColor Green
    
    if (Test-Path -LiteralPath $localeLayoutPath) {
        Write-Host "  [OK]   [locale]/layout.tsx already exists" -ForegroundColor Green
    } else {
        Write-Host "  [CREATING] [locale]/layout.tsx..." -ForegroundColor Yellow
        
        $localeLayoutContent = @(
            'export default function LocaleLayout({'
            '  children,'
            '  params,'
            '}: {'
            '  children: React.ReactNode;'
            '  params: { locale: string };'
            '}) {'
            '  return ('
            '    <div dir={params.locale === "fa" ? "rtl" : "ltr"}>'
            '      {children}'
            '    </div>'
            '  );'
            '}'
        )
        
        # Use -LiteralPath to avoid wildcard interpretation
        $localeLayoutContent -join "`n" | Out-File -LiteralPath $localeLayoutPath -Encoding UTF8 -NoNewline
        
        if (Test-Path -LiteralPath $localeLayoutPath) {
            Write-Host "  [OK]   [locale]/layout.tsx created successfully" -ForegroundColor Green
        } else {
            Write-Host "  [ERR]  Failed to create [locale]/layout.tsx" -ForegroundColor Red
        }
    }
} else {
    Write-Host "  [INFO] [locale] folder not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 3: Check next.config.js
# ============================================================
Write-Host "[Step 3/5] Checking next.config.js..." -ForegroundColor Cyan
Write-Host ""

$nextConfigPath = "apps\web\next.config.js"

if (Test-Path $nextConfigPath) {
    $content = Get-Content $nextConfigPath -Raw
    Write-Host "  [OK]   next.config.js exists" -ForegroundColor Green
    
    # Show content
    Write-Host "  Content:" -ForegroundColor Gray
    $lines = Get-Content $nextConfigPath
    $lines | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
} else {
    Write-Host "  [WARN] next.config.js not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 4: Verify (auth) structure
# ============================================================
Write-Host "[Step 4/5] Verifying (auth) structure..." -ForegroundColor Cyan
Write-Host ""

$authPath = "apps\web\src\app\(auth)"

if (Test-Path -LiteralPath $authPath) {
    Write-Host "  [OK]   (auth) folder exists" -ForegroundColor Green
    
    # List contents
    $items = Get-ChildItem -LiteralPath $authPath -Force
    foreach ($item in $items) {
        if ($item.PSIsContainer) {
            Write-Host "    [DIR]  $($item.Name)/" -ForegroundColor Cyan
        } else {
            Write-Host "    [FILE] $($item.Name)" -ForegroundColor White
        }
    }
    
    # Check for layout.tsx
    $authLayoutPath = "apps\web\src\app\(auth)\layout.tsx"
    if (Test-Path -LiteralPath $authLayoutPath) {
        Write-Host "  [OK]   (auth)/layout.tsx exists" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] (auth)/layout.tsx missing" -ForegroundColor Yellow
    }
    
    # Check for login/page.tsx
    $loginPagePath = "apps\web\src\app\(auth)\login\page.tsx"
    if (Test-Path -LiteralPath $loginPagePath) {
        Write-Host "  [OK]   (auth)/login/page.tsx exists" -ForegroundColor Green
    } else {
        Write-Host "  [ERR]  (auth)/login/page.tsx NOT FOUND" -ForegroundColor Red
    }
} else {
    Write-Host "  [ERR]  (auth) folder NOT FOUND" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# Step 5: Final structure report
# ============================================================
Write-Host "[Step 5/5] Final app structure..." -ForegroundColor Cyan
Write-Host ""

Write-Host "apps/web/src/app/ structure:" -ForegroundColor White
Get-ChildItem -Path "apps\web\src\app" -Force | ForEach-Object {
    if ($_.PSIsContainer) {
        $itemCount = (Get-ChildItem -LiteralPath $_.FullName -Recurse -File | Measure-Object).Count
        Write-Host "  [DIR]  $($_.Name)/ ($itemCount files)" -ForegroundColor Cyan
    } else {
        Write-Host "  [FILE] $($_.Name)" -ForegroundColor White
    }
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  FINAL FIX v2 COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git add -A" -ForegroundColor White
Write-Host "  2. git commit -m 'fix: create [locale]/layout.tsx for i18n'" -ForegroundColor White
Write-Host "  3. pnpm build" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
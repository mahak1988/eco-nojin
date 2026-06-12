# ============================================================
# Fix Final Build Issues - Phase 8
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Fix Final Build Issues - Phase 8" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Check and fix root layout.tsx
# ============================================================
Write-Host "[Step 1/5] Checking root layout.tsx..." -ForegroundColor Cyan
Write-Host ""

$rootLayoutPath = "apps\web\src\app\layout.tsx"

if (Test-Path $rootLayoutPath) {
    $content = Get-Content $rootLayoutPath -Raw
    
    # Check if file is empty or has minimal content
    if ($content.Length -lt 50) {
        Write-Host "  [WARN] Root layout is too short, recreating..." -ForegroundColor Yellow
        
        $newLayoutContent = @(
            'import { Inter } from "next/font/google";'
            'import "./globals.css";'
            ''
            'const inter = Inter({ subsets: ["latin"] });'
            ''
            'export const metadata = {'
            '  title: "Econojin",'
            '  description: "Econojin Monorepo Application",'
            '};'
            ''
            'export default function RootLayout({'
            '  children,'
            '}: {'
            '  children: React.ReactNode;'
            '}) {'
            '  return ('
            '    <html lang="fa" dir="rtl">'
            '      <body className={inter.className}>{children}</body>'
            '    </html>'
            '  );'
            '}'
        )
        
        $newLayoutContent -join "`n" | Out-File -FilePath $rootLayoutPath -Encoding UTF8 -NoNewline
        Write-Host "  [OK]   Root layout recreated" -ForegroundColor Green
    } else {
        Write-Host "  [OK]   Root layout exists and has content ($($content.Length) chars)" -ForegroundColor Green
        
        # Show first 10 lines
        $lines = Get-Content $rootLayoutPath -TotalCount 10
        Write-Host "  First 10 lines:" -ForegroundColor Gray
        $lines | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
    }
} else {
    Write-Host "  [ERR]  Root layout NOT FOUND!" -ForegroundColor Red
    Write-Host "  Creating new root layout..." -ForegroundColor Yellow
    
    $newLayoutContent = @(
        'import { Inter } from "next/font/google";'
        'import "./globals.css";'
        ''
        'const inter = Inter({ subsets: ["latin"] });'
        ''
        'export const metadata = {'
        '  title: "Econojin",'
        '  description: "Econojin Monorepo Application",'
        '};'
        ''
        'export default function RootLayout({'
        '  children,'
        '}: {'
        '  children: React.ReactNode;'
        '}) {'
        '  return ('
        '    <html lang="fa" dir="rtl">'
        '      <body className={inter.className}>{children}</body>'
        '    </html>'
        '  );'
        '}'
    )
    
    $newLayoutContent -join "`n" | Out-File -FilePath $rootLayoutPath -Encoding UTF8 -NoNewline
    Write-Host "  [CREATED] Root layout created" -ForegroundColor Green
}

Write-Host ""

# ============================================================
# Step 2: Check [locale] folder (for i18n)
# ============================================================
Write-Host "[Step 2/5] Checking [locale] folder for i18n..." -ForegroundColor Cyan
Write-Host ""

$localePath = "apps\web\src\app\[locale]"

if (Test-Path -LiteralPath $localePath) {
    Write-Host "  [OK]   [locale] folder exists" -ForegroundColor Green
    
    $localeFiles = Get-ChildItem -LiteralPath $localePath -Recurse -File
    Write-Host "  [INFO] Found $($localeFiles.Count) files in [locale]" -ForegroundColor Cyan
    
    # Check if [locale] has layout.tsx
    $localeLayoutPath = Join-Path $localePath "layout.tsx"
    if (Test-Path -LiteralPath $localeLayoutPath) {
        Write-Host "  [OK]   [locale]/layout.tsx exists" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] [locale]/layout.tsx missing - creating..." -ForegroundColor Yellow
        
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
        
        $localeLayoutContent -join "`n" | Out-File -FilePath $localeLayoutPath -Encoding UTF8 -NoNewline
        Write-Host "  [CREATED] [locale]/layout.tsx" -ForegroundColor Green
    }
} else {
    Write-Host "  [INFO] [locale] folder not found" -ForegroundColor Yellow
    Write-Host "  Skipping i18n setup (can be added later)" -ForegroundColor Gray
}

Write-Host ""

# ============================================================
# Step 3: Verify next.config.js
# ============================================================
Write-Host "[Step 3/5] Checking next.config.js..." -ForegroundColor Cyan
Write-Host ""

$nextConfigPath = "apps\web\next.config.js"

if (Test-Path $nextConfigPath) {
    $content = Get-Content $nextConfigPath -Raw
    Write-Host "  [OK]   next.config.js exists" -ForegroundColor Green
    
    # Check for i18n config
    if ($content -match 'i18n') {
        Write-Host "  [OK]   i18n configuration found" -ForegroundColor Green
    } else {
        Write-Host "  [INFO] No i18n configuration (can be added later)" -ForegroundColor Gray
    }
} else {
    Write-Host "  [WARN] next.config.js not found" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================
# Step 4: Check all route groups have proper structure
# ============================================================
Write-Host "[Step 4/5] Verifying route group structures..." -ForegroundColor Cyan
Write-Host ""

$routeGroups = @("(admin)", "(auth)", "(dashboard)", "(marketing)", "(modules)")

foreach ($group in $routeGroups) {
    $groupPath = "apps\web\src\app\$group"
    
    if (Test-Path -LiteralPath $groupPath) {
        $pageCount = (Get-ChildItem -LiteralPath $groupPath -Recurse -Filter "page.tsx" | Measure-Object).Count
        Write-Host "  [OK]   $group - $pageCount pages" -ForegroundColor Green
    } else {
        Write-Host "  [SKIP] $group not found" -ForegroundColor DarkGray
    }
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
Write-Host "                  FINAL FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git status" -ForegroundColor White
Write-Host "  2. git add -A" -ForegroundColor White
Write-Host "  3. git commit -m 'fix: ensure root layout and i18n structure'" -ForegroundColor White
Write-Host "  4. pnpm build" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
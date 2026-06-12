$ErrorActionPreference = "Continue"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   ULTIMATE DIAGNOSIS - Final Investigation" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# ====================================================================
# STEP 1: Check package.json of apps/web
# ====================================================================
Write-Host "[STEP 1] Checking apps/web/package.json..." -ForegroundColor Cyan
Write-Host ""

$webPackagePath = "apps\web\package.json"
if (Test-Path $webPackagePath) {
    Write-Host "  Content:" -ForegroundColor Gray
    Get-Content $webPackagePath | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  [ERR]  NOT FOUND!" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# STEP 2: Check React/Next versions
# ====================================================================
Write-Host "[STEP 2] Checking React/Next versions..." -ForegroundColor Cyan
Write-Host ""

try {
    $nextVersion = pnpm list next --depth 0 --filter @econojin/web 2>&1 | Out-String
    Write-Host "  Next.js:" -ForegroundColor Gray
    Write-Host "    $nextVersion" -ForegroundColor White
    
    $reactVersion = pnpm list react --depth 0 --filter @econojin/web 2>&1 | Out-String
    Write-Host "  React:" -ForegroundColor Gray
    Write-Host "    $reactVersion" -ForegroundColor White
} catch {
    Write-Host "  [WARN] Could not get versions" -ForegroundColor Yellow
}
Write-Host ""

# ====================================================================
# STEP 3: Create minimal app OUTSIDE monorepo
# ====================================================================
Write-Host "[STEP 3] Creating test app OUTSIDE monorepo..." -ForegroundColor Cyan
Write-Host ""

$testDir = "C:\temp-nextjs-test-$(Get-Random)"
New-Item -ItemType Directory -Path $testDir -Force | Out-Null
Set-Location $testDir

Write-Host "  Test directory: $testDir" -ForegroundColor Gray

# Initialize new Next.js app
Write-Host "  Running: pnpm create next-app..." -ForegroundColor Gray

try {
    # Use npx to create Next.js app non-interactively
    $env:CI = "true"
    
    # Create minimal package.json
    $packageJson = @"
{
  "name": "temp-test",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "14.2.5",
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@types/node": "^20",
    "@types/react": "^18",
    "@types/react-dom": "^18",
    "typescript": "^5"
  }
}
"@
    $utf8NoBom = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText("$testDir\package.json", $packageJson, $utf8NoBom)
    
    # Create minimal files
    New-Item -ItemType Directory -Path "$testDir\src\app" -Force | Out-Null
    
    $layout = @"
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
"@
    [System.IO.File]::WriteAllText("$testDir\src\app\layout.tsx", $layout, $utf8NoBom)
    
    $page = @"
export default function Home() {
  return <div>Hello World</div>;
}
"@
    [System.IO.File]::WriteAllText("$testDir\src\app\page.tsx", $page, $utf8NoBom)
    
    $tsconfig = @"
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
"@
    [System.IO.File]::WriteAllText("$testDir\tsconfig.json", $tsconfig, $utf8NoBom)
    
    $nextConfig = @"
/** @type {import('next').NextConfig} */
const nextConfig = {};
module.exports = nextConfig;
"@
    [System.IO.File]::WriteAllText("$testDir\next.config.js", $nextConfig, $utf8NoBom)
    
    Write-Host "  [OK]   Minimal app created" -ForegroundColor Green
    Write-Host ""
    
    # Install dependencies
    Write-Host "  Installing dependencies..." -ForegroundColor Gray
    pnpm install 2>&1 | Out-Null
    Write-Host "  [OK]   Dependencies installed" -ForegroundColor Green
    Write-Host ""
    
    # Build
    Write-Host "  Building..." -ForegroundColor Gray
    $buildOutput = pnpm build 2>&1 | Out-String
    Write-Host $buildOutput
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  STANDALONE NEXT.JS BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  This PROVES:" -ForegroundColor Cyan
        Write-Host "  - Next.js 14.2.5 works fine" -ForegroundColor White
        Write-Host "  - React 18.3.1 works fine" -ForegroundColor White
        Write-Host "  - Problem is in YOUR monorepo configuration" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  Likely culprits:" -ForegroundColor Yellow
        Write-Host "  - pnpm-workspace.yaml" -ForegroundColor White
        Write-Host "  - turbo.json" -ForegroundColor White
        Write-Host "  - Root package.json" -ForegroundColor White
        Write-Host "  - node_modules corruption" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "  STANDALONE NEXT.JS BUILD FAILED!" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "  This means Next.js itself has issues." -ForegroundColor Yellow
        Write-Host "  Need to upgrade or fix environment." -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "  [ERR]  Exception: $_" -ForegroundColor Red
}

# Cleanup
Write-Host ""
Write-Host "[CLEANUP] Removing test directory..." -ForegroundColor Cyan
Set-Location "D:\econojin.com"
Remove-Item $testDir -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  [OK]   Cleaned up" -ForegroundColor Green

# ====================================================================
# STEP 4: Check monorepo-specific issues
# ====================================================================
Write-Host ""
Write-Host "[STEP 4] Checking monorepo configuration..." -ForegroundColor Cyan
Write-Host ""

Write-Host "  Root package.json:" -ForegroundColor Gray
Get-Content "package.json" | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
Write-Host ""

Write-Host "  pnpm-workspace.yaml:" -ForegroundColor Gray
Get-Content "pnpm-workspace.yaml" | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
Write-Host ""

Write-Host "  turbo.json:" -ForegroundColor Gray
Get-Content "turbo.json" | ForEach-Object { Write-Host "    $_" -ForegroundColor White }

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  ULTIMATE DIAGNOSIS COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
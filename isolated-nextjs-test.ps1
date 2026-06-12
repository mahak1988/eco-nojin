$ErrorActionPreference = "Stop"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   ISOLATED NEXT.JS TEST" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# ====================================================================
# STEP 1: Check next.config.js
# ====================================================================
Write-Host "[STEP 1] Checking next.config.js..." -ForegroundColor Cyan
Write-Host ""

$nextConfigPath = "apps\web\next.config.js"
if (Test-Path $nextConfigPath) {
    Write-Host "  Content:" -ForegroundColor Gray
    Get-Content $nextConfigPath | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
} else {
    Write-Host "  [ERR]  NOT FOUND!" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# STEP 2: Check globals.css
# ====================================================================
Write-Host "[STEP 2] Checking globals.css..." -ForegroundColor Cyan
Write-Host ""

$globalsCssPath = "apps\web\src\app\globals.css"
if (Test-Path $globalsCssPath) {
    $content = Get-Content $globalsCssPath -Raw
    Write-Host "  File size: $($content.Length) chars" -ForegroundColor Gray
    
    # Check for common issues
    if ($content -match '@import') {
        Write-Host "  [WARN] Has @import (might cause issues)" -ForegroundColor Yellow
    }
    
    Write-Host "  First 20 lines:" -ForegroundColor Gray
    Get-Content $globalsCssPath -TotalCount 20 | ForEach-Object { Write-Host "    $_" -ForegroundColor DarkGray }
} else {
    Write-Host "  [ERR]  NOT FOUND!" -ForegroundColor Red
}
Write-Host ""

# ====================================================================
# STEP 3: Create minimal Next.js app in temp folder
# ====================================================================
Write-Host "[STEP 3] Creating minimal Next.js app in temp folder..." -ForegroundColor Cyan
Write-Host ""

$tempDir = "temp-nextjs-test"
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}

New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
Set-Location $tempDir

# Create package.json
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
  }
}
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$PWD\package.json", $packageJson, $utf8NoBom)

# Create next.config.js
$nextConfig = @"
/** @type {import('next').NextConfig} */
const nextConfig = {};
module.exports = nextConfig;
"@

[System.IO.File]::WriteAllText("$PWD\next.config.js", $nextConfig, $utf8NoBom)

# Create tsconfig.json
$tsConfig = @"
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
    "plugins": [{ "name": "next" }]
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"@

[System.IO.File]::WriteAllText("$PWD\tsconfig.json", $tsConfig, $utf8NoBom)

# Create src/app structure
New-Item -ItemType Directory -Path "src\app" -Force | Out-Null

# Create layout.tsx
$layout = @"
export const metadata = {
  title: 'Test',
  description: 'Test',
};

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

[System.IO.File]::WriteAllText("$PWD\src\app\layout.tsx", $layout, $utf8NoBom)

# Create page.tsx
$page = @"
export default function HomePage() {
  return <div>Hello World</div>;
}
"@

[System.IO.File]::WriteAllText("$PWD\src\app\page.tsx", $page, $utf8NoBom)

# Create (auth) route group
New-Item -ItemType Directory -Path "src\app\(auth)\login" -Force | Out-Null

$authLayout = @"
export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <div>{children}</div>;
}
"@

[System.IO.File]::WriteAllText("$PWD\src\app\(auth)\layout.tsx", $authLayout, $utf8NoBom)

$loginPage = @"
export default function LoginPage() {
  return <div>Login Page</div>;
}
"@

[System.IO.File]::WriteAllText("$PWD\src\app\(auth)\login\page.tsx", $loginPage, $utf8NoBom)

Write-Host "  [OK]   Minimal app created" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 4: Install dependencies
# ====================================================================
Write-Host "[STEP 4] Installing dependencies..." -ForegroundColor Cyan
Write-Host ""

try {
    pnpm install
    Write-Host ""
    Write-Host "  [OK]   Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "  [ERR]  Install failed: $_" -ForegroundColor Red
    Set-Location ".."
    Remove-Item $tempDir -Recurse -Force
    exit 1
}
Write-Host ""

# ====================================================================
# STEP 5: Try build
# ====================================================================
Write-Host "[STEP 5] Building minimal app..." -ForegroundColor Cyan
Write-Host ""

$buildSuccess = $false
try {
    pnpm build 2>&1 | Out-String | Write-Host
    
    if ($LASTEXITCODE -eq 0) {
        $buildSuccess = $true
    }
} catch {
    Write-Host "  Build failed" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 6: Analyze results
# ====================================================================
Set-Location ".."

if ($buildSuccess) {
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  MINIMAL APP BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  This means:" -ForegroundColor Cyan
    Write-Host "  - Next.js 14.2.5 works fine" -ForegroundColor White
    Write-Host "  - Route Groups work fine" -ForegroundColor White
    Write-Host "  - Problem is in YOUR project files" -ForegroundColor White
    Write-Host ""
    Write-Host "  Next step: Binary search to find problematic file" -ForegroundColor Yellow
} else {
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  MINIMAL APP BUILD FAILED!" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  This means:" -ForegroundColor Cyan
    Write-Host "  - Next.js 14.2.5 has issues" -ForegroundColor White
    Write-Host "  - Or environment problem" -ForegroundColor White
    Write-Host "  - Need to upgrade Next.js" -ForegroundColor White
}

# Cleanup
Remove-Item $tempDir -Recurse -Force
Write-Host ""
Write-Host "  [CLEANUP] Temp folder removed" -ForegroundColor Gray

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  TEST COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
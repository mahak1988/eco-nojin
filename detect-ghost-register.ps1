$ErrorActionPreference = "Continue"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   FIX GHOST REGISTER ROUTE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
$root = (Get-Location).Path

# ====================================================================
# STEP 1: Create dummy register page
# ====================================================================
Write-Host "[STEP 1] Creating dummy register page..." -ForegroundColor Cyan
Write-Host ""

$registerDir = "apps\web\src\app\(auth)\register"
if (-not (Test-Path -LiteralPath $registerDir)) {
    New-Item -ItemType Directory -Path $registerDir -Force | Out-Null
    Write-Host "  [CREATED] Directory: $registerDir" -ForegroundColor Green
}

$registerContent = @'
export const metadata = {
  title: 'Register - Econojin',
};

export default function RegisterPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Register</h1>
      <p className="text-gray-600">
        Registration page is under construction.
      </p>
    </div>
  );
}
'@

$registerPath = Join-Path $registerDir "page.tsx"
[System.IO.File]::WriteAllText((Join-Path $root $registerPath), $registerContent, $utf8NoBom)
Write-Host "  [CREATED] $registerPath" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 2: Clean ALL caches
# ====================================================================
Write-Host "[STEP 2] Cleaning ALL caches..." -ForegroundColor Cyan
Write-Host ""

$cacheDirs = @(
    "apps\web\.next",
    ".turbo",
    "node_modules\.cache"
)

foreach ($dir in $cacheDirs) {
    if (Test-Path -LiteralPath $dir) {
        Remove-Item -LiteralPath $dir -Recurse -Force
        Write-Host "  [DEL]  $dir" -ForegroundColor Yellow
    }
}

# Delete next-env.d.ts
$nextEnv = "apps\web\next-env.d.ts"
if (Test-Path -LiteralPath $nextEnv) {
    Remove-Item -LiteralPath $nextEnv -Force
    Write-Host "  [DEL]  $nextEnv" -ForegroundColor Yellow
}

Write-Host ""

# ====================================================================
# STEP 3: Test build
# ====================================================================
Write-Host "[STEP 3] Testing build..." -ForegroundColor Cyan
Write-Host ""

$buildSuccess = $false
try {
    $output = pnpm --filter @econojin/web build 2>&1 | Out-String
    Write-Host $output
    
    if ($LASTEXITCODE -eq 0) {
        $buildSuccess = $true
    }
} catch {
    Write-Host "  Build failed: $_" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 4: Report
# ====================================================================
if ($buildSuccess) {
    Write-Host "================================================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host "================================================================" -ForegroundColor Green
} else {
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED" -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Check error above for next problematic route." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
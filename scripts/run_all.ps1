#═══════════════════════════════════════════════════════════════════════
#  🚀 Econojin All-in-One Runner  (Phase 2 + 3)
#  -----------------------------------------------------------------------
#  این اسکریپت هر سه سرویس را به‌صورت همزمان اجرا می‌کند:
#    1. Backend (FastAPI)              → http://localhost:8000
#    2. Frontend (apps/web, Vite)      → http://localhost:5173
#    3. Admin Panel (apps/admin_panel) → http://localhost:5174
#
#  هر سرویس در یک پنجره PowerShell جداگانه باز می‌شود.
#  برای توقف، کافی است هر پنجره را ببندید یا Ctrl+C بزنید.
#
#  پیش‌نیازها:
#    - Python 3.10+ با venv در D:\econojin.com\eco-nojin\.venv
#    - Node.js 22+ و pnpm 11+
#    - فایل .env در ریشه پروژه (با SECRET_KEY حداقل ۳۲ کاراکتر)
#    - نصب وابستگی‌های Python (pip install -r requirements یا حداقلی)
#    - pnpm install در ریشه پروژه (برای monorepo)
#
#  نحوه اجرا:
#    PowerShell را باز کنید، به پوشه پروژه بروید، سپس:
#      .\run_all.ps1
#  یا اگر Execution Policy محدود است:
#      Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#      .\run_all.ps1
#═══════════════════════════════════════════════════════════════════════

# ── Configuration ──────────────────────────────────────────────────────
$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\econojin.com\eco-nojin"
$VenvPython = "$ProjectRoot\.venv\Scripts\python.exe"
$VenvActivate = "$ProjectRoot\.venv\Scripts\Activate.ps1"

# ── Banner ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🚀 Econojin All-in-One Runner" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Project Root: $ProjectRoot"
Write-Host "  Backend:      http://localhost:8000  (FastAPI)"
Write-Host "  Frontend:     http://localhost:5173  (apps/web)"
Write-Host "  Admin Panel:  http://localhost:5174  (apps/admin_panel)"
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ── Pre-flight checks ─────────────────────────────────────────────────
function Test-Command {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    return $null -ne $cmd
}

Write-Host "  [i] بررسی پیش‌نیازها..." -ForegroundColor Yellow

# 1. Project folder
if (-Not (Test-Path $ProjectRoot)) {
    Write-Host "  [✗] پوشه پروژه پیدا نشد: $ProjectRoot" -ForegroundColor Red
    Write-Host "      ابتدا مخزن را کلون کنید: git clone https://github.com/mahak1988/eco-nojin.git"
    exit 1
}
Write-Host "  [✓] پوشه پروژه" -ForegroundColor Green

# 2. venv
if (-Not (Test-Path $VenvPython)) {
    Write-Host "  [✗] venv پیدا نشد: $VenvPython" -ForegroundColor Red
    Write-Host "      بسازید: cd '$ProjectRoot'; python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt"
    exit 1
}
Write-Host "  [✓] venv" -ForegroundColor Green

# 3. .env
if (-Not (Test-Path "$ProjectRoot\.env")) {
    Write-Host "  [!] .env وجود ندارد. از .env.example کپی می‌شود..." -ForegroundColor Yellow
    Copy-Item "$ProjectRoot\.env.example" "$ProjectRoot\.env"
    Write-Host "  [i] لطفاً .env را ویرایش کرده و SECRET_KEY را تنظیم کنید." -ForegroundColor Yellow
}
Write-Host "  [✓] .env" -ForegroundColor Green

# 4. pnpm
if (-Not (Test-Command "pnpm")) {
    Write-Host "  [✗] pnpm نصب نیست." -ForegroundColor Red
    Write-Host "      نصب: npm install -g pnpm@11.4.0"
    exit 1
}
Write-Host "  [✓] pnpm" -ForegroundColor Green

# 5. node_modules (در root برای monorepo)
if (-Not (Test-Path "$ProjectRoot\node_modules")) {
    Write-Host "  [!] node_modules وجود ندارد. در حال اجرای pnpm install..." -ForegroundColor Yellow
    Push-Location $ProjectRoot
    pnpm install
    Pop-Location
}
Write-Host "  [✓] node_modules" -ForegroundColor Green

Write-Host ""
Write-Host "  [✓] همه پیش‌نیازها OK." -ForegroundColor Green
Write-Host ""

# ── Start services in separate windows ─────────────────────────────────
$backendScript = @"
cd '$ProjectRoot'
& '$VenvActivate'
Write-Host 'Starting Backend (FastAPI) on port 8000...' -ForegroundColor Green
Write-Host 'Docs: http://localhost:8000/docs' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop.' -ForegroundColor Gray
Write-Host ''
python -m uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
"@

$frontendScript = @"
cd '$ProjectRoot'
Write-Host 'Starting Frontend (apps/web, Vite) on port 5173...' -ForegroundColor Green
Write-Host 'URL: http://localhost:5173' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop.' -ForegroundColor Gray
Write-Host ''
pnpm dev:web
"@

$adminScript = @"
cd '$ProjectRoot\apps\admin_panel\frontend'
Write-Host 'Starting Admin Panel on port 5174...' -ForegroundColor Green
Write-Host 'URL: http://localhost:5174' -ForegroundColor Cyan
Write-Host 'Press Ctrl+C to stop.' -ForegroundColor Gray
Write-Host ''
npx vite --port 5174
"@

Write-Host "  [i] راه‌اندازی Backend در پنجره جدید..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript
Start-Sleep -Seconds 2

Write-Host "  [i] راه‌اندازی Frontend در پنجره جدید..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript
Start-Sleep -Seconds 2

Write-Host "  [i] راه‌اندازی Admin Panel در پنجره جدید..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", $adminScript

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "  ✓ هر سه سرویس در پنجره‌های جداگانه شروع شدند." -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "  📚 Backend Docs:   http://localhost:8000/docs"
Write-Host "  🌐 Frontend:       http://localhost:5173"
Write-Host "  🛡️  Admin Panel:   http://localhost:5174"
Write-Host ""
Write-Host "  برای توقف، پنجره‌های مربوطه را ببندید یا Ctrl+C بزنید."
Write-Host ""

# ── Health check (optional, after 5 seconds) ───────────────────────────
Write-Host "  [i] بررسی سلامت سرویس‌ها بعد از ۱۰ ثانیه..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

$endpoints = @(
    @{ Name = "Backend";  Url = "http://localhost:8000/health" },
    @{ Name = "Frontend"; Url = "http://localhost:5173" },
    @{ Name = "Admin";    Url = "http://localhost:5174" }
)

foreach ($ep in $endpoints) {
    try {
        $response = Invoke-WebRequest -Uri $ep.Url -TimeoutSec 5 -UseBasicParsing
        Write-Host "  [✓] $($ep.Name): HTTP $($response.StatusCode) - $($ep.Url)" -ForegroundColor Green
    } catch {
        Write-Host "  [!] $($ep.Name): در حال راه‌اندازی یا خطا - $($ep.Url)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "  برای خروج از این پنجره، Enter را بزنید." -ForegroundColor Gray
Read-Host

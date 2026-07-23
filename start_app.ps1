# start_app.ps1 — راه‌اندازی سریع پروژه بدون داکر
Write-Host "🚀 در حال آماده‌سازی محیط اجرای Econojin..." -ForegroundColor Green

# ۱. بررسی و نصب پیش‌نیازهای بک‌اند با uv
Write-Host "⚙️  در حال به‌روزرسانی وابستگی‌های Python..." -ForegroundColor Cyan
uv pip install -r requirements.txt

# ۲. نصب پیش‌نیازهای فرانت‌اند (فقط اگر node_modules وجود ندارد)
if (-Not (Test-Path "node_modules")) {
    Write-Host "📦 در حال نصب پکیج‌های Node.js (pnpm)..." -ForegroundColor Cyan
    pnpm install
}

Write-Host "✅ آماده‌سازی کامل شد!" -ForegroundColor Green
Write-Host "🌐 در حال اجرای سرور Backend و Frontend..." -ForegroundColor Yellow
Write-Host "برای توقف، در این پنجره Ctrl+C را بزنید." -ForegroundColor Gray

# ۳. اجرای همزمان با استفاده از Start-Process (برای باز شدن در پنجره‌های جداگانه)
# یا اجرای Turbo Dev به صورت یکپارچه
pnpm dev
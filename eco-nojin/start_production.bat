@echo off
chcp 65001 >nul
echo ===================================================
echo   🚀 در حال راه‌اندازی Econojin API (Production Mode)
echo ===================================================
echo.

REM بررسی نصب بودن uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ خطا: ابزار 'uv' نصب نیست. لطفاً ابتدا uv را نصب کنید.
    pause
    exit /b
)

echo ⚙️ در حال به‌روزرسانی وابستگی‌ها...
uv pip install -r requirements.txt

echo.
echo 🌐 در حال اجرای سرور روی پورت 8000...
echo برای توقف، پنجره را ببندید یا Ctrl+C را بزنید.
echo ===================================================
echo.

uv run uvicorn apps.main:app --host 0.0.0.0 --port 8000 --workers 2
pause

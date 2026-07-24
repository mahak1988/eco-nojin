@echo off
chcp 65001 >nul
title Econojin Repo Sync
echo ═══════════════════════════════════════════════════
echo   Econojin Repository Sync
echo ═══════════════════════════════════════════════════
echo.

REM ── بررسی Python ──
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found in PATH!
    pause
    exit /b 1
)

REM ── بررسی Git ──
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git not found in PATH!
    pause
    exit /b 1
)

echo [1/2] Running DRY-RUN first (preview only)...
echo ───────────────────────────────────────────────────
python "%~dp0sync_repo.py" --dry-run
echo.

echo ───────────────────────────────────────────────────
set /p CONFIRM="Apply changes? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Cancelled.
    pause
    exit /b 0
)

echo.
echo [2/2] Syncing with backup...
echo ───────────────────────────────────────────────────
python "%~dp0sync_repo.py"
echo.
pause
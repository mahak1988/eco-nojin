# Local recovery (Windows)

## A) git pull OK but API not running

Port 8000 closed means uvicorn is not started. Start it first.

## B) run_local.ps1 ParseException (MissingEndCurlyBrace)

Pull latest (ASCII-only script):

```powershell
cd D:\econojin.com
git pull origin main
```

## C) Python 3.14 venv error

```
Unable to copy ... venvlauncher.exe ... python.exe
```

Known Windows + Python 3.14 issue. Script falls back to system Python.

Prefer 3.11/3.12:

```powershell
py -0p
py -3.12 -m pip install -r requirements.txt
$env:PYTHONPATH = "D:\econojin.com"
$env:ENVIRONMENT = "local"
$env:DATABASE_URL = "sqlite+aiosqlite:///./apps/econojin.db"
$env:ENABLE_RATE_LIMIT = "true"
$env:ENABLE_AUDIT_LOG = "true"
$env:ENABLE_SPIDERGUARD = "false"
py -3.12 -m uvicorn apps.main:app --reload --reload-dir apps --host 0.0.0.0 --port 8000
```

Or:

```powershell
.\scripts\run_local.ps1
# or
.\scripts\start_api_simple.ps1
```

## D) Verify

```powershell
curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/health
```

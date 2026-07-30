# بازیابی local (git pull + venv + celery)

## ۱. git pull گیر کرده روی `.devcontainer`

```powershell
cd D:\econojin.com
.\scripts\recover_git_pull.ps1
# یا دستی:
# Move-Item .devcontainer\devcontainer.json .devcontainer\devcontainer.json.localbak -Force
# git pull origin main
```

## ۲. `.venv` خراب (`Activate.ps1` پیدا نشد)

```powershell
cd D:\econojin.com
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
python -m venv .venv
.\scripts\run_local.ps1
```

`run_local.ps1` بدون Activate هم با `Scripts\python.exe` کار می‌کند.

## ۳. `No module named 'celery'`

از commit اخیر، celery **اختیاری** است (stub sync). بعد از pull:

- `science_phase3` و `simulation_jobs` باید load شوند حتی بدون pip install celery
- در صورت تمایل: `.\.venv\Scripts\python.exe -m pip install "celery[redis]>=5.4.0"`

## ۴. reload بی‌دلیل از `node_modules`

uvicorn فقط `--reload-dir apps` — دیگر فایل‌های pnpm را رصد نمی‌کند.

## ۵. تأیید فاز ۱

```powershell
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
```

`security.rate_limit` باید `true` باشد و `failed_routers` خالی یا بدون celery error.

# Hotfix: farms seed + Vite API_BASE

## Root cause
1. Local tree was **behind** `origin/main` (`seed_farms` still had `total = meta dict`).
2. Vite failed because local `simulationApi.ts` lacked `export const API_BASE`.

## Fix on server (already pushed)
- `seed_farms` uses `SELECT COUNT(*)` on `Farm` (no meta tuple).
- `simulationApi.ts` always has `export const API_BASE = ""` and `API_V1 = "/api/v1"`.

## On your PC (required)

```powershell
cd D:\econojin.com

# Preferred one-shot:
.\scripts\sync_and_verify.ps1

# Or manual:
git fetch origin
git checkout main
git reset --hard origin/main

# Confirm fixed line exists:
Select-String -Path apps\farms\router.py -Pattern "func.count"
Select-String -Path apps\web\src\lib\simulationApi.ts -Pattern "export const API_BASE"

# Restart API (Ctrl+C then):
.\scripts\run_local.ps1

curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/farms/seed-demo
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/farms?page=1&size=5"

cd apps\web
Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue
pnpm dev
```

Expect seed: `{"seeded":3,"message":"ok"}` (or already has farms).
Expect Vite without API_BASE errors.

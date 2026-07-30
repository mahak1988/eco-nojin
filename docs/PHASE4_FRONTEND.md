# Phase 4 — Frontend API + i18n

## Rules
- All **source code** in English.
- UI strings only via `t('common.nav.farms')` style keys.
- Locales: **en** (source of truth), **fa**, **ar**.

## Delivered bootstrap
| Path | Role |
|------|------|
| `apps/web/src/i18n/` | Locale packs + `t()` |
| `apps/web/src/api/resources.ts` | farms/crops/dashboard/auth fetchers |
| `apps/web/src/api/http.ts` | existing fetch + cookies |

## Verify API first
```powershell
git pull origin main
# restart API
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/crops?page=1&size=5"
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/farms?page=1&size=5"
.\.venv\Scripts\python.exe -m pytest tests/contract/test_phase3_api.py -q
```
Expect JSON `{ "data": [...], "meta": {...} }` not INTERNAL_ERROR.

Optional seed crops:
```powershell
# needs auth permission in prod; local may allow via flag
curl.exe -X POST -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/crops/seed-demo"
```

## FE
```powershell
cd D:\econojin.com\apps\web
pnpm install
pnpm dev
```

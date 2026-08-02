# Frontend ↔ API connection

## Required processes

1. API: `uvicorn apps.main:app --reload --host 127.0.0.1 --port 8000`
2. Web: from repo root `pnpm dev:web` → open **http://127.0.0.1:5173**

Do **not** use `http://192.168.x.x:517x` for local dev (proxy/HMR breaks).

## Verify

```powershell
curl http://127.0.0.1:8000/health
# Browser Network tab: GET /health should be 200 via Vite proxy
```

Banner at top of app should show `API connected`.

## Common failures

| Symptom | Cause |
|---------|--------|
| Timeout /health in UI, curl OK | Vite dead or wrong host; restart `pnpm dev:web` |
| 401 /users/me | Not logged in (normal) |
| DestinationHero crash | Fixed: wrong import of SectionReveal |
| Fake MRV rows | Removed; empty until DB has projects |

## Simulators priority (backend)

Already registered pure-Python proxies: `rusle2`, `qual2k`, `maxent`. WEAP/CBA under hydrology/economics modules.

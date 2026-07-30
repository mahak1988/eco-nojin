# Phase 4 in progress

API list OK (empty until seed). Pull and seed:

```powershell
git pull origin main
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/crops/seed-demo
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/farms/seed-demo
```

Then FE: `cd apps\web; pnpm dev` → `/crops` `/farms`

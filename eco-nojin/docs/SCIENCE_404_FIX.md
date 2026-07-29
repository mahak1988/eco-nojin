# Fix /api/v1/science 404

## Cause
Science router lived only under `apps.simulation.phase3_router` and could fail silently on import. Failed includes become 404.

## Fix
Primary mount: `apps/api/routes/science.py` (same pattern as education).

## You must

```powershell
cd D:\econojin.com
git pull origin main
git log -1 --oneline
# expect commit mentioning science routes via apps/api/routes/science.py

# Kill ALL python/uvicorn on 8000, then:
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
```

Look for: `science: router loaded`

```powershell
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
# science_loaded should be true

curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/debug/routers
# science_paths non-empty

curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/status
```

If `project_root` in /health is NOT `D:\econojin.com`, you are running the wrong tree.

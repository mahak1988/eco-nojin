# Frontend ↔ Backend connection (local)

## Correct setup

1. **Terminal A – API**
   ```powershell
   cd D:\econojin.com
   git pull
   uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Terminal B – Web**
   ```powershell
   cd D:\econojin.com\apps\web
   # Do NOT set VITE_API_BASE_URL unless you know you need it
   pnpm install
   pnpm dev
   ```
   Open **http://localhost:5173**

3. **Seed demo courses (once)**
   ```powershell
   curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/seed-demo
   ```

4. **Verify**
   ```powershell
   curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
   # expect: "database":"ok"
   curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/courses
   # expect: items with titles after seed
   ```

## How traffic flows

Browser → `http://localhost:5173/api/v1/...` → **Vite proxy** → `http://127.0.0.1:8000/api/v1/...`

Same for `/health`.

If `VITE_API_BASE_URL=http://localhost:8000` is set, browser calls API **directly** (CORS must allow 5173). Proxy mode is safer.

## Symptoms

| Symptom | Cause | Fix |
|---------|-------|-----|
| Badge always SAMPLE | API down or wrong base URL | Start uvicorn; clear VITE_API_* |
| CORS error in console | Direct call without CORS | Use proxy (empty API base) |
| health database fail | old code without get_engine | git pull + restart |
| courses items [] | empty DB | POST seed-demo |
| 500 MutableHeaders.pop | fixed in security middleware | git pull |

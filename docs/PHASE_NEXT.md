# فاز بعدی

**فاز ۱ (امنیت):** انجام‌شده در مخزن — `docs/PHASE1_SECURITY.md`

**فاز ۲ بعدی:** دیتابیس local-first — merge Alembic heads، seed پایدار SQLite.

```powershell
cd D:\econojin.com
git pull origin main
Copy-Item .env.example .env -ErrorAction SilentlyContinue
.\scripts\run_local.ps1
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/health
```

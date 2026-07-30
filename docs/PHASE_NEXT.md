# فاز بعدی

**فاز ۱:** امنیتی — تأیید شده با health.security
**فاز ۲:** دیتابیس — `docs/PHASE2_DATABASE.md` + migrations idempotent

```powershell
cd D:\econojin.com
git pull origin main
.\scripts\alembic_upgrade_safe.ps1
# سپس restart API یا:\n.\scripts\run_local.ps1
```

**فاز ۳ بعدی:** یکپارچه‌سازی API (debug routers، pagination، contract smoke)

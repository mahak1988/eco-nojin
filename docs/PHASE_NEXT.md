# فاز بعدی

**الان:** فاز ۱ از برنامه ۱۰فازی (`docs/AUDIT_PROGRESS_10_PHASES.md`) — امنیت/Hardening روی Zero-Install.

**کلیدها:** بعد از فاز ۱۰ — نقشه در `docs/ENV_KEYS_MAP.md`.

```powershell
cd D:\econojin.com
git pull origin main
Copy-Item .env.example .env -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force secrets | Out-Null
.\scripts\run_local.ps1
```

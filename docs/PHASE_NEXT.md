# فاز بعدی

- فاز ۱–۲: تأیید شده
- فاز ۳: `docs/PHASE3_API.md`

```powershell
git pull origin main
curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/dashboard/stats
.\.venv\Scripts\python.exe -m pytest tests/contract/test_phase3_api.py -q
```

فاز ۴ بعدی: اتصال کامل FE (login, farms, crops, science)

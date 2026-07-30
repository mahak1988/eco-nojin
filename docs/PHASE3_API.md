# فاز ۳ — یکپارچه‌سازی API

## تحویل‌ها

| آیتم | مسیر |
|------|------|
| Pagination helpers | `apps/shared_core/schemas/pagination.py` |
| Error envelope | `apps/shared_core/schemas/errors.py` |
| Dashboard canonical | `GET /api/v1/dashboard/stats` + `/overview` |
| Science-only view | `GET /api/v1/dashboard/science-overview` |
| Contract smoke | `tests/contract/test_phase3_api.py` |

## تأیید

```powershell
cd D:\econojin.com
git pull origin main
# API باید در حال اجرا باشد یا:\n.\scripts\run_local.ps1

curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/dashboard/stats
curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/dashboard/overview
curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/debug/routers

.\.venv\Scripts\python.exe -m pytest tests/contract/test_phase3_api.py -q
```

## معیار پذیرش

- [ ] stats و overview → 200 با counts
- [ ] debug/routers → loaded list
- [ ] pytest phase3 سبز (یا با DB local)

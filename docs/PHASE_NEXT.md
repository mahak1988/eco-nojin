# Next phase

## Done
- Phase 1 security
- Phase 2 alembic head `20260729_0002`
- Phase 3 dashboard + pagination (ListMeta restored)

## Hotfix (pull now)
`ListMeta` / `build_meta` restored so farms/crops/education load again.

```powershell
cd D:\econojin.com
git pull origin main
# restart API (Ctrl+C then):\n.\scripts\run_local.ps1
curl.exe -H "User-Agent: Mozilla/5.0" http://127.0.0.1:8000/api/v1/debug/routers
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/crops?page=1&size=5"
.\.venv\Scripts\python.exe -m pytest tests/contract/test_phase3_api.py -q
```

## Before Phase 4
- `.env.example` complete + `docs/KEYS_CHECKLIST.md`
- `docs/I18N_PLAN.md` — English source, fa/ar translation keys

## Phase 4
FE live API wiring + i18n bootstrap (en/fa/ar)

# Status

- Phase 1–3 OK after `page_to_offset` returns **int** again (fixes farms/crops 500).
- Phase 4 started: i18n en/fa/ar + `api/resources.ts`.

```powershell
git pull origin main
# restart API then:
curl.exe -H "User-Agent: Mozilla/5.0" "http://127.0.0.1:8000/api/v1/crops?page=1&size=5"
```

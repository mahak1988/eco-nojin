# Econojin (اکو نوژین)

**Integrated platform for smart agriculture, water, environment, green economy, and rural community.**

پلتفرم یکپارچه کشاورزی هوشمند، آب، محیط‌زیست، اقتصاد سبز و جامعه روستایی.

## Governance

- **Hard rules:** [docs/CONSTITUTION.md](docs/CONSTITUTION.md) (R1–R23)
- **Glossary fa/en:** [docs/GLOSSARY_FA_EN.md](docs/GLOSSARY_FA_EN.md)
- **Science formulas:** [docs/SCIENCE_FORMULAS.md](docs/SCIENCE_FORMULAS.md)
- **Honest backlog:** [docs/REMAINING.md](docs/REMAINING.md)
- **SSOT status:** [docs/PHASE_1_2_SSOT.md](docs/PHASE_1_2_SSOT.md)

UI languages: **fa / en**. Code & API identifiers: **English**.

---

## Status (2026-07-28)

| Area | Status |
|------|--------|
| Phase 0–2 core | ✅ in repo (local SQLite OK) |
| Phase 3 science API | ✅ `/api/v1/science/*` |
| Process models | ✅ FAO Ky AquaCrop *conceptual*, RothC-26.3, SCS-CN |
| FE Science UI | ✅ `/science` |
| Docker / PostGIS on host | ⚠️ optional — install Docker |
| Live GEE | ⚠️ needs service account |
| Official FAO/SWAT binaries | ❌ not bundled (by design) |

---

## Quickstart

```bash
git clone https://github.com/mahak1988/eco-nojin.git
cd eco-nojin
pip install -r requirements.txt
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

cd apps/web && pnpm install && pnpm dev
```

| Service | URL |
|---------|-----|
| API docs | http://localhost:8000/docs |
| Health | http://localhost:8000/health |
| Science status | http://localhost:8000/api/v1/science/status |
| Debug routers | http://localhost:8000/api/v1/debug/routers |
| Web | http://localhost:5173 |
| Science UI | http://localhost:5173/science |

### Science curls

```bash
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/science/status
curl.exe -X POST -H "User-Agent: Mozilla/5.0" -H "Content-Type: application/json" ^
  -d "{\"days\":40,\"rain_mm_day\":0.4,\"crop\":\"wheat\"}" ^
  http://localhost:8000/api/v1/science/aquacrop-advanced
```

### Tests

```bash
pytest tests/unit/test_real_science.py tests/contract/test_science_endpoints.py -q
```

---

## License

MIT — see [License](License).

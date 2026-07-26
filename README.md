# Econojin (اکو نوژین)

**Integrated platform for smart agriculture, water, environment, green economy, and rural community.**

## Governance

- **Hard rules:** [docs/CONSTITUTION.md](docs/CONSTITUTION.md) (R1–R23 — non-negotiable)
- **Compliance gaps:** [docs/RULES_GAP.md](docs/RULES_GAP.md)
- **TO-BE roadmap:** [docs/ROADMAP_TOBE.md](docs/ROADMAP_TOBE.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)

UI languages: **fa / en** only. Code & technical docs: **English**.

---

## Status (2026-07-27)

| Area | Status |
|------|--------|
| API boot + `/health` | ✅ |
| Education list + seed | ✅ (async relationship fix) |
| FE Vite proxy | ✅ |
| `requirements.txt` | ✅ |
| CORS explicit (R10) | ✅ |
| Model registry | ✅ expanded |
| Alembic-first non-local (R11) | ✅ policy enforced in `init_db` |
| RS256 + HttpOnly cookies (R4–R5) | ❌ gap |
| RBAC permissions (R6) | ⚠️ partial |
| Celery / WebSocket | ❌ |

---

## Quickstart

```bash
git clone https://github.com/mahak1988/eco-nojin.git
cd eco-nojin
cp .env.example .env

pip install -r requirements.txt
uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

cd apps/web && pnpm install && pnpm dev
```

- API: http://localhost:8000/docs  
- Web: http://localhost:5173  
- Do **not** set `VITE_API_BASE_URL` for local proxy mode  
- CORS allows listed localhost origins only (R10)

```bash
curl.exe -X POST -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/seed-demo
curl.exe -H "User-Agent: Mozilla/5.0" http://localhost:8000/api/v1/education/courses
```

---

## Architecture

```
apps/main.py           FastAPI entry
apps/shared_core/      config, security, database, middleware
apps/api/routes/       domain HTTP adapters
apps/web/              React + Vite + TypeScript
docs/CONSTITUTION.md   binding engineering law
```

New backend modules **must** follow R3: `router / service / repository / schemas / models / tests`.

---

## License

MIT — see [License](License).

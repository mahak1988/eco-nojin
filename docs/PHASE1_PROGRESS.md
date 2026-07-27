# Phase 1 progress

## Stage 1 — HttpOnly cookies — DONE
## Stage 2 — require_permission writes — DONE
## Stage 3 — FE Education real API — DONE

- `EducationPage` states: **loading / error / empty / ready** (R16)
- Fetches `/api/v1/education/courses?page=&size=` with credentials
- Maps API envelope `data`/`items` → CourseCard model
- Empty → optional **Seed demo courses** button
- Error → Retry; Refresh control in header
- Mock only when `VITE_USE_MOCK=true` (R1)

### FE check
1. API running on :8000
2. Vite proxy or `VITE_API_BASE_URL=http://localhost:8000`
3. Open Education page → should show API courses (badge `api`)
4. Stop API → Error + Retry
5. Empty DB → Empty + Seed demo

## Stage 4 — Accounting seed + contract tests (next)

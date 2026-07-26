# API ↔ UI map

| Page / Feature | Route (UI) | API | Client | Status |
|----------------|------------|-----|--------|--------|
| Health widget | `/dashboard`, `/admin/health` | `GET /health` | `api/simulation.api`, `lib/apiServices` | live + degraded |
| Login | `/login` | `POST /api/v1/auth/login` | `api/auth.api` | wired |
| Admin overview | `/admin` | `/health`, `/modules` | `hooks/useAdmin` | wired |
| Accounting | `/accounting` | `GET /api/v1/accounting/summary` | `lib/apiServices` + `api/accounting.api` | probe + mock UI |
| Education | `/education` | `GET /api/v1/education/courses` | `lib/apiServices` + `hooks/useEducation` | probe + mock UI |
| Community | `/community` | `GET /api/v1/community/posts` | `api/community.api` | client ready |
| Simulation | `/simulators` | `/api/v1/simulation/*` | `lib/simulationApi` | partial live |
| Dashboard KPIs | `/dashboard` | `/api/v1/dashboard/stats` (optional) | `getDashboardStats` | fallback mock |

## Client rules
1. Prefer `VITE_API_BASE_URL` (default `http://localhost:8000`).
2. On network/4xx/5xx → keep UI usable with `source: mock` badge.
3. Never hide mock as live.

## Next wiring priorities
1. Map education API course shape → `CourseCard` model
2. Accounting summary fields → StatCard numbers when `source=api`
3. Community posts list when API returns items

# API ↔ UI map

| Page | UI route | API | Mapper | Behavior |
|------|----------|-----|--------|----------|
| Education | `/education` | `GET /api/v1/education/courses` | `lib/mappers/education.ts` | If `items.length > 0` → replace mock cards; else keep mock + badge |
| Education stats | same | `GET /api/v1/education/courses/stats` | — | `total_enrollments` → learners KPI |
| Accounting | `/accounting` | `GET /api/v1/accounting/summary` | `lib/mappers/accounting.ts` | Maps income/expense/profit/balance into StatCards |
| Accounting accounts | same | `GET /api/v1/accounting/accounts` | same | Up to 6 accounts when API returns items |
| Dashboard | `/dashboard` | `/health` + optional stats | HealthWidget | Live health; KPIs still sample until dashboard API exists |
| Admin | `/admin/*` | `/health`, `/modules` | useAdmin | Live JSON panels |
| Login | `/login` | `POST /api/v1/auth/login` | auth.api | Token → localStorage |

## Badge rules
- `API · live` = HTTP 200 from backend
- `offline · sample` = timeout/error/empty fallback

## Env
```
VITE_API_BASE_URL=http://localhost:8000
```

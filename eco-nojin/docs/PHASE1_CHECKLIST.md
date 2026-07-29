# Phase 1 checklist status

## Backend modules

| ID | Module | Status |
|----|--------|--------|
| F1.1 | apps/farms | Done — CRUD + GeoJSON |
| F1.2 | apps/crops | Done — 100+ catalog, agronomy, irrigation calc |
| F1.3 | apps/inventory | Done — seeds/fertilizer/pesticide |
| F1.4 | apps/water | Done — dashboard, systems, schedules, quality, calc |
| F1.5 | apps/weather | Done — forecast synthetic + OWM proxy |
| F1.6 | apps/notifications | Done — in-app list + email stub |

Also: apps/planting (plans + tasks)

## Frontend pages

| ID | Pages | Routes | Status |
|----|-------|--------|--------|
| F1.7 | login, register, verify-otp, forgot-password | /login /register /verify-otp /forgot-password | Done |
| F1.8 | profile, security, notifications | /account /account/security /account/notifications | Partial (edit via account) |
| F1.9 | dashboard, weather | /dashboard /weather | Done (onboarding soft) |
| F1.10 | farms list/new/wizard/detail | /farms /farms/new /farms/wizard /farms/:id | Done (edit soft) |
| F1.11 | crops catalog/detail | /crops /crops/:id | Done |
| F1.12 | planting, tasks, inventory | /planting /tasks /inventory | Done |
| F1.13 | water, irrigation | /water /water/irrigation | Done (sources/quality on water page) |

## Agronomy fields on crop detail

planting_method, spacing, depth, seed_rate, irrigation_method/interval, kc_mid, NPK rates, soil pH, harvest_method/moisture, pests, diseases, care_notes

## Irrigation formula

`ETc = ET0 × Kc`  
`gross = ETc / efficiency`  
`volume_m3 = gross_mm × area_ha × 10`

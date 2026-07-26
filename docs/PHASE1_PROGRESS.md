# Phase 1 progress

**Date:** 2026-07-26

## Done
- [x] Engineering language standard (code = English)
- [x] Security architecture doc
- [x] Deploy checklist (Neon + Render/Fly + Pages)
- [x] Frontend structure: api/, hooks/, stores/, types/, features/, admin pages (30+ files)
- [x] Login + Admin shell routes
- [x] apiServices uses absolute API base (Vite fix)
- [x] `/health` reports database ok/fail and overall degraded
- [x] `/docs` disabled when ENVIRONMENT=production
- [x] Error JSON includes `request_id`
- [x] Dashboard HealthWidget + DataSourceBadge

## In progress
- [ ] Map live education/accounting payloads into UI cards (not only probe)
- [ ] Redis rate limit for staging
- [ ] Contract tests in CI

## Blocked / deferred
- Strapi as critical path
- EcoCoin mainnet

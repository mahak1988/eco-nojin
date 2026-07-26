# Rules gap matrix (AS-IS vs Constitution)

Updated: 2026-07-27

| Rule | AS-IS | Target wave | Notes |
|------|-------|-------------|-------|
| R1 | `VITE_USE_MOCK` flag added; pages still need badge discipline | B | mock only when flag true |
| R2 | Violations remain in older files | B | OpenAPI codegen |
| R3 | Mixed layouts | B–C | New modules R3-only |
| R4 | HS256 | **A next** | RS256 |
| R5 | localStorage + `credentials:include` prepared | **A next** | HttpOnly cookies |
| R6 | require_write_auth | B | @require_permission |
| R7 | Partial | A | Redis-backed |
| R8–R9 | Mostly OK | — | |
| R10 | Explicit origins | ✅ | |
| R11 | create_all local-only | ✅ policy | Alembic staging+ |
| R12 | Incomplete | C | Mixins |
| R13–R14 | `types/list.ts` envelope helper | B | Migrate endpoints |
| R15–R18 | Sparse | C | |
| R19 | fetch helper | ✅ path | Drop axios dep if present |
| R20 | session uses settings | ✅ | |
| R21 | Manual includes | C | pkgutil |
| R22–R23 | Partial | B | |

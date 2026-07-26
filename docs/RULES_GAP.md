# Rules gap matrix (AS-IS vs Constitution)

Updated: 2026-07-27

| Rule | AS-IS | Target wave | Notes |
|------|-------|-------------|-------|
| R1 | Partial (education live; many pages still silent mock) | B | `VITE_USE_MOCK` flag to add |
| R2 | Violations exist (`as never`, weak types) | B | OpenAPI codegen |
| R3 | Mixed (api/routes vs apps/module) | B–C | New modules must follow R3 |
| R4 | HS256 | A+ | RS256 keys in env |
| R5 | localStorage common | A+ | HttpOnly cookies |
| R6 | `require_write_auth` only | B | Permission decorator |
| R7 | In-memory / partial | A | Redis for multi-instance |
| R8 | Mostly yes | — | Keep |
| R9 | Mostly yes | — | Audit any `text()` usage |
| R10 | Was `*` in local → **fixed to explicit list** | A | Done this commit |
| R11 | create_all still used locally | A | Alembic required staging+ |
| R12 | Incomplete on many tables | C | Mixins |
| R13–R14 | Mixed list shapes | B | Standard envelope |
| R15 | Sparse | C | Contract suite |
| R16 | Partial | B | Page shells |
| R17 | Flat `{error,message,request_id}` | A | Align to nested `error` |
| R18 | Plain logging | B | JSON logger |
| R19 | Custom fetch exists; axios may still be dep | A | Remove axios dep if present |
| R20 | session/sentry used os.getenv → **session fixed** | A | sentry next |
| R21 | Manual `_include` list | C | pkgutil discovery |
| R22 | OK if .env used | — | Audit scripts |
| R23 | Not enforced in build | B | ESLint no-console |

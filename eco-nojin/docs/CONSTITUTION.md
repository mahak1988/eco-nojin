# EcoNojin Constitution — Hard Rules (R1–R23)

**Status:** Binding for all phases. No rule may be silently ignored.
**Language:** Technical docs English; UI fa/en only.

When a rule is not yet implemented, the gap MUST appear in `docs/RULES_GAP.md` with owner and target wave.

---

## 2.1 Architecture

| ID | Rule |
|----|------|
| **R1** | Every frontend page connects to a real API. Mock only if `VITE_USE_MOCK=true`. |
| **R2** | No `any` or `as never` in TypeScript. Types from OpenAPI codegen. |
| **R3** | Backend module layout: `router / service / repository / schemas / models / tests`. |

## 2.2 Security

| ID | Rule |
|----|------|
| **R4** | JWT **RS256** + refresh token with rotation. |
| **R5** | Tokens in **HttpOnly** cookies (not localStorage). |
| **R6** | RBAC via `@require_permission("resource:action")` on every mutating endpoint. |
| **R7** | Rate limit: 5/min auth, 120/min general API. |
| **R8** | All inputs validated with Pydantic v2. |
| **R9** | No raw SQL; SQLAlchemy ORM/Query only. |
| **R10** | CORS: explicit origins only. `*` forbidden (including local). |

## 2.3 Data

| ID | Rule |
|----|------|
| **R11** | Schema changes only via **Alembic**. |
| **R12** | Tables: `id, created_at, updated_at, created_by, updated_by, is_deleted`. |
| **R13** | Pagination: `?page=1&size=20&sort=-created_at`. |
| **R14** | List envelope: `{ "data": [...], "meta": { "total", "page", "pages" } }`. |

## 2.4 Quality

| ID | Rule |
|----|------|
| **R15** | Contract test per endpoint. |
| **R16** | Pages: Loading, Error, Empty states. |
| **R17** | Error shape: `{ "error": { "code", "message", "details", "request_id" } }`. |
| **R18** | Structured JSON logs + correlation_id. |

## 2.5 Prohibitions

| ID | Rule |
|----|------|
| **R19** | No axios; only `apps/web/src/api/http.ts` fetch helper. |
| **R20** | No direct `os.getenv` in app code; use `settings` (Pydantic Settings). |
| **R21** | No manual module import lists for routers; prefer pkgutil auto-discovery. |
| **R22** | No hardcoded secrets. |
| **R23** | No `console.log` in production builds. |

---

## Enforcement checklist (PR)

- [ ] R1/R2/R19 satisfied for touched FE files
- [ ] R3 structure for new backend modules
- [ ] R8/R9/R11 for data changes
- [ ] R10 origins listed in `.env` / settings
- [ ] Gap file updated if deferred

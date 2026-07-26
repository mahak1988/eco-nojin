# Interaction protocol & acceptance checklist

Binding with Constitution (R1–R23). Active every session.

## 4. Interaction protocol

### 4.1 Before writing code
1. State **phase + item** (e.g. `Wave A / F1.3 Auth cookies`).
2. If ambiguous → ask first.
3. If architecture decision → offer 2–3 options with trade-offs.

### 4.2 Code order (mandatory for new modules)
1. Schema (Pydantic + SQLAlchemy)
2. Repository
3. Service
4. Router
5. Tests
6. Frontend: types → api → hook → page

### 4.3 After each module
1. Summary of changes
2. Run commands (migrate, test, run)
3. New dependencies called out
4. Next step proposed

### 4.4 Response format
- Full files preferred over incomplete snippets
- Path header: `# apps/farms/service.py`
- Mark changed sections when editing
- Logic comments may be Persian; identifiers English

## 5. Phase acceptance checklist

A phase is **not done** until:

- [ ] `docker compose up` clean
- [ ] `alembic upgrade head` clean
- [ ] `pytest` green with meaningful coverage (target >70% over time)
- [ ] OpenAPI → TS types generation works (`make generate-types` when target exists)
- [ ] All pages in that phase hit **real API** (or `VITE_USE_MOCK=true` only in explicit dev)
- [ ] No new `any` / `as never`
- [ ] RBAC on endpoints in scope
- [ ] Audit log where required
- [ ] Structured logging with correlation id
- [ ] Lighthouse >80 for key pages (later waves)
- [ ] Contract tests green for endpoints in scope
- [ ] fa/en UI strings complete for scope
- [ ] R4–R5 (RS256 + HttpOnly) when auth phase closes

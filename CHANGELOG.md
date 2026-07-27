# Changelog

## [Unreleased]

### 2026-07-27 — Wave A / F1.1 (R13–R14)
- `apps/shared_core/schemas/pagination.py` — ListMeta, page_to_offset, build_meta
- Education `GET /courses` accepts `page`, `size`, `sort` (legacy `skip`/`limit` still work)
- Response includes R14 `{ data, meta }` **and** legacy `{ items, total }` for FE compatibility
- FE mapper reads both shapes

### Protocol / R1
- INTERACTION_PROTOCOL, VITE_USE_MOCK, credentials include

### Foundation
- Constitution R1–R23, CORS explicit, model registry, requirements restore

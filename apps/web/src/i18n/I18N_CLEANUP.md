# i18n cleanup report (2026-08-08)

## Policy

- **UI languages in production path:** `en`, `fa`, `ar` only.
- Expandable: add `locales/{code}/` + register in `index.ts`.
- Source strings in English; translations in JSON (or eco `CONTENT` for shell pages).

## Removed (unused / scattered / incomplete vs fa)

Flat files under `apps/web/src/i18n/locales/`:

- bn, de, es, fr, hi, id, it, pt, ru, sw, tr, ur, zh-CN
- Flat duplicates: `en.json`, `fa.json`, `ar.json` (replaced by modular `locales/{lang}/`)

These were not referenced by `index.ts` and had incomplete key sets per `i18n_sync_report.md`.

## Kept / extended

| Path | Role |
|------|------|
| `locales/en\|fa\|ar/common.json` | Shared UI + nav (incl. simulators) |
| `locales/en\|fa\|ar/auth.json` | Auth forms |
| `locales/en\|fa\|ar/simulation.json` | Simulation Lab |
| `i18n/index.ts` | Catalog + `t()` + RTL |
| `components/eco/i18n.tsx` | LanguageProvider + large shell CONTENT (fa/en/ar) |

## Dual systems note

1. **JSON catalogs** (`i18n/index.ts`) — preferred for new Simulation pages.
2. **Inline CONTENT** (`components/eco/i18n.tsx`) — used by many existing pages; still fa|en|ar only.

Long-term: migrate shell keys into JSON namespaces to avoid the 160KB+ TS dictionary file.

## Root `locale/`

Contains merge/generated artifacts (`generated_fa.json`, …). Treat as tooling output; do not import in web app runtime.

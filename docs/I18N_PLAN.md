# Internationalization plan (before Phase 4)

## Hard rules (from owner)

1. **Source code, comments, API messages, docs in repo: English only.**
2. **User-visible strings: translation keys**, not hard-coded Persian/Arabic in components.
3. **Locales to support:** `en` (default), `fa` (Persian), `ar` (Arabic); more locales added via same key files.

## Architecture

```
apps/web/src/i18n/
  index.ts              # i18next (or lightweight dict) bootstrap
  locales/
    en/common.json
    en/auth.json
    en/farms.json
    en/science.json
    fa/common.json
    fa/auth.json
    ...
    ar/common.json
    ...
```

- Namespace per domain: `common`, `auth`, `farms`, `crops`, `water`, `science`, `errors`
- Key style: `auth.login.title`, `farms.list.empty`
- RTL: `fa` and `ar` set `dir=rtl` on `<html>`

## Backend

- API error `message` stays English technical code + optional `message_key` for FE translation
- Prefer: `{ "error": { "code": "FARM_NOT_FOUND", "message": "Farm not found" } }`
- FE maps `code` or `message_key` to locale strings

## Phase 4+ work items

| Step | Task |
|------|------|
| I1 | Add `apps/web` i18n bootstrap (en default) |
| I2 | Extract hard-coded UI strings to keys |
| I3 | Complete `fa` + `ar` for auth, nav, dashboard, farms, crops |
| I4 | Language switcher wired to cookie/localStorage |
| I5 | Lint rule / checklist: no Persian in `.tsx` source |

## Locales priority

1. **en** — complete first (source of truth for keys)
2. **fa** — primary market
3. **ar** — secondary
4. Other languages: copy `en/*.json` structure, translate later

## Backend DEFAULT_LOCALE

`.env`: `DEFAULT_LOCALE=en` / `SUPPORTED_LOCALES=en,fa,ar`

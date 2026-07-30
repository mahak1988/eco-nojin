# Phase A — i18n unification

**Status:** started  
**Decision:** keep **custom `useLang` + `CONTENT` + `I18N_EXTRAS`** as the single runtime source of truth.

## What is active

| Piece | Role |
|-------|------|
| `apps/web/src/components/eco/i18n.tsx` | `LanguageProvider`, `CONTENT` (fa/en/ar), `useLang` |
| `apps/web/src/components/eco/i18n_extras.ts` | Extra keys + `tr()` / `tExtra()` |
| `LanguageSwitcher` | Switches lang; sets `dir` / `lang` on `<html>` |
| `locale/source_en.json` | English catalog for MT pipeline |
| `scripts/i18n_auto_translate.py` | MT draft → `generated_fa.json` / `generated_ar.json` |
| `scripts/i18n_merge_extras.py` | Lists **missing** keys only (no overwrite) |

## What is NOT active

- **`i18next` / `react-i18next`** are listed in `package.json` but **not initialized** in the app.
  - Do not call `useTranslation` until a dedicated migration PR.
  - Optional later: migrate `CONTENT` → JSON namespaces under i18next; until then treat packages as unused deps.

## Rules (non-negotiable)

1. User-visible copy goes through `CONTENT[lang]` or `tr(CONTENT[lang], lang, key)` / `tExtra(lang, key)`.
2. Machine translations never overwrite existing keys in `i18n_extras.ts` or `CONTENT`.
3. Code identifiers and comments stay English.
4. Product languages: **fa**, **en**, **ar** only for now.

## Developer workflow

```powershell
# 1) Optional: refresh MT drafts
pip install deep-translator
python scripts\i18n_auto_translate.py --apply

# 2) See what is still missing from extras
python scripts\i18n_merge_extras.py
python scripts\i18n_merge_extras.py --print-ts

# 3) Manually paste reviewed lines into i18n_extras.ts
```

## Done in this phase slice

- Expanded `I18N_EXTRAS` (nav groups, auth fields, simulator UI, empty/loading states) for fa/en/ar.
- Added `tExtra()` helper.
- Added `scripts/i18n_merge_extras.py` + this doc.

## Next (Phase A remaining / Phase B)

- Wire Login/Register/Farms pages to `tr` / `tExtra` (remove hardcoded mixed language).
- Same for Simulators hub labels.
- Coverage test: every key in `source_en.json` exists in extras or CONTENT for all three langs.

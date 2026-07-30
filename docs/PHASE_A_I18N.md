# Phase A — i18n unification

**Status:** pages wired (Login / Register / Farms); Simulators hub already on `useLang` + `SIM_STR`

## Runtime source of truth

| Piece | Role |
|-------|------|
| `components/eco/i18n.tsx` | `LanguageProvider`, `CONTENT`, `useLang` (storage key `econojin.lang`) |
| `components/eco/i18n_extras.ts` | Extra keys + `tr` / `tExtra` |
| `components/simulators/simulatorsI18n.ts` | Simulator UI packs (fa/en/ar), driven by `useLang` |
| `src/i18n/index.ts` + JSON locales | **Legacy** — do not use for new pages (`t()` + `econojin_locale` diverges from switcher) |
| i18next packages | Installed but **not initialized** |

## Wired in this slice

- `LoginPage` + `LoginForm` → `useLang` + `tExtra` / `tr`
- `RegisterPage` → roles, fields, errors, hero in fa/en/ar
- `FarmsPage` → stopped using `../i18n` `t()`; same switcher as header
- `SimulatorsPage` → already used `SIM_STR[useLang()]` (no change required)

## Rules

1. New UI strings: add to `CONTENT` or `I18N_EXTRAS`, never hardcoded mixed language.
2. Prefer `useLang` from `eco/i18n` over `getStoredLocale` from `src/i18n`.
3. Machine translate → review → merge missing keys only (`i18n_merge_extras.py`).

## Verify

```powershell
git pull origin main
cd apps\web
pnpm dev
```

Open `/login`, `/register`, `/farms`, `/simulators` and switch fa / en / ar — chrome and body should stay in sync.

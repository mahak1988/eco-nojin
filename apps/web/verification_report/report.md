# apps/web Refactor — Verification Report

- **Root:** `D:\econojin.com\apps\web`
- **Files expected:** 42
- **Overall:** ✅ PASS
- **Summary:** 42 files expected — 0 missing, 0 errored, 0 warned, i18n parity OK

## File-by-file results

| # | File | Status | Lines | Issues / Warnings |
|---|------|--------|-------|-------------------|
| 1 | `.env.example` | ✅ ok | 13 | — |
| 2 | `INSTALL.fa.md` | ✅ ok | 58 | — |
| 3 | `tsconfig.json` | ✅ ok | 44 | — |
| 4 | `tsconfig.node.json` | ✅ ok | 17 | — |
| 5 | `postcss.config.js` | ✅ ok | 10 | — |
| 6 | `tailwind.config.js` | ✅ ok | 54 | — |
| 7 | `vite.config.ts` | ✅ ok | 30 | — |
| 8 | `src/main.tsx` | ✅ ok | 49 | — |
| 9 | `src/App.tsx` | ✅ ok | 146 | — |
| 10 | `src/i18n/index.ts` | ✅ ok | 174 | — |
| 11 | `src/i18n/locales/fa.json` | ✅ ok | 388 | — |
| 12 | `src/i18n/locales/en.json` | ✅ ok | 388 | — |
| 13 | `src/lib/utils.ts` | ✅ ok | 40 | — |
| 14 | `src/lib/i18n-utils.ts` | ✅ ok | 131 | — |
| 15 | `src/styles/index.css` | ✅ ok | 129 | — |
| 16 | `src/types/index.ts` | ✅ ok | 231 | — |
| 17 | `src/types/api.ts` | ✅ ok | 141 | — |
| 18 | `src/types/ethereum.d.ts` | ✅ ok | 64 | — |
| 19 | `src/services/authService.ts` | ✅ ok | 194 | — |
| 20 | `src/hooks/useApi.tsx` | ✅ ok | 123 | — |
| 21 | `src/hooks/useAuth.tsx` | ✅ ok | 155 | — |
| 22 | `src/hooks/useLanguage.tsx` | ✅ ok | 72 | — |
| 23 | `src/components/common/ErrorBoundary.tsx` | ✅ ok | 67 | — |
| 24 | `src/components/common/ErrorFallback.tsx` | ✅ ok | 47 | — |
| 25 | `src/components/common/LoadingSpinner.tsx` | ✅ ok | 78 | — |
| 26 | `src/components/common/PagePlaceholder.tsx` | ✅ ok | 60 | — |
| 27 | `src/components/common/LanguageSwitcher.tsx` | ✅ ok | 134 | — |
| 28 | `src/components/Layout/Header.tsx` | ✅ ok | 256 | — |
| 29 | `src/components/Layout/Sidebar.tsx` | ✅ ok | 195 | — |
| 30 | `src/components/Layout/Footer.tsx` | ✅ ok | 126 | — |
| 31 | `src/components/Layout/Layout.tsx` | ✅ ok | 41 | — |
| 32 | `src/pages/Dashboard.tsx` | ✅ ok | 149 | — |
| 33 | `src/pages/Documents.tsx` | ✅ ok | 246 | — |
| 34 | `src/pages/Login.tsx` | ✅ ok | 225 | — |
| 35 | `src/pages/Register/Register.tsx` | ✅ ok | 333 | — |
| 36 | `src/pages/Carbon/CarbonDashboard.tsx` | ✅ ok | 228 | — |
| 37 | `src/pages/Hydrology/WatershedList.tsx` | ✅ ok | 265 | — |
| 38 | `src/pages/Soil/SoilDashboard.tsx` | ✅ ok | 209 | — |
| 39 | `src/pages/AboutUs/AboutUs.tsx` | ✅ ok | 158 | — |
| 40 | `src/pages/Accounting/Accounting.tsx` | ✅ ok | 267 | — |
| 41 | `src/pages/AgricultureSchools/AgricultureSchools.tsx` | ✅ ok | 260 | — |
| 42 | `src/pages/Animations/Animations.tsx` | ✅ ok | 156 | — |

## i18n key parity (fa.json ↔ en.json)

✅ All keys match between `fa.json` and `en.json`.

## Aggregate warnings

_No warnings._

## Verdict

✅ **All 42 files are present, syntactically valid, and i18n parity holds.**

You can safely proceed to `pnpm install` and `pnpm run build`.
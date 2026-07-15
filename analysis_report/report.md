# apps/web — Code Quality Report

- **Generated:** 2026-07-11T05:57:55.437882+00:00
- **Root:** `D:\econojin.com\apps\web`
- **Total files:** 88
- **Total lines:** 2,621
- **Overall score:** **85.0/100**

## Files by extension

| Extension | Count |
|-----------|-------|
| `.tsx` | 66 |
| `.ts` | 16 |
| `.json` | 3 |
| `.js` | 2 |
| `.css` | 1 |

## Top issues (across all files)

| Issue | Occurrences |
|-------|-------------|
| `long_functions` | 294 |
| `react_inline_style` | 159 |
| `default_export` | 67 |
| `named_export` | 35 |
| `missing_return_type` | 15 |
| `use_any` | 10 |
| `console_log` | 9 |
| `any_usage` | 8 |
| `todo_comment` | 5 |
| `react_class` | 1 |
| `non_null_assertion` | 1 |

## Severity breakdown

| Severity | Files |
|----------|-------|
| critical | 0 |
| high | 0 |
| medium | 0 |
| low | 83 |
| ok | 5 |

## Worst 50 files (redesign queue)

| # | Score | Severity | Lines | File | Key issues |
|---|-------|----------|-------|------|------------|
| 1 | 75.0 | low | 27 | `src\components\common\ErrorBoundary.tsx` | default_export=1, react_class=1 |
| 2 | 77.0 | low | 8 | `src\types\ethereum.d.ts` | any_usage=4, use_any=4 |
| 3 | 77.5 | low | 137 | `src\pages\Documents.tsx` | long_functions=62, react_inline_style=17, any_usage=1 |
| 4 | 80.0 | low | 63 | `src\components\Layout\Sidebar.tsx` | long_functions=60, react_inline_style=4, default_export=1 |
| 5 | 80.0 | low | 136 | `src\pages\Login.tsx` | long_functions=63, react_inline_style=13, default_export=1 |
| 6 | 80.0 | low | 64 | `src\types\api.ts` | long_functions=57, named_export=8, use_any=2 |
| 7 | 80.0 | low | 25 | `tsconfig.json` | — |
| 8 | 80.0 | low | 10 | `tsconfig.node.json` | — |
| 9 | 83.0 | low | 89 | `src\hooks\useApi.tsx` | missing_return_type=3, console_log=2, named_export=2 |
| 10 | 83.0 | low | 89 | `src\hooks\useAuth.tsx` | missing_return_type=3, console_log=2, named_export=2 |
| 11 | 83.0 | low | 46 | `src\pages\Register\Register.tsx` | react_inline_style=10, any_usage=1, default_export=1 |
| 12 | 83.0 | low | 18 | `src\services\authService.ts` | named_export=2, any_usage=1, use_any=1 |
| 13 | 84.0 | low | 55 | `src\pages\Carbon\CarbonDashboard.tsx` | console_log=1, default_export=1, react_inline_style=1 |
| 14 | 84.0 | low | 43 | `src\pages\Hydrology\WatershedList.tsx` | console_log=1, default_export=1 |
| 15 | 84.0 | low | 55 | `src\pages\Soil\SoilDashboard.tsx` | console_log=1, default_export=1, react_inline_style=1 |
| 16 | 85.0 | low | 6 | `postcss.config.js` | default_export=1 |
| 17 | 85.0 | low | 168 | `src\App.tsx` | long_functions=52, react_inline_style=3, default_export=1 |
| 18 | 85.0 | low | 9 | `src\components\common\LoadingSpinner.tsx` | default_export=1, react_inline_style=1 |
| 19 | 85.0 | low | 11 | `src\components\Layout\Footer.tsx` | default_export=1, react_inline_style=1 |
| 20 | 85.0 | low | 38 | `src\components\Layout\Header.tsx` | react_inline_style=8, missing_return_type=1, default_export=1 |
| 21 | 85.0 | low | 10 | `src\main.tsx` | — |
| 22 | 85.0 | low | 12 | `src\pages\AboutUs\AboutUs.tsx` | default_export=1, react_inline_style=1 |
| 23 | 85.0 | low | 12 | `src\pages\Accounting\Accounting.tsx` | default_export=1, react_inline_style=1 |
| 24 | 85.0 | low | 12 | `src\pages\AgricultureSchools\AgricultureSchools.tsx` | default_export=1, react_inline_style=1 |
| 25 | 85.0 | low | 12 | `src\pages\Animations\Animations.tsx` | default_export=1, react_inline_style=1 |
| 26 | 85.0 | low | 24 | `src\pages\Biodiversity\BiodiversityDashboard.tsx` | default_export=1, react_inline_style=1 |
| 27 | 85.0 | low | 12 | `src\pages\Blog\Blog.tsx` | default_export=1, react_inline_style=1 |
| 28 | 85.0 | low | 12 | `src\pages\Careers\Careers.tsx` | default_export=1, react_inline_style=1 |
| 29 | 85.0 | low | 35 | `src\pages\ContactUs\ContactUs.tsx` | react_inline_style=8, missing_return_type=1, default_export=1 |
| 30 | 85.0 | low | 12 | `src\pages\Daneshyar\Daneshyar.tsx` | default_export=1, react_inline_style=1 |
| 31 | 85.0 | low | 64 | `src\pages\Dashboard.tsx` | react_inline_style=9, default_export=1 |
| 32 | 85.0 | low | 12 | `src\pages\DecisionYar\DecisionYar.tsx` | default_export=1, react_inline_style=1 |
| 33 | 85.0 | low | 24 | `src\pages\Drought\DroughtDashboard.tsx` | default_export=1, react_inline_style=1 |
| 34 | 85.0 | low | 12 | `src\pages\EcoCoin\Challenges.tsx` | default_export=1, react_inline_style=1 |
| 35 | 85.0 | low | 19 | `src\pages\EcoCoin\EcoCoinDashboard.tsx` | react_inline_style=2, default_export=1 |
| 36 | 85.0 | low | 12 | `src\pages\EcoCoin\Mining.tsx` | default_export=1, react_inline_style=1 |
| 37 | 85.0 | low | 12 | `src\pages\EcoCoin\Rewards.tsx` | default_export=1, react_inline_style=1 |
| 38 | 85.0 | low | 12 | `src\pages\EcoCoin\Wallet.tsx` | default_export=1, react_inline_style=1 |
| 39 | 85.0 | low | 12 | `src\pages\EconomicModels\EconomicModels.tsx` | default_export=1, react_inline_style=1 |
| 40 | 85.0 | low | 24 | `src\pages\Ecosystem\EcosystemDashboard.tsx` | default_export=1, react_inline_style=1 |
| 41 | 85.0 | low | 12 | `src\pages\EcosystemRestoration\EcosystemRestoration.tsx` | default_export=1, react_inline_style=1 |
| 42 | 85.0 | low | 24 | `src\pages\Energy\EnergyDashboard.tsx` | default_export=1, react_inline_style=1 |
| 43 | 85.0 | low | 12 | `src\pages\FAQ\FAQ.tsx` | default_export=1, react_inline_style=1 |
| 44 | 85.0 | low | 29 | `src\pages\ForgotPassword\ForgotPassword.tsx` | react_inline_style=6, missing_return_type=1, default_export=1 |
| 45 | 85.0 | low | 12 | `src\pages\GIS\FlowAccumulationAnalysis.tsx` | default_export=1, react_inline_style=1 |
| 46 | 85.0 | low | 28 | `src\pages\GIS\GISDashboard.tsx` | default_export=1, react_inline_style=1 |
| 47 | 85.0 | low | 12 | `src\pages\GIS\LandCoverAnalysis.tsx` | default_export=1, react_inline_style=1 |
| 48 | 85.0 | low | 12 | `src\pages\GIS\SlopeAnalysis.tsx` | default_export=1, react_inline_style=1 |
| 49 | 85.0 | low | 12 | `src\pages\GIS\ViewshedAnalysis.tsx` | default_export=1, react_inline_style=1 |
| 50 | 85.0 | low | 12 | `src\pages\GIS\WatershedAnalysis.tsx` | default_export=1, react_inline_style=1 |

## Fix batches (size = 25)

### Batch 1 — 25 files

- `src\components\common\ErrorBoundary.tsx`
- `src\types\ethereum.d.ts`
- `src\pages\Documents.tsx`
- `src\components\Layout\Sidebar.tsx`
- `src\pages\Login.tsx`
- `src\types\api.ts`
- `tsconfig.json`
- `tsconfig.node.json`
- `src\hooks\useApi.tsx`
- `src\hooks\useAuth.tsx`
- `src\pages\Register\Register.tsx`
- `src\services\authService.ts`
- `src\pages\Carbon\CarbonDashboard.tsx`
- `src\pages\Hydrology\WatershedList.tsx`
- `src\pages\Soil\SoilDashboard.tsx`
- `postcss.config.js`
- `src\App.tsx`
- `src\components\common\LoadingSpinner.tsx`
- `src\components\Layout\Footer.tsx`
- `src\components\Layout\Header.tsx`
- `src\main.tsx`
- `src\pages\AboutUs\AboutUs.tsx`
- `src\pages\Accounting\Accounting.tsx`
- `src\pages\AgricultureSchools\AgricultureSchools.tsx`
- `src\pages\Animations\Animations.tsx`

### Batch 2 — 25 files

- `src\pages\Biodiversity\BiodiversityDashboard.tsx`
- `src\pages\Blog\Blog.tsx`
- `src\pages\Careers\Careers.tsx`
- `src\pages\ContactUs\ContactUs.tsx`
- `src\pages\Daneshyar\Daneshyar.tsx`
- `src\pages\Dashboard.tsx`
- `src\pages\DecisionYar\DecisionYar.tsx`
- `src\pages\Drought\DroughtDashboard.tsx`
- `src\pages\EcoCoin\Challenges.tsx`
- `src\pages\EcoCoin\EcoCoinDashboard.tsx`
- `src\pages\EcoCoin\Mining.tsx`
- `src\pages\EcoCoin\Rewards.tsx`
- `src\pages\EcoCoin\Wallet.tsx`
- `src\pages\EconomicModels\EconomicModels.tsx`
- `src\pages\Ecosystem\EcosystemDashboard.tsx`
- `src\pages\EcosystemRestoration\EcosystemRestoration.tsx`
- `src\pages\Energy\EnergyDashboard.tsx`
- `src\pages\FAQ\FAQ.tsx`
- `src\pages\ForgotPassword\ForgotPassword.tsx`
- `src\pages\GIS\FlowAccumulationAnalysis.tsx`
- `src\pages\GIS\GISDashboard.tsx`
- `src\pages\GIS\LandCoverAnalysis.tsx`
- `src\pages\GIS\SlopeAnalysis.tsx`
- `src\pages\GIS\ViewshedAnalysis.tsx`
- `src\pages\GIS\WatershedAnalysis.tsx`

## Notes

- Scores are heuristic, not absolute. Use them to prioritize, not to judge.
- The `duplicate_type_export` check directly targets the TS2484 error from the last build.
- The `worst_files` list is the input for the next refactor phase: 25 files per batch.
- Paste `report.json` back to the assistant to drive the file-by-file redesign.
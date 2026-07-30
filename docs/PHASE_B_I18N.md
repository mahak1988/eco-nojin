# Phase B i18n + UI enrichment

## B4
| Page | Improvements |
|------|----------------|
| MonitoringMapPage | Sidebar coords, GPS, city presets, gradient header, i18n |
| MonitoringRulesPage | Labeled form, local rule list + severity chips, empty state |
| EducationPage | Loading/error/empty/seed/refresh via `tExtra` (fa/en/ar) |
| AccountingPage | Already uses `FIN_STR` + period/type filters + empty table |

Pack: `i18n_phase_b4.ts` → `I18N_EXTRAS`

## Verify
```powershell
git pull origin main
cd apps\web
pnpm dev
```
- `/monitoring/map`
- `/monitoring/rules`
- `/education`
- `/accounting`

# Phase B — page coverage (i18n)

## B1 wired
Crops, CropDetail, Water, ForgotPassword, VerifyOtp

## B2 wired
| Route | File |
|-------|------|
| `/farms/:id` | FarmDetailPage |
| `/farms/new` | FarmNewPage |
| `/weather` | WeatherPage |
| `/monitoring` | MonitoringHubPage |
| (keys ready) | FarmWizard, Planting, Tasks, Inventory — packs in `i18n_phase_b2.ts` |

Packs: `i18n_phase_b.ts`, `i18n_phase_b2.ts` → merged in `i18n_extras.ts`.

## Remaining
- Full string pass on FarmWizard / Planting / Tasks / Inventory forms (labels)
- Monitoring sub-pages (soil, map, alerts, rules)
- Account security / notifications, Accounting body

## Verify
```powershell
git pull origin main
cd apps\web
pnpm dev
```
Switch fa/en/ar on `/farms`, `/crops`, `/water`, `/weather`, `/monitoring`.

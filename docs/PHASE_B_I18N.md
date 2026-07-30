# Phase B — page coverage (i18n)

## Wired

| Route | File | Notes |
|-------|------|--------|
| `/crops` | `CropsPage.tsx` | left legacy `t()` |
| `/crops/:id` | `CropDetailPage.tsx` | section labels |
| `/water` | `WaterPage.tsx` | KPI labels |
| `/forgot-password` | `ForgotPasswordPage.tsx` | + LanguageSwitcher |
| `/verify-otp` | `VerifyOtpPage.tsx` | + LanguageSwitcher |

Strings live in `i18n_phase_b.ts`, merged into `I18N_EXTRAS`.

## Still on legacy / hardcoded (next slices)

- Farm detail / wizard / new
- Planting, tasks, inventory, weather pages
- Monitoring hub family
- Accounting / education bodies
- Account security / notifications

## Verify

```powershell
git pull origin main
cd apps\web
pnpm dev
```

Switch fa/en/ar on `/crops`, `/water`, `/forgot-password`, `/verify-otp`.

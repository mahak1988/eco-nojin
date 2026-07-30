# Phase B i18n + UI

## B3 (this slice)
- `MonitoringSoilPage` — layer cards, progress bars, wet/ok/dry, i18n
- `MonitoringAlertsPage` — severity filter chips, empty state, card list
- `AccountSecurityPage` — password form, sessions, 2FA placeholder
- `AccountNotificationsPage` — preference toggles + list
- Pack: `i18n_phase_b3.ts` merged in `i18n_extras.ts`

## Verify
```powershell
git pull origin main
cd apps\web
pnpm dev
```
Routes: `/monitoring/soil`, `/monitoring/alerts`, `/account/security`, `/account/notifications`

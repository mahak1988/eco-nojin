# Header menu + simulator i18n (fa / en / ar)

## Menu jump fix
- **Before:** CSS `group-hover` — menu closed when pointer crossed the gap.
- **After:** click toggle + outside click + Escape; closes on route change.
- Mobile: full group list under More, not only main nav.

## Simulator localization
- Backend: `apps/simulation/i18n_catalog.py` + `?lang=fa|en|ar` on `/api/v1/simulation/simulators`.
- Frontend: `fetchSimulators(lang)` passes current UI language; badge strings use `SIM_STR`.

## Pull
```powershell
cd D:\econojin.com
git pull origin main
cd apps\web
pnpm dev
```
Test: open More menu → stays open until click outside; switch language → header + /simulators labels follow.

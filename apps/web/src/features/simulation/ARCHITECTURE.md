# Simulation frontend architecture

## Languages (R1-compatible, expandable)

| Code | Name | Dir | Packs |
|------|------|-----|-------|
| `en` | English | LTR | `locales/en/{common,auth,simulation}.json` |
| `fa` | فارسی | RTL | `locales/fa/...` |
| `ar` | العربية | RTL | `locales/ar/...` |

- Catalog: `apps/web/src/i18n/index.ts` (`t("simulation.hubTitle")`).
- UI shell also uses `components/eco/i18n.tsx` (`LanguageProvider`, `Lang = fa|en|ar`).
- **Do not** add flat multi-language JSONs (bn/de/…) — removed in cleanup.
- To add a language: copy `locales/en` → `locales/{code}`, translate, extend `Locale` + `catalogs`.

## Pages

```
pages/simulation/
  SimulationHubPage.tsx     # catalog of models
  RichardsPinPage.tsx       # planned
  SebsEtPage.tsx            # planned
  DayCentPage.tsx           # planned
  UncertaintyPage.tsx       # planned
  …
features/simulation/
  api/client.ts             # run + status (+ mock)
  components/               # ParamForm, MetricCards, ResultChart (next)
  hooks/                    # useSimulationRun (next)
```

## Routes (wire in App.tsx)

```
/simulation              → SimulationHubPage
/simulation/richards
/simulation/sebs
/simulation/daycent
/simulation/uncertainty
…
```

## API

- `POST /api/v1/simulation/run` body `{ model, params }`
- `GET /api/v1/simulation/runs/:id`
- Mock when `VITE_USE_MOCK=true`

## Next steps

1. Register routes in `App.tsx` under RequireAuth layout.
2. Build ParamForm + MetricCards + simple charts.
3. Backend expose unified simulation router if not already.

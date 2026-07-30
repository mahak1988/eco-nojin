# External keys checklist (owner registers; paste into local .env only)

| # | Service | Env vars | When needed | Cost |
|---|---------|----------|-------------|------|
| 1 | **None for local core** | SQLite + Open-Meteo + synthetic EO | Phase 1-4 | Free |
| 2 | OpenWeatherMap | `OPENWEATHER_API_KEY` | Better weather proxy | Free tier |
| 3 | Google Earth Engine | `GEE_*` + `secrets/gee-sa.json` | Live NDVI | Free community |
| 4 | Copernicus Data Space | `COPERNICUS_USERNAME/PASSWORD` | Sentinel download | Free |
| 5 | Sentinel Hub | `SENTINEL_HUB_*` | WMS tiles | Trial |
| 6 | Sentry | `SENTRY_DSN` | Prod errors | Free tier |
| 7 | Groq / OpenAI / Gemini | `LLM_API_KEY` + `LLM_PROVIDER` | Real AI agents | Paid/free tiers |
| 8 | RS256 keys | openssl PEMs | Production auth | Free |
| 9 | Postgres cloud (Neon etc.) | `DATABASE_URL` | Prod DB | Free tier |

**Do not send real keys in chat or commit them.**

After Phase 10: fill `.env`, restart API, re-test satellite/science endpoints.

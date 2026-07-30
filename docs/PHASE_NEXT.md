# Next steps

## Done recently
- Header More menu: click-stable (no hover jump)
- Simulator list: `?lang=fa|en|ar` on API + FE badge i18n
- Auto-translate toolkit: `scripts/i18n_auto_translate.py` + `locale/source_en.json`

## Recommended next
1. `pip install deep-translator` then `python scripts/i18n_auto_translate.py --apply`
2. Review `locale/generated_*.json` and merge into UI catalogs
3. Expand `apps/simulation/i18n_catalog.py` for remaining simulator IDs
4. Wire remaining FE pages (Science, Accounting, …) to `useLang` / `tr()`
5. Phase 5+: RS256 cookies when keys are ready in `.env`

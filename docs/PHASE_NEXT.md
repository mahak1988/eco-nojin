# Next steps

## Phase A (i18n) — in progress
- Single runtime source: `useLang` + `CONTENT` + `I18N_EXTRAS` (not i18next)
- Expanded extras + `scripts/i18n_merge_extras.py`
- See `docs/PHASE_A_I18N.md`

## Immediate follow-up
1. `git pull` then hard-refresh FE (`pnpm dev`)
2. `python scripts/i18n_merge_extras.py` on machine with `generated_*.json`
3. Wire Login / Register / Farms to `tExtra` / `tr`
4. Phase B: page coverage

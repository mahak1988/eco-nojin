# Automatic translation tools (Econojin)

## Recommended stack (no Docker required)

| Tool | Cost | Needs key? | Iran-friendly | Use for |
|------|------|------------|---------------|---------|
| **deep-translator + MyMemory** | Free | No | Often yes | Bulk UI strings |
| **deep-translator + Google** | Free | No | Often blocked | Fallback |
| **LibreTranslate** (self-host) | Free | No | Yes if self-hosted | Offline / privacy |
| **Argos Translate** | Free | No | Yes (offline models) | Fully offline |
| **DeepL / Google Cloud** | Paid tiers | Yes | Variable | Production QA |

This repo ships a **zero-key** script using MyMemory then Google via `deep-translator`.

## Install

```powershell
cd D:\econojin.com
.\.venv\Scripts\Activate.ps1
pip install deep-translator
```

## Run

```powershell
# Sample (5 keys)
python scripts\i18n_auto_translate.py --dry-run

# Full source_en.json -> generated_fa.json + generated_ar.json
python scripts\i18n_auto_translate.py --apply
```

Outputs:

- `locale/source_en.json` — **English source of truth** (edit this)
- `locale/generated_fa.json` — machine FA
- `locale/generated_ar.json` — machine AR
- `locale/report.md` — failures

## Workflow (mandatory review)

1. Add new English keys only to `locale/source_en.json`.
2. Run `--apply`.
3. **Human-review** navigation, legal, science, and farm terms.
4. Copy approved strings into:
   - `apps/web/src/components/eco/i18n.tsx` / `i18n_extras.ts`
   - `apps/web/src/components/simulators/simulatorsI18n.ts`
   - `apps/simulation/i18n_catalog.py`
5. Never ship raw MT for contracts, safety alerts, or chemical units without review.

## Optional: LibreTranslate (self-host later)

When network allows Docker or a remote LT instance:

```text
LIBRETRANSLATE_URL=https://your-lt.example/translate
```

Extend `scripts/i18n_auto_translate.py` to POST `{"q","source","target"}` to that URL as engine #0.

## Optional: Argos offline

```powershell
pip install argostranslate
# install language packs via argospm (large download)
```

Best when Google/MyMemory are unreachable.

## Policy for Econojin

- **Code comments and identifiers:** English only.
- **User-visible UI:** en / fa / ar packs, keys stable in English.
- **Auto-translate:** draft only; product strings need review.
- **Simulators:** prefer curated entries in `i18n_catalog.py` for scientific names.

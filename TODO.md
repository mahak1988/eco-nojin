# TODO: Centralized i18n Dictionary Consolidation

## ✅ Step 1: Analyze and Plan [DONE]
- Scanned all scattered i18n files (18 module files + 1 legacy eco/i18n.tsx)
- Identified all missing keys across modules
- Understood current architecture (2 systems: component-level CONTENT + i18next JSON)

## ✅ Step 2: Create Comprehensive Centralized Dictionary [IN PROGRESS]
- [x] Add ALL module sections to FA in `apps/web/src/i18n/i18n.tsx`:
  - `account`, `analytics`, `community`, `ecocoin`, `education`, `finance`
  - `games`, `invoices`, `journal`, `library`, `mrv`, `news`, `notFound`
  - `payments`, `pilots`, `policies`, `regional`
  - `home` (from eco/i18n.tsx HomePage keys)
  - `nav` (from eco/i18n.tsx navigation keys)
  - Expand `dashboard` (add dash_* keys from eco/i18n.tsx)
- [x] Complete EN mirroring FA exactly
- [x] Complete AR mirroring FA exactly
- [x] Add 12 remaining languages (ur, ru, hi, bn, id, zh-CN, fr, de, tr, es, pt, it) as EN copies
- [x] Ensure `ContentStrings = typeof FA` TypeScript strictness

## 🔲 Step 3: Update Component-Level i18n Files
- [ ] Update `components/eco/i18n.tsx` to re-export from centralized dict
- [ ] Ensure all component imports still work

## 🔲 Step 4: Sync JSON Locale Files
- [ ] Update `apps/web/src/i18n/locales/*.json` to match centralized dict keys
- [ ] Verify i18next integration works

## 🔲 Step 5: Verify TypeScript
- [ ] Run `tsc --noEmit` to check for type errors
- [ ] Fix any type mismatches


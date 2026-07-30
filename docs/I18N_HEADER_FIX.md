# i18n Header/Footer fix

## Problem
`components/Layout/Layout.tsx` imported **legacy** `components/Header.tsx` and `components/Footer.tsx` which had **hardcoded Persian** nav/footer strings and `dir="rtl"` always.

`HomePage` correctly used `CONTENT[lang]` from `components/eco/i18n.tsx`.

Result: switching language (or browser EN) → body English, chrome still Persian.

## Fix
1. Layout uses `./Header` and `./Footer` (CONTENT-driven).
2. `dir` from `getLanguageDir(lang)` — not forced RTL.
3. Legacy `components/Header.tsx` / `Footer.tsx` re-export Layout versions.
4. LanguageSwitcher on header; auth buttons translated.
5. Satellite/Weather panels use CONTENT strings.

## Pull & verify
```powershell
cd D:\econojin.com
git pull origin main
cd apps\web
Remove-Item -Recurse -Force node_modules\.vite -ErrorAction SilentlyContinue
pnpm dev
```
Open http://localhost:5173 — switch FA / EN / AR; header, footer, and home must all match.

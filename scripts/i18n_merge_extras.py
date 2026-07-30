#!/usr/bin/env python3
"""
Phase A — merge machine translations into i18n_extras WITHOUT overwriting humans.

Reads:
  locale/generated_fa.json
  locale/generated_ar.json
  locale/source_en.json
  apps/web/src/components/eco/i18n_extras.ts  (parses key lists loosely)

Writes (optional):
  locale/merge_candidates.json   — only keys missing from extras for each lang
  locale/merge_report.md

Does NOT auto-edit the .ts file (safe). Print suggested snippets for review.

Usage:
  python scripts/i18n_merge_extras.py
  python scripts/i18n_merge_extras.py --print-ts
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"
EXTRAS_TS = ROOT / "apps" / "web" / "src" / "components" / "eco" / "i18n_extras.ts"


def load_json(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}


def keys_in_extras_ts(text: str) -> set[str]:
    """Collect string keys under fa/en/ar blocks (best-effort)."""
    return set(re.findall(r"^\s{4}([a-z][a-z0-9_]*):\s*\"", text, flags=re.M))


def _bullet_keys(keys: list[str]) -> list[str]:
    if not keys:
        return ["- none"]
    return [f"- `{k}`" for k in keys]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--print-ts", action="store_true", help="Print TS snippets for missing keys")
    args = parser.parse_args()

    en = load_json(LOCALE / "source_en.json")
    fa = load_json(LOCALE / "generated_fa.json")
    ar = load_json(LOCALE / "generated_ar.json")

    existing: set[str] = set()
    if EXTRAS_TS.exists():
        existing = keys_in_extras_ts(EXTRAS_TS.read_text(encoding="utf-8"))

    # Keys present in EN source but not in extras file
    missing = sorted(k for k in en if k not in existing)

    candidates = {
        "en": {k: en[k] for k in missing},
        "fa": {k: fa.get(k, en[k]) for k in missing},
        "ar": {k: ar.get(k, en[k]) for k in missing},
    }

    LOCALE.mkdir(parents=True, exist_ok=True)
    out = LOCALE / "merge_candidates.json"
    out.write_text(json.dumps(candidates, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report_lines = [
        "# i18n merge report (Phase A)",
        "",
        f"- Keys in source_en: {len(en)}",
        f"- Keys detected in i18n_extras.ts: {len(existing)}",
        f"- Missing (candidates): {len(missing)}",
        f"- generated_fa loaded: {bool(fa)}",
        f"- generated_ar loaded: {bool(ar)}",
        "",
        "## Missing keys",
        *_bullet_keys(missing),
        "",
        "Policy: do not overwrite human-curated extras. Review merge_candidates.json then paste.",
        "",
    ]
    (LOCALE / "merge_report.md").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Missing keys: {len(missing)}")

    if args.print_ts and missing:
        print("\n// --- suggested fa entries ---")
        for k in missing:
            val = candidates["fa"][k].replace("\\", "\\\\").replace('"', '\\"')
            print(f'    {k}: "{val}",')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Econojin i18n auto-translate
============================
Translate English UI strings to fa / ar using free engines (no API key required).

Engines (tried in order):
  1. MyMemoryTranslator  — free, often works in restricted networks
  2. GoogleTranslator    — via deep-translator (may be blocked in some regions)

Usage (from repo root, with venv active):

  pip install deep-translator
  python scripts/i18n_auto_translate.py --dry-run
  python scripts/i18n_auto_translate.py --apply

Inputs (English source of truth):
  locale/source_en.json   — flat key -> English string

Outputs:
  locale/generated_fa.json
  locale/generated_ar.json
  locale/report.md        — coverage + failures

Review generated_* before merging into apps/web or apps/simulation catalogs.
Never commit machine translation without a human pass for product UI.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALE = ROOT / "locale"
SOURCE = LOCALE / "source_en.json"
OUT_FA = LOCALE / "generated_fa.json"
OUT_AR = LOCALE / "generated_ar.json"
REPORT = LOCALE / "report.md"

# Prefer MyMemory first (often reachable); Google as fallback.
ENGINE_ORDER = ("mymemory", "google")


def _translate_one(text: str, target: str, engine: str) -> str:
    from deep_translator import GoogleTranslator, MyMemoryTranslator

    if not text or not text.strip():
        return text
    # Skip pure codes / units
    if text in {"NDVI", "MRV", "CO2", "ppm", "MW", "mm", "°C", "%", "٪"}:
        return text
    if engine == "mymemory":
        # MyMemory uses codes like en-US / fa-IR
        src, tgt = "en-US", {"fa": "fa-IR", "ar": "ar-SA"}.get(target, target)
        return MyMemoryTranslator(source=src, target=tgt).translate(text)
    return GoogleTranslator(source="en", target=target).translate(text)


def translate_batch(
    items: dict[str, str],
    target: str,
    *,
    sleep_s: float = 0.35,
) -> tuple[dict[str, str], list[str]]:
    out: dict[str, str] = {}
    errors: list[str] = []
    for key, en in items.items():
        translated = None
        last_err = ""
        for engine in ENGINE_ORDER:
            try:
                translated = _translate_one(en, target, engine)
                if translated:
                    break
            except Exception as e:  # noqa: BLE001 — report per key
                last_err = f"{engine}: {e}"
                time.sleep(sleep_s)
        if translated:
            out[key] = translated
        else:
            out[key] = en  # fallback: keep English
            errors.append(f"{key}: {last_err or 'empty'}")
        time.sleep(sleep_s)
    return out, errors


def ensure_source() -> dict[str, str]:
    """Create a starter English catalog if missing."""
    LOCALE.mkdir(parents=True, exist_ok=True)
    if SOURCE.exists():
        data = json.loads(SOURCE.read_text(encoding="utf-8"))
        return {str(k): str(v) for k, v in data.items() if isinstance(v, str)}

    starter = {
        "nav_farms": "Farms",
        "nav_dashboard": "Dashboard",
        "nav_simulators": "Simulators",
        "nav_satellite": "Satellite",
        "nav_education": "Education",
        "nav_mrv": "MRV",
        "auth_signin": "Sign in",
        "auth_register": "Register",
        "footer_rights": "All rights reserved.",
        "sim_title": "Simulators",
        "sim_subtitle": "Climate, water, agriculture and energy models",
        "sim_run": "Run",
        "sim_stop": "Stop",
        "sim_reset": "Reset",
        "sim_export": "Export CSV",
        "sim_backend_online": "simulators (server)",
        "sim_backend_offline": "Local mode",
        "sim_climate_name": "Climate Model",
        "sim_climate_desc": "Temperature, precipitation, extremes and NDVI from CO2 and climate sensitivity.",
        "sim_aquacrop_name": "AquaCrop",
        "sim_aquacrop_desc": "FAO crop-water productivity model (process approximation).",
        "sim_rothc_name": "RothC",
        "sim_rothc_desc": "Soil organic carbon turnover (RothC-26.3 style).",
        "sim_swat_name": "SWAT+",
        "sim_swat_desc": "Basin hydrology and sediment proxy (not official SWAT binary).",
        "sim_dssat_name": "DSSAT",
        "sim_dssat_desc": "Crop growth decision support (simplified).",
    }
    SOURCE.write_text(json.dumps(starter, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Created starter source: {SOURCE}")
    return starter


def _bullet_lines(errors: list[str]) -> list[str]:
    if not errors:
        return ["- none"]
    return [f"- {e}" for e in errors]


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-translate EN -> FA/AR for Econojin")
    parser.add_argument("--apply", action="store_true", help="Write generated_fa/ar.json")
    parser.add_argument("--dry-run", action="store_true", help="Translate only first 5 keys")
    parser.add_argument("--sleep", type=float, default=0.35, help="Delay between requests")
    args = parser.parse_args()

    try:
        import deep_translator  # noqa: F401
    except ImportError:
        print("Install: pip install deep-translator", file=sys.stderr)
        return 2

    source = ensure_source()
    keys = list(source.items())
    if args.dry_run:
        keys = keys[:5]
        print(f"Dry-run: {len(keys)} keys")

    batch = dict(keys)
    print(f"Translating {len(batch)} keys -> fa, ar ...")
    fa, err_fa = translate_batch(batch, "fa", sleep_s=args.sleep)
    ar, err_ar = translate_batch(batch, "ar", sleep_s=args.sleep)

    report_lines = [
        "# i18n auto-translate report",
        "",
        f"- Source keys: {len(source)}",
        f"- Processed: {len(batch)}",
        f"- FA failures: {len(err_fa)}",
        f"- AR failures: {len(err_ar)}",
        "",
        "## Failures (FA)",
        *_bullet_lines(err_fa),
        "",
        "## Failures (AR)",
        *_bullet_lines(err_ar),
        "",
        "## Next steps",
        "1. Review `locale/generated_fa.json` and `locale/generated_ar.json`",
        "2. Copy approved strings into `apps/web/.../i18n` and `apps/simulation/i18n_catalog.py`",
        "3. Prefer human edit for navigation, legal, and science labels",
        "",
    ]
    REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report: {REPORT}")

    if args.apply or args.dry_run:
        OUT_FA.write_text(json.dumps(fa, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        OUT_AR.write_text(json.dumps(ar, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {OUT_FA}")
        print(f"Wrote {OUT_AR}")
    else:
        print("Pass --apply to write JSON files (or --dry-run for a sample).")

    return 0 if not err_fa and not err_ar else 1


if __name__ == "__main__":
    raise SystemExit(main())

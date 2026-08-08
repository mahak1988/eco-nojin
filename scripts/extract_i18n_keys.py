#!/usr/bin/env python3
"""
extract_i18n_keys.py — Phase P0, Step 2
=========================================
Scans frontend source files (TSX/TS/JSX) for hard-coded Persian/RTL strings
and generates/updates i18n JSON locale files.

Usage:
    python scripts/extract_i18n_keys.py              # scan & report only
    python scripts/extract_i18n_keys.py --apply       # update locale files

Output:
    - reports/i18n_extraction_report.json
    - src/i18n/locales/en.json  (updated)
    - src/i18n/locales/fa.json  (updated)
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS: set[str] = {
    ".git",
    ".github",
    ".venv",
    ".turbo",
    ".pnpm-store",
    "node_modules",
    "dist",
    "build",
    ".next",
    "__pycache__",
}

FRONTEND_DIRS: list[Path] = [
    ROOT / "apps" / "web" / "src",
    ROOT / "packages" / "features" / "src",
    ROOT / "packages" / "ui" / "src",
    ROOT / "packages" / "hooks" / "src",
    ROOT / "packages" / "lib" / "src",
    ROOT / "packages" / "api-client" / "src",
    ROOT / "src",
]

LOCALE_DIR = ROOT / "src" / "i18n" / "locales"
EN_PATH = LOCALE_DIR / "en.json"
FA_PATH = LOCALE_DIR / "fa.json"

RTL_RE = re.compile("[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]")

# ---------------------------------------------------------------------------
# Key generation
# ---------------------------------------------------------------------------

_KEY_COUNTER: dict[str, int] = defaultdict(int)


def _make_key(file_rel: str, text: str) -> str:
    """Generate a unique i18n key from file path and text content."""
    # Extract module name from path
    parts = file_rel.replace("\\", "/").split("/")
    module = parts[0] if len(parts) > 0 else "unknown"
    if module in {"apps", "packages"} and len(parts) > 2:
        module = parts[2]  # e.g. web, features, ui

    # Create a slug from the first few words of the text
    words = re.findall(r"[a-zA-Z\u0600-\u06FF]+", text.lower())
    slug = "_".join(words[:4]) if words else "unknown"
    slug = re.sub(r"[^a-z0-9_]", "", slug)[:60]

    # Ensure uniqueness
    counter = _KEY_COUNTER[slug]
    _KEY_COUNTER[slug] += 1
    if counter > 0:
        slug = f"{slug}_{counter}"

    return f"{module}.{slug}"


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


class ExtractedString(NamedTuple):
    file: str
    line: int
    text: str
    key: str


def scan_frontend_files() -> list[ExtractedString]:
    """Scan frontend directories for hard-coded Persian strings."""
    results: list[ExtractedString] = []

    for scan_dir in FRONTEND_DIRS:
        if not scan_dir.exists():
            continue
        for root_str, dirs, files in os.walk(scan_dir):
            root = Path(root_str)
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for fname in files:
                if not fname.endswith((".tsx", ".ts", ".jsx", ".js")):
                    continue
                fpath = root / fname
                try:
                    text = fpath.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue

                rel = str(fpath.relative_to(ROOT)).replace("\\", "/")
                lines = text.split("\n")

                # Find quoted strings containing RTL text
                for i, line in enumerate(lines):
                    for m in re.finditer(r"""["'`]([^"'`]{4,})["'`]""", line):
                        content = m.group(1)
                        if RTL_RE.search(content):
                            key = _make_key(rel, content)
                            results.append(
                                ExtractedString(
                                    file=rel,
                                    line=i,
                                    text=content.strip(),
                                    key=key,
                                )
                            )
    return results


# ---------------------------------------------------------------------------
# Locale file management
# ---------------------------------------------------------------------------


def _load_locale(path: Path) -> dict[str, str]:
    """Load a JSON locale file, return empty dict if missing."""
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print(f"  [WARN] Could not parse {path}, starting fresh.", file=sys.stderr)
        return {}


def _save_locale(path: Path, data: dict[str, str]) -> None:
    """Save locale data as pretty-printed JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def update_locale_files(
    extracted: list[ExtractedString], apply: bool = False
) -> dict[str, list[dict]]:
    """Update en.json and fa.json with extracted strings."""
    en_data = _load_locale(EN_PATH)
    fa_data = _load_locale(FA_PATH)

    report: dict[str, list[dict]] = defaultdict(list)
    new_keys = 0
    existing_keys = 0

    for item in extracted:
        entry = {
            "key": item.key,
            "file": item.file,
            "line": item.line + 1,
            "persian_text": item.text,
        }

        if item.key in en_data:
            entry["status"] = "already_exists"
            existing_keys += 1
        else:
            entry["status"] = "new"
            new_keys += 1
            if apply:
                # English translation placeholder (same as Persian for now)
                en_data[item.key] = item.text
                fa_data[item.key] = item.text

        report[item.file].append(entry)

    if apply:
        _save_locale(EN_PATH, dict(sorted(en_data.items())))
        _save_locale(FA_PATH, dict(sorted(fa_data.items())))
        print(f"\n  Updated {EN_PATH.name} and {FA_PATH.name}", file=sys.stderr)

    print(f"  New keys: {new_keys}, Existing: {existing_keys}", file=sys.stderr)
    return dict(report)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_report(report: dict[str, list[dict]], path: Path) -> None:
    output = {
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "generator": "extract_i18n_keys.py",
        "total_files": len(report),
        "total_strings": sum(len(v) for v in report.values()),
        "files": report,
    }
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Extract i18n keys from frontend source")
    parser.add_argument("--apply", action="store_true", help="Actually update locale files")
    args = parser.parse_args()

    print("=" * 60, file=sys.stderr)
    print("  i18n Key Extractor - Phase P0 / Step 2", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    extracted = scan_frontend_files()
    print(f"\nFound {len(extracted)} hard-coded Persian strings in frontend.", file=sys.stderr)

    report = update_locale_files(extracted, apply=args.apply)

    out_dir = ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    write_report(report, out_dir / "i18n_extraction_report.json")

    if not args.apply:
        print("\n[DRY RUN] Use --apply to update locale files.", file=sys.stderr)

    print("\nDone.", file=sys.stderr)


if __name__ == "__main__":
    main()

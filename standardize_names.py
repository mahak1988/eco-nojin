#!/usr/bin/env python3
"""
Eco Nojin — Phase 2.3: Standardize Package Naming (Simple & Safe)
===================================================================
Renames: "hydrology-frontend" → "@econojin/web"

TEXT-BASED find-and-replace (no JSON/YAML dump).
Preserves all formatting, comments, and indentation.

What it scans:
  • apps/ directory (all subdirectories)
  • Root config files (package.json, turbo.json, pnpm-workspace.yaml)
  • .github/workflows/ (CI/CD files)

Safety:
  - Dry-run by default (no files modified)
  - --apply to execute
  - Only replaces exact string "hydrology-frontend"

Usage:
    python standardize_names.py                    # dry-run
    python standardize_names.py --apply            # execute
    python standardize_names.py --root D:\\path    # custom root
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

OLD_NAME = "hydrology-frontend"
NEW_NAME = "@econojin/web"

SCAN_EXTENSIONS = {".json", ".yaml", ".yml", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}
SKIP_DIRS = {
    "node_modules", ".git", ".pnpm-store", ".turbo", ".next", ".nuxt",
    "__pycache__", ".venv", ".venv-1", "venv", "dist", "build", ".output",
    ".svelte-kit", "target", ".cache", "coverage", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".idea", ".vscode",
}


def is_skip_dir(name: str) -> bool:
    if name in SKIP_DIRS:
        return True
    if re.match(r'^(?:\.)?venv-\d+', name, re.IGNORECASE):
        return True
    return False


def scan_and_replace(root: Path, apply: bool, verbose: bool) -> tuple[int, int, int]:
    """Scan files and optionally replace.

    Returns (files_scanned, files_modified, total_replacements).
    """
    files_scanned = 0
    files_modified = 0
    total_replacements = 0

    # Target directories: apps/, .github/workflows/, and root config files
    target_paths = [
        root / "apps",
        root / ".github" / "workflows",
    ]

    # Also scan root config files
    root_config_files = [
        root / "package.json",
        root / "turbo.json",
        root / "pnpm-workspace.yaml",
    ]

    all_files: list[Path] = []

    # Collect files from target directories
    for target in target_paths:
        if not target.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(target):
            dirnames[:] = [d for d in dirnames if not is_skip_dir(d)]
            for fname in filenames:
                fpath = Path(dirpath) / fname
                if fpath.suffix.lower() in SCAN_EXTENSIONS:
                    all_files.append(fpath)

    # Add root config files
    for cfg in root_config_files:
        if cfg.exists() and cfg.is_file():
            all_files.append(cfg)

    # Scan and replace
    print(f"  Scanning {len(all_files)} files for '{OLD_NAME}'...")
    print()

    files_with_matches: list[tuple[Path, int, list]] = []

    for fpath in all_files:
        files_scanned += 1
        try:
            text = fpath.read_text(encoding="utf-8-sig", errors="ignore")
        except OSError:
            continue

        if OLD_NAME not in text:
            continue

        count = text.count(OLD_NAME)
        rel = str(fpath.relative_to(root)).replace("\\", "/")

        # Collect sample lines for display
        samples = []
        for i, line in enumerate(text.splitlines(), 1):
            if OLD_NAME in line and len(samples) < 3:
                samples.append((i, line.strip()[:80]))

        files_with_matches.append((fpath, count, samples))

        if apply:
            new_text = text.replace(OLD_NAME, NEW_NAME)
            try:
                fpath.write_text(new_text, encoding="utf-8")
                files_modified += 1
                total_replacements += count
                print(f"  ✓ {rel}: {count} replacement(s)")
            except OSError as e:
                print(f"  ✗ {rel}: {e}")
        else:
            total_replacements += count
            if verbose:
                print(f"  • {rel}: {count} match(es)")
                for line_num, line_text in samples:
                    print(f"      L{line_num}: {line_text}")

    if not apply:
        # Show summary in dry-run
        for fpath, count, samples in files_with_matches:
            rel = str(fpath.relative_to(root)).replace("\\", "/")
            print(f"  • {rel}: {count} match(es)")
            if verbose:
                for line_num, line_text in samples:
                    print(f"      L{line_num}: {line_text}")

    return (files_scanned, files_modified, total_replacements)


def main():
    parser = argparse.ArgumentParser(
        description=f"Rename '{OLD_NAME}' → '{NEW_NAME}' (text-based, safe).",
    )
    parser.add_argument("--root", type=str, default=".", help="Repo root (default: cwd)")
    parser.add_argument("--apply", action="store_true", help="Actually modify files (default: dry-run)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show matching lines")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"Error: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    mode = "APPLY" if args.apply else "DRY-RUN (pass --apply to execute)"
    print("=" * 70)
    print(f"  Eco Nojin — Phase 2.3: Standardize Package Naming")
    print(f"  Mode: {mode}")
    print(f"  Root: {root}")
    print(f"  Rename: '{OLD_NAME}' → '{NEW_NAME}'")
    print(f"  Scan: apps/, .github/workflows/, root configs")
    print("=" * 70)
    print()

    files_scanned, files_modified, total_replacements = scan_and_replace(
        root, args.apply, args.verbose
    )

    print()
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Files scanned      : {files_scanned}")
    print(f"  Files {'modified' if args.apply else 'with matches'}: {files_modified if args.apply else 'see above'}")
    print(f"  Total replacements : {total_replacements}")

    if not args.apply and total_replacements > 0:
        print()
        print(f"  ⚠ DRY-RUN. To apply:")
        print(f"     python standardize_names.py --apply")
    elif args.apply and files_modified > 0:
        print()
        print("  ✅ Done! Next steps:")
        print(f"     1. pnpm install  (update lockfile)")
        print(f"     2. pnpm --filter {NEW_NAME} -- list  (verify rename)")
        print(f"     3. git add apps/web/package.json pnpm-lock.yaml")
        print(f"     4. git commit -m \"refactor(naming): rename {OLD_NAME} to {NEW_NAME}\"")
    elif args.apply and files_modified == 0:
        print()
        print("  ℹ  No files needed modification (already renamed or no matches).")
    print()


if __name__ == "__main__":
    sys.exit(0 if main() is None else 0)

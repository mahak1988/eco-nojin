#!/usr/bin/env python3
"""
Eco Nojin — Phase 2.3: Standardize Package Naming
===================================================
Renames the inconsistently-named frontend package:
  "hydrology-frontend" → "@econojin/web"

This is a TEXT-BASED find-and-replace (no YAML/JSON dump).
Preserves all formatting, comments, and indentation.

What it changes:
  1. apps/web/package.json: "name": "hydrology-frontend" → "@econojin/web"
  2. Any package.json that references "hydrology-frontend" in dependencies
  3. turbo.json / pnpm-workspace.yaml if they reference the old name
  4. CI/CD workflows that filter by package name (e.g., pnpm --filter hydrology-frontend)
  5. Any .ts/.tsx/.js source files that import from "hydrology-frontend"

Safety:
  - Dry-run by default (no files modified)
  - --apply to execute
  - Only replaces exact string "hydrology-frontend" (not partial matches)
  - Generates a report of every file changed + line numbers

Usage:
    python3 standardize_names.py --root D:\\econojin.com
    python3 standardize_names.py --root D:\\econojin.com --apply
    python3 standardize_names.py --root D:\\econojin.com --verbose
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════

OLD_NAME = "hydrology-frontend"
NEW_NAME = "@econojin/web"

# File extensions to scan for references (text-based, safe)
SCAN_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".ts", ".tsx", ".js", ".jsx",
    ".mjs", ".cjs", ".md", ".txt", ".sh", ".ps1", ".bat",
    ".toml", ".cfg", ".ini", ".env", ".config.js", ".config.ts",
}

# Directories to skip (generated, cache, dependencies)
SKIP_DIRS = {
    "node_modules", ".git", ".pnpm-store", ".turbo", ".next", ".nuxt",
    "__pycache__", ".venv", ".venv-1", "venv", "dist", "build",
    ".output", ".svelte-kit", "target", ".cache", "coverage",
    ".pytest_cache", ".mypy_cache", ".ruff_cache", ".idea", ".vscode",
}


# ═══════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class FileChange:
    file: str
    matches: int = 0
    line_numbers: list = field(default_factory=list)  # lines with matches
    sample_lines: list = field(default_factory=list)  # first 3 matching lines (truncated)


@dataclass
class Report:
    root: str
    mode: str
    executed_at: str
    old_name: str
    new_name: str
    files_scanned: int = 0
    files_with_matches: int = 0
    files_modified: int = 0
    total_replacements: int = 0
    changes: list = field(default_factory=list)
    errors: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# FILE WALKER
# ═══════════════════════════════════════════════════════════════════════

def is_skip_dir(name: str) -> bool:
    if name in SKIP_DIRS:
        return True
    # Match versioned venv patterns
    if re.match(r'^(?:\.)?venv-\d+', name, re.IGNORECASE):
        return True
    return False


def scan_file(path: Path, root: Path) -> tuple[int, list[int], list[str]]:
    """Scan a file for occurrences of OLD_NAME.

    Returns (match_count, line_numbers, sample_lines).
    """
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return (0, [], [])

    if OLD_NAME not in text:
        return (0, [], [])

    count = 0
    line_numbers = []
    sample_lines = []

    for i, line in enumerate(text.splitlines(), 1):
        if OLD_NAME in line:
            count += line.count(OLD_NAME)
            line_numbers.append(i)
            if len(sample_lines) < 3:
                # Truncate line for display, show context around match
                truncated = line.strip()[:100]
                sample_lines.append(f"L{i}: {truncated}")

    return (count, line_numbers, sample_lines)


def replace_in_file(path: Path, root: Path) -> int:
    """Replace OLD_NAME with NEW_NAME in a file. Returns number of replacements."""
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError:
        return 0

    if OLD_NAME not in text:
        return 0

    new_text = text.replace(OLD_NAME, NEW_NAME)
    replacements = text.count(OLD_NAME) - new_text.count(OLD_NAME)
    # Actually, count = text.count(OLD_NAME) since we replaced all
    replacements = text.count(OLD_NAME)

    try:
        path.write_text(new_text, encoding="utf-8")
    except OSError as e:
        raise

    return replacements


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="standardize_names",
        description=f"Eco Nojin Phase 2.3: Rename '{OLD_NAME}' → '{NEW_NAME}' everywhere.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--root", type=str, default=".", help="Repo root")
    parser.add_argument("--apply", action="store_true", help="Actually modify files (default: dry-run)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show every matching line")
    parser.add_argument("--report", type=str, default="standardize_names_report.json")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.exists():
        print(f"Error: root not found: {root}", file=sys.stderr)
        sys.exit(1)

    mode = "APPLY" if args.apply else "DRY-RUN (pass --apply to execute)"
    print("=" * 70)
    print("  Eco Nojin — Phase 2.3: Standardize Package Naming")
    print(f"  Mode: {mode}")
    print(f"  Root: {root}")
    print(f"  Rename: '{OLD_NAME}' → '{NEW_NAME}'")
    print("=" * 70)
    print()

    report = Report(
        root=str(root),
        mode="apply" if args.apply else "dry-run",
        executed_at=datetime.now().isoformat(timespec="seconds"),
        old_name=OLD_NAME,
        new_name=NEW_NAME,
    )

    # Walk all files
    print("  Scanning files for references to 'hydrology-frontend'...")
    files_with_matches: list[tuple[Path, FileChange]] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Filter skip dirs in-place
        dirnames[:] = [d for d in dirnames if not is_skip_dir(d)]

        for fname in filenames:
            fpath = Path(dirpath) / fname
            ext = fpath.suffix.lower()

            # Also check files without extension that might be configs
            # (e.g., "Dockerfile", "Makefile", ".env")
            should_scan = ext in SCAN_EXTENSIONS or fname in {
                "Dockerfile", "Makefile", ".env", ".env.example",
                "pnpmfile.cjs", "turbo.json",
            }

            if not should_scan:
                continue

            try:
                count, line_nums, samples = scan_file(fpath, root)
            except Exception as e:
                report.errors.append(f"{fpath}: {e}")
                continue

            report.files_scanned += 1

            if count > 0:
                rel = str(fpath.relative_to(root)).replace("\\", "/")
                change = FileChange(
                    file=rel,
                    matches=count,
                    line_numbers=line_nums,
                    sample_lines=samples,
                )
                files_with_matches.append((fpath, change))
                report.changes.append(change)
                report.files_with_matches += 1
                report.total_replacements += count

    print(f"  Scanned {report.files_scanned} files")
    print(f"  Found {report.total_replacements} occurrence(s) in {report.files_with_matches} file(s)")
    print()

    # Show results grouped by directory
    if files_with_matches:
        print("  " + "─" * 68)
        print("  FILES WITH MATCHES:")
        print("  " + "─" * 68)

        # Group by top-level directory
        by_dir: dict[str, list[FileChange]] = {}
        for _, change in files_with_matches:
            parts = change.file.split("/")
            top = parts[0] if parts else "(root)"
            by_dir.setdefault(top, []).append(change)

        for dir_name in sorted(by_dir.keys()):
            changes = by_dir[dir_name]
            dir_total = sum(c.matches for c in changes)
            print(f"  📁 {dir_name}/ ({dir_total} match(es) in {len(changes)} file(s))")
            for c in changes:
                short = c.file
                if len(short) > 55:
                    short = "..." + short[-52:]
                print(f"     • {short:<55} {c.matches:>3} match(es)")
                if args.verbose:
                    for sample in c.sample_lines:
                        print(f"         {sample}")
            print()

    # Apply changes
    if args.apply and files_with_matches:
        print("  " + "─" * 68)
        print("  APPLYING CHANGES...")
        print("  " + "─" * 68)
        for fpath, change in files_with_matches:
            try:
                n = replace_in_file(fpath, root)
                report.files_modified += 1
                rel = str(fpath.relative_to(root)).replace("\\", "/")
                print(f"  ✓ {rel}: {n} replacement(s)")
            except OSError as e:
                report.errors.append(f"{fpath}: {e}")
                print(f"  ✗ {fpath}: {e}")
        print()

    # Summary
    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Files scanned       : {report.files_scanned}")
    print(f"  Files with matches  : {report.files_with_matches}")
    if args.apply:
        print(f"  Files modified      : {report.files_modified}")
    print(f"  Total replacements  : {report.total_replacements}")
    print(f"  Errors              : {len(report.errors)}")
    if not args.apply and report.total_replacements > 0:
        print()
        print(f"  ⚠ DRY-RUN. To apply, run:")
        print(f"     python3 {Path(sys.argv[0]).name} --apply")
    print()

    # Write report
    report_path = root / args.report
    try:
        report_path.write_text(
            json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        print(f"  Report: {report_path}")
    except OSError as e:
        print(f"  Warning: could not write report: {e}", file=sys.stderr)
    print()

    # Post-apply instructions
    if args.apply and report.files_modified > 0:
        print("  " + "─" * 68)
        print("  NEXT STEPS (after rename):")
        print("  " + "─" * 68)
        print(f"  1. Update pnpm-lock.yaml:")
        print(f"       pnpm install")
        print()
        print(f"  2. Verify the rename worked:")
        print(f"       pnpm --filter {NEW_NAME} -- list")
        print()
        print(f"  3. Run type-check to catch broken imports:")
        print(f"       pnpm --filter {NEW_NAME} type-check")
        print()
        print(f"  4. Commit:")
        print(f'       git add -A')
        print(f'       git commit -m "refactor(naming): rename hydrology-frontend to @econojin/web"')
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())

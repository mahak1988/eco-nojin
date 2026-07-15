#!/usr/bin/env python3
"""
Eco Nojin — Phase 1 Verifier: Check Git Tracking
==================================================
After running phase1_complete_apps.py, this script verifies that the
created files are actually tracked by git (not ignored by .gitignore).

It cross-references:
  1. Files reported as created in phase1_report.json
  2. Files actually tracked by git (via `git ls-files`)
  3. .gitignore rules that may be blocking them

Output:
  - List of created files that ARE tracked (good)
  - List of created files that are NOT tracked (problematic)
  - The specific .gitignore rule(s) blocking each ignored file
  - Suggested fix commands

Usage:
    python3 phase1_verify_git.py                       # uses ./phase1_report.json
    python3 phase1_verify_git.py --report other.json   # custom report path
    python3 phase1_verify_git.py --root /path/to/repo  # custom repo root
    python3 phase1_verify_git.py --fix                 # print git add -f commands
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional


def run_git(root: Path, args: list[str]) -> tuple[int, str, str]:
    """Run a git command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode, result.stdout, result.stderr
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return -1, "", str(e)


def get_tracked_files(root: Path) -> set[str]:
    """Get all files tracked by git (forward-slash normalized)."""
    code, stdout, _ = run_git(root, ["ls-files"])
    if code != 0:
        return set()
    return {line.strip().replace("\\", "/") for line in stdout.splitlines() if line.strip()}


def get_gitignored_files(root: Path, paths: list[str]) -> dict[str, str]:
    """For each path, check if it's ignored and return the matching rule.

    Uses `git check-ignore -v` which prints the source .gitignore rule.
    """
    ignored: dict[str, str] = {}
    if not paths:
        return ignored

    # git check-ignore can take multiple paths at once
    # -v prints verbose info: "<source>:<linenum>:<pattern>\t<pathname>"
    code, stdout, stderr = run_git(root, ["check-ignore", "-v"] + paths)
    if code == 0:
        # Each line: <source>:<linenum>:<pattern>\t<pathname>
        for line in stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # Parse: source:linenum:pattern\tpathname
            # The first 3 fields are colon-separated, then a tab, then the pathname
            try:
                # Find the tab separator
                if "\t" in line:
                    rule_part, pathname = line.rsplit("\t", 1)
                else:
                    # Some git versions use spaces
                    parts = line.split(" ", 1)
                    if len(parts) == 2:
                        rule_part, pathname = parts
                    else:
                        continue
                # rule_part looks like: ".gitignore:42:*.py"
                rule_fields = rule_part.split(":", 2)
                if len(rule_fields) >= 3:
                    source_file = rule_fields[0]
                    line_num = rule_fields[1]
                    pattern = rule_fields[2]
                    rule_str = f"{source_file}:{line_num}: {pattern}"
                else:
                    rule_str = rule_part
                ignored[pathname.replace("\\", "/")] = rule_str
            except (ValueError, IndexError):
                continue
    return ignored


def parse_gitignore(root: Path) -> list[tuple[str, int, str]]:
    """Parse all .gitignore files in the repo and return their rules.

    Returns list of (file_path, line_number, pattern) tuples.
    """
    rules: list[tuple[str, int, str]] = []

    # Find all .gitignore files (top-level + nested)
    gitignore_files = []
    for path in root.rglob(".gitignore"):
        # Skip .git directory
        if ".git" in path.parts:
            continue
        gitignore_files.append(path)

    for gi_path in gitignore_files:
        try:
            rel_path = str(gi_path.relative_to(root)).replace("\\", "/")
            lines = gi_path.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
            for line_num, line in enumerate(lines, 1):
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                rules.append((rel_path, line_num, stripped))
        except OSError:
            continue

    return rules


def main():
    parser = argparse.ArgumentParser(
        prog="phase1_verify_git",
        description="Verify that phase1_created files are tracked by git.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="Path to the repo root (default: current directory)",
    )
    parser.add_argument(
        "--report", type=str, default="phase1_report.json",
        help="Path to phase1_report.json (default: ./phase1_report.json)",
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Print `git add -f` commands for ignored files",
    )
    parser.add_argument(
        "--apply-fix", action="store_true",
        help="Actually run `git add -f` for ignored files (use with caution)",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    report_path = root / args.report

    if not report_path.exists():
        print(f"Error: report file not found: {report_path}", file=sys.stderr)
        print(f"Run phase1_complete_apps.py first to generate it.", file=sys.stderr)
        sys.exit(1)

    # Load report
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {report_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Collect all created files (relative to repo root, forward-slash normalized)
    created_files: list[str] = []
    for app in report.get("apps", []):
        app_name = app["name"]
        for f in app.get("files_created", []):
            rel = f"apps/{app_name}/{f}".replace("\\", "/")
            created_files.append(rel)

    if not created_files:
        print("=" * 70)
        print("  Phase 1 Git Verifier")
        print("=" * 70)
        print()
        print(f"  No files were created in the report ({report_path}).")
        print(f"  This means either:")
        print(f"    1. phase1_complete_apps.py was run in dry-run mode, OR")
        print(f"    2. All planned files already existed (skipped).")
        print()
        return 0

    # Check git repo
    git_dir = root / ".git"
    if not git_dir.exists():
        print(f"Error: not a git repository: {root}", file=sys.stderr)
        sys.exit(1)

    # Get all tracked files
    tracked = get_tracked_files(root)

    # Check which created files are tracked vs ignored
    tracked_created = []
    untracked_created = []
    for f in created_files:
        if f in tracked:
            tracked_created.append(f)
        else:
            untracked_created.append(f)

    # For untracked files, find which .gitignore rule is blocking them
    ignored_rules = {}
    if untracked_created:
        # git check-ignore needs paths to exist on disk
        existing_untracked = [f for f in untracked_created if (root / f).exists()]
        if existing_untracked:
            # Run check-ignore in batches (avoid command-line length limits)
            batch_size = 50
            for i in range(0, len(existing_untracked), batch_size):
                batch = existing_untracked[i:i + batch_size]
                ignored_rules.update(get_gitignored_files(root, batch))

    # Output
    print("=" * 70)
    print("  Phase 1 Git Verifier — Check Tracking Status")
    print("=" * 70)
    print(f"  Repo root       : {root}")
    print(f"  Report file     : {report_path}")
    print(f"  Files created   : {len(created_files)}")
    print(f"  Tracked by git  : {len(tracked_created)}")
    print(f"  Untracked/ignored: {len(untracked_created)}")
    print()

    if tracked_created:
        print("─" * 70)
        print(f"  ✅ TRACKED ({len(tracked_created)} files) — these are committed correctly")
        print("─" * 70)
        for f in tracked_created[:20]:
            print(f"  ✓ {f}")
        if len(tracked_created) > 20:
            print(f"  ... and {len(tracked_created) - 20} more")
        print()

    if untracked_created:
        print("─" * 70)
        print(f"  ⚠️  UNTRACKED / IGNORED ({len(untracked_created)} files)")
        print("─" * 70)
        print()
        print("  These files were created on disk but are NOT tracked by git.")
        print("  They will be lost if the working directory is cleaned or the")
        print("  branch is switched. The blocking .gitignore rule is shown.")
        print()

        # Group by rule
        by_rule: dict[str, list[str]] = {}
        no_rule: list[str] = []
        for f in untracked_created:
            rule = ignored_rules.get(f)
            if rule:
                by_rule.setdefault(rule, []).append(f)
            else:
                # File exists on disk but not tracked and not ignored by .gitignore
                # → maybe newly created and not yet `git add`-ed
                if (root / f).exists():
                    no_rule.append(f)

        for rule, files in by_rule.items():
            print(f"  📋 Rule: {rule}")
            for f in files[:5]:
                print(f"      ✗ {f}")
            if len(files) > 5:
                print(f"      ... and {len(files) - 5} more")
            print()

        if no_rule:
            print(f"  📋 NOT IGNORED but not yet `git add`-ed ({len(no_rule)} files):")
            print(f"      These exist on disk but haven't been staged yet.")
            print(f"      Run: git add {' '.join(no_rule[:3])} ...")
            for f in no_rule[:5]:
                print(f"      ? {f}")
            if len(no_rule) > 5:
                print(f"      ... and {len(no_rule) - 5} more")
            print()

    # Suggest fixes
    if untracked_created:
        print("=" * 70)
        print("  RECOMMENDED FIXES")
        print("=" * 70)
        print()

        if by_rule:
            print("  Option A: Remove the blocking .gitignore rule(s)")
            print("  ─────────────────────────────────────────────────────")
            for rule in by_rule:
                source_file, line_num, pattern = rule.split(":", 2)
                line_num = line_num.strip()
                pattern = pattern.strip()
                print(f"  Edit {source_file} line {line_num}:")
                print(f"    Currently: {pattern}")
                print(f"    Action: comment out (prefix with #) or remove the line")
                print()
            print("  Then run:")
            print(f"    git add apps/")
            print(f"    git status  # verify")
            print()

        print("  Option B: Force-add the ignored files (keeps .gitignore as-is)")
        print("  ─────────────────────────────────────────────────────")
        print("  Use this if the .gitignore rule is intentionally broad and you")
        print("  want to track these specific files anyway.")
        print()

        if args.fix or args.apply_fix:
            print("  Commands to run:")
            add_commands = []
            for f in untracked_created:
                if (root / f).exists():
                    add_commands.append(f"git add -f \"{f}\"")
            for cmd in add_commands:
                print(f"    {cmd}")
            print()

            if args.apply_fix:
                print("  Applying...")
                for f in untracked_created:
                    if (root / f).exists():
                        # Run git add -f without quoting (subprocess handles paths safely)
                        code, _, stderr = run_git(root, ["add", "-f", f])
                        if code == 0:
                            print(f"    ✓ {f}")
                        else:
                            print(f"    ✗ {f}: {stderr.strip()}")
                print()
                print("  Done. Run `git status` to verify, then commit:")
                print(f"    git commit -m \"feat(phase1): track scaffolded files\"")
            else:
                print("  (Dry-run. Add --apply-fix to execute these commands.)")
        else:
            print("  Run with --fix to see the exact commands:")
            print(f"    python3 {Path(sys.argv[0]).name} --fix")
            print()

    elif not untracked_created and tracked_created:
        print("=" * 70)
        print("  ✅ ALL CREATED FILES ARE TRACKED BY GIT")
        print("=" * 70)
        print()
        print(f"  All {len(tracked_created)} files created by phase1_complete_apps.py")
        print(f"  are properly tracked. You can safely commit them.")
        print()

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

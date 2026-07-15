#!/usr/bin/env python3
"""
Eco Nojin — Phase 1 Verifier v2: Direct Git Tracking Check
=============================================================
Scans all files in apps/ on disk and reports which ones are:
  - Tracked by git (good)
  - Untracked but not ignored (just need `git add`)
  - Untracked AND ignored by a .gitignore rule (problem — needs fix)

Unlike v1, this does NOT depend on phase1_report.json — it scans the
actual apps/ directory directly. Use this when the report is stale or
when you've made manual changes after running phase1_complete_apps.py.

Features:
  • Direct filesystem scan (no report dependency)
  • Identifies the EXACT .gitignore rule blocking each ignored file
  • Groups results by app for easy review
  • --fix prints `git add -f` commands
  • --apply-fix runs them automatically
  • --only / --skip to focus on specific apps

Usage:
    python3 phase1_verify_git_v2.py                         # scan all apps/
    python3 phase1_verify_git_v2.py --only users,web        # only specific apps
    python3 phase1_verify_git_v2.py --fix                   # show fix commands
    python3 phase1_verify_git_v2.py --apply-fix             # run git add -f
    python3 phase1_verify_git_v2.py --root /path/to/repo    # custom root
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Directories that are typically generated — skip them (same as project_analyzer)
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".tox", ".eggs", "dist", "build", ".next", ".nuxt",
    ".output", ".svelte-kit", "target", "vendor", ".venv", "venv", "env",
    ".env", ".idea", ".vscode", "coverage", ".nyc_output", ".cache",
    ".parcel-cache", "tmp", "temp", ".gradle", ".mvn", ".terraform",
    ".pnpm-store", ".turbo", ".yarn", ".deno", ".bun",
}


@dataclass
class FileInfo:
    rel_path: str          # path relative to repo root, forward-slash normalized
    abs_path: Path
    size: int
    is_tracked: bool = False
    is_ignored: bool = False
    ignore_rule: str = ""  # e.g. ".gitignore:42: *.py"
    app_name: str = ""     # top-level apps/<name>/ component


@dataclass
class AppReport:
    name: str
    total_files: int = 0
    tracked: int = 0
    untracked_not_ignored: int = 0
    ignored: int = 0
    ignored_files: list = field(default_factory=list)
    ignored_rules: dict = field(default_factory=dict)  # rule_str → [files]


def run_git(root: Path, args: list[str]) -> tuple[int, str, str]:
    """Run a git command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode, result.stdout, result.stderr
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return -1, "", str(e)


def is_ignored_dir(name: str) -> bool:
    """Check if a directory should be skipped during scan."""
    if name in IGNORE_DIRS:
        return True
    # Match versioned venv patterns
    import re
    if re.match(r'^(?:\.)?venv-\d+(?:\.\d+)*$', name, re.IGNORECASE):
        return True
    if re.match(r'^env-\d+(?:\.\d+)*$', name, re.IGNORECASE):
        return True
    if name.endswith(".egg-info") or name.endswith(".egg-link"):
        return True
    return False


def scan_apps_dir(apps_dir: Path, root: Path) -> list[FileInfo]:
    """Walk apps/ and collect all files (excluding IGNORE_DIRS)."""
    files: list[FileInfo] = []
    if not apps_dir.exists():
        return files

    for dirpath, dirnames, filenames in os.walk(apps_dir):
        # Filter ignored directories in-place
        dirnames[:] = [d for d in dirnames if not is_ignored_dir(d)]

        for fname in filenames:
            fpath = Path(dirpath) / fname
            try:
                stat = fpath.stat()
            except (PermissionError, OSError):
                continue

            # Compute relative path to repo root
            try:
                rel = str(fpath.relative_to(root)).replace("\\", "/")
            except ValueError:
                continue

            # Extract app name (apps/<name>/...)
            parts = rel.split("/")
            app_name = parts[1] if len(parts) >= 2 and parts[0] == "apps" else "(root)"

            files.append(FileInfo(
                rel_path=rel,
                abs_path=fpath,
                size=stat.st_size,
                app_name=app_name,
            ))

    return files


def get_tracked_files(root: Path) -> set[str]:
    """Get all files tracked by git (forward-slash normalized)."""
    code, stdout, _ = run_git(root, ["ls-files"])
    if code != 0:
        return set()
    return {line.strip().replace("\\", "/") for line in stdout.splitlines() if line.strip()}


def check_ignored(root: Path, paths: list[str]) -> dict[str, str]:
    """For each path, return the .gitignore rule blocking it (if any).

    Uses `git check-ignore -v` which prints: <source>:<line>:<pattern>\t<path>
    """
    ignored: dict[str, str] = {}
    if not paths:
        return ignored

    # Process in batches to avoid command-line length limits (Windows ~8KB)
    batch_size = 30
    for i in range(0, len(paths), batch_size):
        batch = paths[i:i + batch_size]
        code, stdout, _ = run_git(root, ["check-ignore", "-v"] + batch)
        # git check-ignore returns 0 if any path is ignored, 1 if none, 128 on error
        if code in (0, 1):
            for line in stdout.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Parse: source:linenum:pattern\tpathname
                try:
                    if "\t" in line:
                        rule_part, pathname = line.rsplit("\t", 1)
                    else:
                        # Fallback: split by spaces (less reliable)
                        parts = line.rsplit(" ", 1)
                        if len(parts) == 2:
                            rule_part, pathname = parts
                        else:
                            continue

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


def main():
    parser = argparse.ArgumentParser(
        prog="phase1_verify_git_v2",
        description="Eco Nojin Phase 1 Verifier v2 — direct git tracking check for apps/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="Path to the repo root (default: current directory)",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Comma-separated list of app names to check (default: all in apps/)",
    )
    parser.add_argument(
        "--skip", type=str, default=None,
        help="Comma-separated list of app names to skip",
    )
    parser.add_argument(
        "--fix", action="store_true",
        help="Print `git add -f` commands for ignored files",
    )
    parser.add_argument(
        "--apply-fix", action="store_true",
        help="Actually run `git add -f` for ignored files (use with caution)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show every ignored file (not just summary)",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    apps_dir = root / "apps"

    if not apps_dir.exists():
        print(f"Error: apps/ directory not found at: {apps_dir}", file=sys.stderr)
        sys.exit(1)

    git_dir = root / ".git"
    if not git_dir.exists():
        print(f"Error: not a git repository: {root}", file=sys.stderr)
        sys.exit(1)

    # Build include/exclude sets
    only_set = {s.strip() for s in args.only.split(",")} if args.only else None
    skip_set = {s.strip() for s in args.skip.split(",")} if args.skip else set()

    print("=" * 70)
    print("  Phase 1 Git Verifier v2 — Direct Scan")
    print("=" * 70)
    print(f"  Root: {root}")
    print(f"  Scanning: apps/ (excluding cache/generated dirs)")
    print()

    # Scan filesystem
    print("  [1/3] Scanning apps/ directory...", end=" ", flush=True)
    all_files = scan_apps_dir(apps_dir, root)
    print(f"{len(all_files)} files found")

    # Filter by --only / --skip
    if only_set or skip_set:
        filtered = []
        for f in all_files:
            if only_set and f.app_name not in only_set:
                continue
            if f.app_name in skip_set:
                continue
            filtered.append(f)
        all_files = filtered

    if not all_files:
        print("  No files to check (after --only / --skip filter).")
        return 0

    # Get tracked files from git
    print("  [2/3] Querying git for tracked files...", end=" ", flush=True)
    tracked_set = get_tracked_files(root)
    print(f"{len(tracked_set)} files tracked by git")

    # Mark tracked
    for f in all_files:
        f.is_tracked = f.rel_path in tracked_set

    # Find untracked files
    untracked = [f for f in all_files if not f.is_tracked]
    print(f"  [3/3] Checking {len(untracked)} untracked files against .gitignore...",
          end=" ", flush=True)
    untracked_paths = [f.rel_path for f in untracked]
    ignored_map = check_ignored(root, untracked_paths)
    print("done")
    print()

    # Mark ignored
    for f in untracked:
        if f.rel_path in ignored_map:
            f.is_ignored = True
            f.ignore_rule = ignored_map[f.rel_path]

    # Build per-app reports
    apps: dict[str, AppReport] = {}
    for f in all_files:
        if f.app_name not in apps:
            apps[f.app_name] = AppReport(name=f.app_name)
        app = apps[f.app_name]
        app.total_files += 1
        if f.is_tracked:
            app.tracked += 1
        elif f.is_ignored:
            app.ignored += 1
            app.ignored_files.append(f.rel_path)
            rule = f.ignore_rule
            app.ignored_rules.setdefault(rule, []).append(f.rel_path)
        else:
            app.untracked_not_ignored += 1

    # Summary
    total_files = len(all_files)
    total_tracked = sum(a.tracked for a in apps.values())
    total_untracked_not_ignored = sum(a.untracked_not_ignored for a in apps.values())
    total_ignored = sum(a.ignored for a in apps.values())

    print("=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Total files in apps/ : {total_files}")
    print(f"  Tracked by git       : {total_tracked}  ({total_tracked * 100 // max(total_files, 1)}%)")
    print(f"  Untracked (not ign.) : {total_untracked_not_ignored}  ← just need `git add`")
    print(f"  Ignored by .gitignore: {total_ignored}  ← needs `git add -f` or .gitignore fix")
    print()

    # Per-app breakdown
    print("─" * 70)
    print(f"  {'App':<25} {'Total':>7} {'Tracked':>9} {'Untracked':>10} {'Ignored':>9}")
    print("─" * 70)
    for app_name in sorted(apps.keys()):
        a = apps[app_name]
        flag = " ⚠️" if a.ignored > 0 or a.untracked_not_ignored > 0 else "  ✓"
        print(f"  {flag} {app_name:<22} {a.total_files:>7} {a.tracked:>9} "
              f"{a.untracked_not_ignored:>10} {a.ignored:>9}")
    print()

    # Detail: ignored files (the real problem)
    if total_ignored > 0:
        print("=" * 70)
        print(f"  ⚠️  IGNORED FILES — BLOCKED BY .gitignore  ({total_ignored} files)")
        print("=" * 70)
        print()
        print("  These files exist on disk but git refuses to track them.")
        print("  They will be LOST if the working directory is cleaned.")
        print()

        # Group by app, then by rule
        for app_name in sorted(apps.keys()):
            a = apps[app_name]
            if not a.ignored_files:
                continue
            print(f"  📦 apps/{app_name}/  ({len(a.ignored_files)} ignored files)")
            for rule, files in a.ignored_rules.items():
                print(f"     Rule: {rule}")
                show = files if args.verbose else files[:5]
                for f in show:
                    # Show just the path after apps/<name>/
                    short = f.split(f"apps/{app_name}/", 1)[-1] if f"apps/{app_name}/" in f else f
                    print(f"        ✗ {short}")
                if not args.verbose and len(files) > 5:
                    print(f"        ... and {len(files) - 5} more")
            print()

    # Detail: untracked but not ignored (just need git add)
    if total_untracked_not_ignored > 0:
        print("=" * 70)
        print(f"  📋 UNTRACKED (not ignored) — just need `git add`  ({total_untracked_not_ignored} files)")
        print("=" * 70)
        print()
        for app_name in sorted(apps.keys()):
            a = apps[app_name]
            untracked_in_app = [
                f for f in a.ignored_files  # wait, this is ignored only
            ]
            # Recompute: untracked-not-ignored files for this app
            untracked_not_ignored = [
                f for f in all_files
                if f.app_name == app_name and not f.is_tracked and not f.is_ignored
            ]
            if not untracked_not_ignored:
                continue
            print(f"  📦 apps/{app_name}/  ({len(untracked_not_ignored)} untracked files)")
            show = untracked_not_ignored if args.verbose else untracked_not_ignored[:5]
            for f in show:
                short = f.rel_path.split(f"apps/{app_name}/", 1)[-1] if f"apps/{app_name}/" in f.rel_path else f.rel_path
                print(f"        ? {short}")
            if not args.verbose and len(untracked_not_ignored) > 5:
                print(f"        ... and {len(untracked_not_ignored) - 5} more")
            print()

    # Recommended fixes
    if total_ignored > 0 or total_untracked_not_ignored > 0:
        print("=" * 70)
        print("  RECOMMENDED FIXES")
        print("=" * 70)
        print()

        if total_ignored > 0:
            # Collect unique rules across all apps
            all_rules: dict[str, list[str]] = defaultdict(list)
            for a in apps.values():
                for rule, files in a.ignored_rules.items():
                    all_rules[rule].extend(files)

            print(f"  Option A: Fix the .gitignore rule(s) blocking {total_ignored} files")
            print("  " + "─" * 68)
            for rule in sorted(all_rules.keys()):
                files = all_rules[rule]
                # Parse rule: "source:linenum: pattern"
                try:
                    parts = rule.split(":", 2)
                    source_file = parts[0]
                    line_num = parts[1]
                    pattern = parts[2].strip()
                    print(f"  Edit {source_file} line {line_num}:")
                    print(f"    Currently: {pattern}")
                    print(f"    Blocks {len(files)} file(s) in apps/")
                    print(f"    Action: comment out (prefix with #) or make more specific")
                    print()
                except (IndexError, ValueError):
                    print(f"  Rule: {rule}  (blocks {len(files)} files)")
                    print()

            print("  After fixing .gitignore, run:")
            print(f"    git add apps/")
            print(f"    git status  # verify")
            print()

            print(f"  Option B: Force-add the {total_ignored} ignored files (keeps .gitignore)")
            print("  " + "─" * 68)
            print("  Use this if the .gitignore rule is intentionally broad and you")
            print("  want to track these specific files anyway.")
            print()

            if args.fix or args.apply_fix:
                # Collect all ignored file paths
                ignored_paths = []
                for a in apps.values():
                    ignored_paths.extend(a.ignored_files)

                if args.apply_fix:
                    print("  Applying git add -f...")
                    success = 0
                    failed = 0
                    for f in ignored_paths:
                        code, _, stderr = run_git(root, ["add", "-f", f])
                        if code == 0:
                            success += 1
                        else:
                            failed += 1
                            if args.verbose:
                                print(f"    ✗ {f}: {stderr.strip()}")
                    print(f"  ✓ Added {success} files, {failed} failures")
                    print()
                    print("  Next steps:")
                    print(f"    git status")
                    print(f"    git commit -m \"feat(phase1): track scaffolded apps/* files\"")
                else:
                    print("  Commands to run (dry-run — add --apply-fix to execute):")
                    for f in ignored_paths[:20]:
                        print(f"    git add -f \"{f}\"")
                    if len(ignored_paths) > 20:
                        print(f"    # ... and {len(ignored_paths) - 20} more")
                    print()
                    print(f"  Or add all at once:")
                    print(f"    git add -f \\")
                    # Print as a single command (careful with shell escaping)
                    for f in ignored_paths[:5]:
                        print(f"      \"{f}\" \\")
                    if len(ignored_paths) > 5:
                        print(f"      # ... and {len(ignored_paths) - 5} more")
                    print()
            else:
                print("  Run with --fix to see the exact commands:")
                print(f"    python3 {Path(sys.argv[0]).name} --fix")
                print()

        if total_untracked_not_ignored > 0:
            print(f"  Option C: Stage the {total_untracked_not_ignored} untracked (not ignored) files")
            print("  " + "─" * 68)
            print("  These are simply new files that haven't been `git add`-ed yet.")
            print()
            print(f"    git add apps/")
            print()

    elif total_tracked == total_files:
        print("=" * 70)
        print("  ✅ ALL FILES IN apps/ ARE TRACKED BY GIT")
        print("=" * 70)
        print()
        print(f"  All {total_files} files are properly tracked. No action needed.")
        print()

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

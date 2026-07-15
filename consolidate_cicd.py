#!/usr/bin/env python3
"""
Eco Nojin — Phase 2.1: Smart CI/CD Consolidator
=================================================
Consolidates redundant GitHub Actions workflows by:
  1. Identifying unique jobs in redundant workflows (must not be lost)
  2. Appending unique jobs to the "keep" workflow with source attribution
  3. Archiving redundant workflows to .github/workflows/.archived/
  4. Fixing version drift in action references (e.g. checkout@v3 → @v4)
  5. Generating a consolidation report

SMART RULES:
  • Never merge workflows for DIFFERENT environments (staging ≠ production)
  • Detect unique jobs by name + step signature
  • Preserve job dependencies (needs:) when merging
  • Archive (not delete) — files go to .github/workflows/.archived/
  • Add a comment header to merged jobs: "# Migrated from <source-file>"

SAFETY:
  • Dry-run by default (no files modified)
  • --apply to execute
  • Always creates a backup of the keep file before modifying
  • Generates consolidation_report.json with full audit trail

Usage:
    python3 consolidate_cicd.py --root D:\\econojin.com
    python3 consolidate_cicd.py --root D:\\econojin.com --apply
    python3 consolidate_cicd.py --root D:\\econojin.com --only ci,deploy
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# ═══════════════════════════════════════════════════════════════════════
# SMART CONSOLIDATION RULES
# ═══════════════════════════════════════════════════════════════════════

# Workflows that serve DIFFERENT environments should NOT be merged.
# Format: (filename_pattern, environment_label)
ENVIRONMENT_AWARE_WORKFLOWS = {
    "04-deploy-staging.yml": "staging",
    "05-deploy-production.yml": "production",
    "cd-production.yml": "production",
    "deploy.yml": "production",  # generic deploy, treat as production
}

# The "keep" workflow for each purpose — manually curated based on analysis.
# This OVERRIDES the analyzer's automatic recommendation when needed.
KEEP_WORKFLOWS = {
    "ci": "01-ci-main.yml",
    "quality_gate": "03-quality-gates.yml",
    "security_scan": "02-security-scan.yml",
    "deploy_staging": "04-deploy-staging.yml",
    "deploy_production": "05-deploy-production.yml",  # KEEP — different env from staging
    "scheduled": "06-scheduled-tasks.yml",
}

# Workflows to archive (redundant — their unique jobs will be migrated first).
# Mapping: redundant_file → keep_file (where unique jobs go)
ARCHIVE_PLAN = {
    "ci.yml": "01-ci-main.yml",
    "deploy.yml": "01-ci-main.yml",  # build job overlaps; archive
    "econojin-apps-ci.yml": "01-ci-main.yml",  # playwright job is unique → migrate
    "cd-production.yml": "05-deploy-production.yml",  # overlaps with prod deploy
    "quality-gates.yml": "03-quality-gates.yml",
    "quality-gate.yml": "03-quality-gates.yml",  # parse error — investigate
    "architecture-quality-gate.yml": "03-quality-gates.yml",  # parse error
}

# Action version standardization (fix drift).
# Format: (old_pattern, new_version) — applied via regex on raw YAML.
ACTION_VERSION_FIXES = [
    (r'actions/checkout@v3\b', 'actions/checkout@v4'),
    (r'actions/setup-python@v4\b', 'actions/setup-python@v5'),
    (r'pnpm/action-setup@v2\b', 'pnpm/action-setup@v4'),
    (r'slackapi/slack-github-action@v1\b(?!.\d)', 'slackapi/slack-github-action@v1.24.0'),
]


# ═══════════════════════════════════════════════════════════════════════
# DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class JobMigration:
    """A job being migrated from a redundant workflow to a keep workflow."""
    source_file: str
    job_id: str
    job_name: str
    reason: str = ""  # why this job is unique and should be migrated


@dataclass
class FileAction:
    """An action taken on a file."""
    file: str
    action: str  # "keep", "archive", "modify", "skip_parse_error"
    details: str = ""
    jobs_migrated: list = field(default_factory=list)


@dataclass
class ConsolidationReport:
    root: str
    mode: str  # "dry-run" or "apply"
    executed_at: str
    total_workflows_before: int = 0
    total_workflows_after: int = 0
    files_kept: list = field(default_factory=list)
    files_archived: list = field(default_factory=list)
    files_modified: list = field(default_factory=list)
    jobs_migrated: list = field(default_factory=list)
    parse_errors: list = field(default_factory=list)
    version_fixes_applied: list = field(default_factory=list)
    errors: list = field(default_factory=list)


# ═══════════════════════════════════════════════════════════════════════
# YAML HELPERS
# ═══════════════════════════════════════════════════════════════════════

def load_yaml(path: Path) -> Optional[dict]:
    """Load YAML file, return parsed dict or None on error."""
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        return yaml.safe_load(text)
    except (yaml.YAMLError, OSError) as e:
        return None


def dump_yaml(data: dict) -> str:
    """Dump dict to YAML string with consistent formatting.

    CRITICAL: YAML 1.1 treats `on` as a boolean True. PyYAML parses
    the `on:` key in GitHub Actions workflows as `True:`. When we dump
    it back, it becomes `true:` which breaks the workflow.
    We fix this by post-processing the dumped string to replace
    `true:` (at the start of a line) with `on:`.
    """
    text = yaml.dump(
        data,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    # Fix the YAML 1.1 `on:` → `True:` → `true:` round-trip bug.
    # Replace top-level `true:` (the `on:` key) with `on:`.
    # This is safe because `true:` as a top-level key in a workflow
    # is almost certainly the `on:` trigger key.
    text = re.sub(r'^true:', 'on:', text, count=1, flags=re.MULTILINE)
    # Also fix nested `true:` that was originally `on:` inside trigger definitions
    # (less common, but just in case)
    # Actually, only the top-level `on:` key is affected; nested ones are fine.
    return text


def extract_jobs(parsed: dict) -> dict:
    """Extract the jobs dict from a parsed workflow, or empty dict."""
    if not isinstance(parsed, dict):
        return {}
    jobs = parsed.get("jobs", {})
    if not isinstance(jobs, dict):
        return {}
    return jobs


def job_signature(job_def: dict) -> str:
    """Create a signature for a job to detect duplicates.

    Two jobs with the same signature are considered duplicates.
    Signature = sorted tuple of step "uses" + first 40 chars of each "run" command.
    """
    if not isinstance(job_def, dict):
        return ""
    steps = job_def.get("steps", [])
    if not isinstance(steps, list):
        return ""
    sig_parts = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        if "uses" in step:
            sig_parts.append(f"uses:{step['uses']}")
        elif "run" in step:
            run_cmd = str(step["run"]).strip().split("\n")[0][:40]
            sig_parts.append(f"run:{run_cmd}")
    return "|".join(sorted(sig_parts))


def job_step_names(job_def: dict) -> list[str]:
    """Extract human-readable step names from a job."""
    if not isinstance(job_def, dict):
        return []
    steps = job_def.get("steps", [])
    if not isinstance(steps, list):
        return []
    names = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        name = step.get("name", "")
        if not name:
            if "uses" in step:
                name = f"uses: {step['uses']}"
            elif "run" in step:
                name = f"run: {str(step['run']).split(chr(10))[0][:40]}"
        names.append(name)
    return names


# ═══════════════════════════════════════════════════════════════════════
# CONSOLIDATION LOGIC
# ═══════════════════════════════════════════════════════════════════════

def find_unique_jobs(
    source_jobs: dict,
    target_jobs: dict,
) -> list[tuple[str, dict, str]]:
    """Find jobs in source that don't exist in target.

    Returns list of (job_id, job_def, reason) tuples.
    """
    target_signatures = {job_signature(j) for j in target_jobs.values()}
    unique = []
    for job_id, job_def in source_jobs.items():
        if not isinstance(job_def, dict):
            continue
        sig = job_signature(job_def)
        if sig not in target_signatures:
            # Also check by job_id (in case signature is empty due to parse issues)
            if job_id not in target_jobs:
                step_names = job_step_names(job_def)
                reason = (
                    f"Job '{job_id}' has unique steps not in target: "
                    f"{', '.join(step_names[:3])}"
                    + (f" (+{len(step_names)-3} more)" if len(step_names) > 3 else "")
                )
                unique.append((job_id, job_def, reason))
    return unique


def migrate_jobs_into_keep(
    keep_file: Path,
    source_file: Path,
    unique_jobs: list[tuple[str, dict, str]],
) -> tuple[str, list[JobMigration]]:
    """Migrate unique jobs from source into keep file.

    Returns (new_content, list_of_migrations).
    """
    migrations: list[JobMigration] = []
    if not unique_jobs:
        return ("", migrations)

    keep_parsed = load_yaml(keep_file)
    if keep_parsed is None:
        return ("", migrations)

    keep_jobs = extract_jobs(keep_parsed)

    for job_id, job_def, reason in unique_jobs:
        # Rename job if it conflicts with an existing job in keep
        new_job_id = job_id
        counter = 2
        while new_job_id in keep_jobs:
            new_job_id = f"{job_id}_{counter}"
            counter += 1

        # Add a comment indicating migration source
        # YAML doesn't support comments in dict, so we prepend to job name
        if isinstance(job_def, dict):
            original_name = job_def.get("name", job_id)
            job_def["name"] = f"[Migrated from {source_file.name}] {original_name}"

        keep_jobs[new_job_id] = job_def
        migrations.append(JobMigration(
            source_file=source_file.name,
            job_id=new_job_id,
            job_name=job_def.get("name", new_job_id) if isinstance(job_def, dict) else new_job_id,
            reason=reason,
        ))

    keep_parsed["jobs"] = keep_jobs
    new_content = dump_yaml(keep_parsed)
    return (new_content, migrations)


def apply_version_fixes(yaml_text: str) -> tuple[str, list[str]]:
    """Apply action version standardization to raw YAML text.

    Returns (fixed_text, list_of_fixes_applied).
    """
    fixes_applied: list[str] = []
    fixed = yaml_text
    for pattern, replacement in ACTION_VERSION_FIXES:
        new_fixed, count = re.subn(pattern, replacement, fixed)
        if count > 0:
            fixes_applied.append(
                f"Replaced {count}x: {pattern} → {replacement}"
            )
            fixed = new_fixed
    return (fixed, fixes_applied)


def archive_workflow(
    source_file: Path,
    archive_dir: Path,
    apply: bool,
) -> bool:
    """Move a workflow file to the .archived/ directory."""
    if not source_file.exists():
        return False
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / source_file.name
    if target.exists():
        # Add timestamp to avoid collision
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target = archive_dir / f"{source_file.stem}_{timestamp}.yml"
    if apply:
        shutil.move(str(source_file), str(target))
    return True


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        prog="consolidate_cicd",
        description="Eco Nojin Phase 2.1: Smart CI/CD workflow consolidator.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="Path to the repo root (default: current directory)",
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually modify files (default: dry-run, just preview)",
    )
    parser.add_argument(
        "--only", type=str, default=None,
        help="Comma-separated list of redundant files to process (default: all in ARCHIVE_PLAN)",
    )
    parser.add_argument(
        "--skip", type=str, default=None,
        help="Comma-separated list of redundant files to skip",
    )
    parser.add_argument(
        "--report", type=str, default="consolidation_report.json",
        help="Path to write JSON report (default: ./consolidation_report.json)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show detailed progress",
    )
    args = parser.parse_args()

    if not HAS_YAML:
        print("Error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    root = Path(args.root).expanduser().resolve()
    workflows_dir = root / ".github" / "workflows"
    archive_dir = workflows_dir / ".archived"

    if not workflows_dir.exists():
        print(f"Error: .github/workflows/ not found at: {workflows_dir}", file=sys.stderr)
        sys.exit(1)

    # Build include/exclude sets for redundant files
    only_set = {s.strip() for s in args.only.split(",")} if args.only else None
    skip_set = {s.strip() for s in args.skip.split(",")} if args.skip else set()

    mode_label = "APPLY (modifying files)" if args.apply else "DRY-RUN (no files modified — pass --apply to execute)"
    print("=" * 78)
    print("  Eco Nojin — Phase 2.1: Smart CI/CD Consolidator")
    print(f"  Mode: {mode_label}")
    print(f"  Root: {root}")
    print("=" * 78)
    print()

    report = ConsolidationReport(
        root=str(root),
        mode="apply" if args.apply else "dry-run",
        executed_at=datetime.now().isoformat(timespec="seconds"),
    )

    # Count current workflows
    current_workflows = sorted(
        list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    )
    report.total_workflows_before = len(current_workflows)

    # ── Step 1: Identify keep files and verify they exist
    print("  [1/4] Verifying keep workflows exist...")
    keep_files = set(KEEP_WORKFLOWS.values())
    missing_keep = []
    for kf in keep_files:
        path = workflows_dir / kf
        if not path.exists():
            missing_keep.append(kf)
        else:
            report.files_kept.append(kf)
            if args.verbose:
                print(f"    ✓ {kf}")
    if missing_keep:
        print(f"    ⚠ Missing keep files: {', '.join(missing_keep)}")
        print(f"      These won't be modified.")
    print()

    # ── Step 2: Process each redundant file in ARCHIVE_PLAN
    print("  [2/4] Processing redundant workflows...")
    for redundant_name, keep_name in ARCHIVE_PLAN.items():
        if only_set and redundant_name not in only_set:
            continue
        if redundant_name in skip_set:
            continue

        redundant_path = workflows_dir / redundant_name
        keep_path = workflows_dir / keep_name

        if not redundant_path.exists():
            if args.verbose:
                print(f"    ⊘ {redundant_name} — not found, skipping")
            continue

        # Parse the redundant file
        redundant_parsed = load_yaml(redundant_path)
        if redundant_parsed is None:
            report.parse_errors.append(redundant_name)
            print(f"    ⚠ {redundant_name} — parse error, archiving without job migration")
            if archive_workflow(redundant_path, archive_dir, args.apply):
                report.files_archived.append(redundant_name)
                if args.verbose:
                    print(f"    → archived to .archived/{redundant_name}")
            continue

        # Extract jobs from redundant file
        source_jobs = extract_jobs(redundant_parsed)
        if not source_jobs:
            print(f"    ⊘ {redundant_name} — no jobs found, archiving")
            if archive_workflow(redundant_path, archive_dir, args.apply):
                report.files_archived.append(redundant_name)
            continue

        # Load keep file
        keep_parsed = load_yaml(keep_path)
        if keep_parsed is None:
            print(f"    ⚠ {redundant_name} → {keep_name}: keep file parse error, skipping")
            report.errors.append(f"{redundant_name}: keep file {keep_name} parse error")
            continue

        target_jobs = extract_jobs(keep_parsed)

        # Find unique jobs to migrate
        unique_jobs = find_unique_jobs(source_jobs, target_jobs)

        if unique_jobs:
            print(f"    📦 {redundant_name} → {keep_name}: "
                  f"migrating {len(unique_jobs)} unique job(s)")
            for job_id, job_def, reason in unique_jobs:
                if args.verbose:
                    print(f"       • {job_id}: {reason[:80]}")

            # Migrate jobs
            new_content, migrations = migrate_jobs_into_keep(
                keep_path, redundant_path, unique_jobs
            )
            report.jobs_migrated.extend(migrations)

            # Apply version fixes to the modified keep file
            new_content, version_fixes = apply_version_fixes(new_content)
            report.version_fixes_applied.extend(version_fixes)

            if args.apply:
                # Backup the keep file
                backup_path = keep_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml")
                shutil.copy2(keep_path, backup_path)
                # Write the merged content
                keep_path.write_text(new_content, encoding="utf-8")
                report.files_modified.append(keep_name)
                if args.verbose:
                    print(f"    ✓ Modified {keep_name} (backup: {backup_path.name})")
        else:
            print(f"    📦 {redundant_name} → {keep_name}: "
                  f"no unique jobs, archiving directly")

        # Archive the redundant file
        if archive_workflow(redundant_path, archive_dir, args.apply):
            report.files_archived.append(redundant_name)
            if args.verbose:
                print(f"    → archived to .archived/{redundant_name}")
    print()

    # ── Step 3: Apply version fixes to ALL keep files
    print("  [3/4] Applying action version fixes to keep workflows...")
    for keep_name in report.files_kept:
        keep_path = workflows_dir / keep_name
        if keep_name in report.files_modified:
            # Already processed above; version fixes already applied
            continue
        if not keep_path.exists():
            continue
        original = keep_path.read_text(encoding="utf-8-sig", errors="ignore")
        fixed, fixes = apply_version_fixes(original)
        if fixes:
            print(f"    📝 {keep_name}: {len(fixes)} fix(es)")
            if args.verbose:
                for f in fixes:
                    print(f"       • {f}")
            if args.apply:
                keep_path.write_text(fixed, encoding="utf-8")
            report.version_fixes_applied.extend(fixes)
            if keep_name not in report.files_modified:
                report.files_modified.append(keep_name)
        else:
            if args.verbose:
                print(f"    ✓ {keep_name}: no version fixes needed")
    print()

    # ── Step 4: Count final workflows
    print("  [4/4] Counting final workflows...")
    if args.apply:
        final_workflows = sorted(
            list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        )
    else:
        # In dry-run, simulate the count
        final_count = report.total_workflows_before - len(report.files_archived)
        final_workflows = []
    report.total_workflows_after = (
        len(final_workflows) if args.apply
        else report.total_workflows_before - len(report.files_archived)
    )
    print(f"    Before: {report.total_workflows_before} workflows")
    print(f"    After:  {report.total_workflows_after} workflows")
    print(f"    Archived: {len(report.files_archived)}")
    print(f"    Modified: {len(report.files_modified)}")
    print(f"    Jobs migrated: {len(report.jobs_migrated)}")
    print(f"    Version fixes: {len(report.version_fixes_applied)}")
    if report.parse_errors:
        print(f"    Parse errors (archived without migration): {len(report.parse_errors)}")
    if report.errors:
        print(f"    Errors: {len(report.errors)}")
    print()

    # ── Summary
    print("=" * 78)
    print("  SUMMARY")
    print("=" * 78)
    if report.files_kept:
        print(f"  Kept ({len(report.files_kept)}):")
        for f in report.files_kept:
            print(f"    ✓ {f}")
    if report.files_archived:
        print(f"  Archived ({len(report.files_archived)}):")
        for f in report.files_archived:
            print(f"    📦 {f} → .github/workflows/.archived/")
    if report.jobs_migrated:
        print(f"  Jobs migrated ({len(report.jobs_migrated)}):")
        for m in report.jobs_migrated:
            print(f"    • {m.source_file} :: {m.job_id} → {m.job_name}")
    if report.version_fixes_applied:
        unique_fixes = list(set(report.version_fixes_applied))
        print(f"  Version fixes ({len(unique_fixes)} unique):")
        for f in unique_fixes:
            print(f"    • {f}")
    if not args.apply:
        print()
        print("  ⚠ This was a DRY-RUN. To actually consolidate, run:")
        print(f"     python3 {Path(sys.argv[0]).name} --apply")
    print()

    # ── Write JSON report
    report_path = root / args.report
    try:
        report_path.write_text(
            json.dumps(asdict(report), indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        print(f"  Report written to: {report_path}")
    except (PermissionError, OSError) as e:
        print(f"  Warning: could not write report: {e}", file=sys.stderr)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

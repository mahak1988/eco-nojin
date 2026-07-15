#!/usr/bin/env python3
"""
Eco Nojin — Phase 2.1: Smart CI/CD Consolidator v2 (TEXT-BASED)
=================================================================
Rewritten to use TEXT-BASED manipulation instead of yaml.dump.
This preserves:
  - Comments (including Persian comments)
  - Block style vs flow style
  - Empty lines and indentation
  - Multi-line run: | commands (no \\n escaping)

How it works:
  1. Parse YAML to identify jobs to migrate (read-only)
  2. Render the migrated jobs as YAML TEXT blocks (preserving formatting)
  3. APPEND the new jobs to the keep file's text (not rewrite the whole file)
  4. Apply version fixes via regex on the original text
  5. Archive redundant files (unchanged from v1)

The keep file's existing content is NEVER reflowed or reformatted.
Only new job blocks are appended at the end (before EOF).

Usage:
    python3 consolidate_cicd_v2.py --root D:\\econojin.com
    python3 consolidate_cicd_v2.py --root D:\\econojin.com --apply
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
# CONFIG (same as v1)
# ═══════════════════════════════════════════════════════════════════════

KEEP_WORKFLOWS = {
    "ci": "01-ci-main.yml",
    "quality_gate": "03-quality-gates.yml",
    "security_scan": "02-security-scan.yml",
    "deploy_staging": "04-deploy-staging.yml",
    "deploy_production": "05-deploy-production.yml",
    "scheduled": "06-scheduled-tasks.yml",
}

ARCHIVE_PLAN = {
    "ci.yml": "01-ci-main.yml",
    "deploy.yml": "01-ci-main.yml",
    "econojin-apps-ci.yml": "01-ci-main.yml",
    "cd-production.yml": "05-deploy-production.yml",
    "quality-gates.yml": "03-quality-gates.yml",
    "quality-gate.yml": "03-quality-gates.yml",
    "architecture-quality-gate.yml": "03-quality-gates.yml",
}

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
    source_file: str
    job_id: str
    job_name: str
    reason: str = ""


@dataclass
class ConsolidationReport:
    root: str
    mode: str
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
# YAML HELPERS (parse only — never dump)
# ═══════════════════════════════════════════════════════════════════════

def load_yaml(path: Path) -> Optional[dict]:
    """Load YAML for parsing/inspection only. We NEVER dump it back."""
    try:
        text = path.read_text(encoding="utf-8-sig", errors="ignore")
        return yaml.safe_load(text)
    except (yaml.YAMLError, OSError):
        return None


def extract_jobs(parsed: dict) -> dict:
    if not isinstance(parsed, dict):
        return {}
    jobs = parsed.get("jobs", {})
    return jobs if isinstance(jobs, dict) else {}


def job_signature(job_def: dict) -> str:
    """Signature for duplicate detection."""
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


def find_unique_jobs(source_jobs: dict, target_jobs: dict) -> list[tuple[str, dict, str]]:
    """Find jobs in source not in target. Returns (job_id, job_def, reason)."""
    target_signatures = {job_signature(j) for j in target_jobs.values()}
    unique = []
    for job_id, job_def in source_jobs.items():
        if not isinstance(job_def, dict):
            continue
        sig = job_signature(job_def)
        if sig not in target_signatures and job_id not in target_jobs:
            steps = job_def.get("steps", [])
            step_names = []
            if isinstance(steps, list):
                for step in steps:
                    if isinstance(step, dict):
                        name = step.get("name", "")
                        if not name:
                            if "uses" in step:
                                name = f"uses:{step['uses']}"
                            elif "run" in step:
                                name = f"run:{str(step['run']).split(chr(10))[0][:40]}"
                        step_names.append(name)
            reason = (
                f"Job '{job_id}' has unique steps: "
                f"{', '.join(step_names[:3])}"
                + (f" (+{len(step_names)-3} more)" if len(step_names) > 3 else "")
            )
            unique.append((job_id, job_def, reason))
    return unique


# ═══════════════════════════════════════════════════════════════════════
# TEXT-BASED JOB EXTRACTION (preserves formatting)
# ═══════════════════════════════════════════════════════════════════════

def extract_job_text_blocks(yaml_text: str) -> dict[str, str]:
    """Extract each top-level job as a raw text block, preserving formatting.

    Returns dict: {job_id: raw_text_block}
    The raw_text_block includes the job_id line and all indented content.
    """
    lines = yaml_text.split("\n")
    jobs: dict[str, str] = {}
    in_jobs_section = False
    current_job_id: Optional[str] = None
    current_job_lines: list[str] = []
    jobs_indent = -1  # indentation level of job keys under "jobs:"

    for i, line in enumerate(lines):
        # Detect "jobs:" at top level (no leading whitespace)
        if re.match(r'^jobs\s*:\s*$', line):
            in_jobs_section = True
            jobs_indent = -1
            continue

        if not in_jobs_section:
            continue

        # Check if this line starts a new top-level key (not indented, not blank, not comment)
        if line and not line[0].isspace() and not line.startswith("#"):
            # End of jobs section
            if current_job_id:
                jobs[current_job_id] = "\n".join(current_job_lines)
                current_job_id = None
                current_job_lines = []
            in_jobs_section = False
            continue

        # Inside jobs section
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            if current_job_id:
                current_job_lines.append(line)
            continue

        # Determine indentation
        indent = len(line) - len(stripped)
        if jobs_indent == -1:
            jobs_indent = indent

        # Check if this is a new job definition (indent == jobs_indent, ends with :)
        if indent == jobs_indent and stripped.endswith(":"):
            # Save previous job
            if current_job_id:
                jobs[current_job_id] = "\n".join(current_job_lines)
            # Start new job
            current_job_id = stripped[:-1].strip()  # remove trailing :
            # Handle quoted keys: 'job-name:' or "job-name:"
            if (current_job_id.startswith("'") and current_job_id.endswith("'")) or \
               (current_job_id.startswith('"') and current_job_id.endswith('"')):
                current_job_id = current_job_id[1:-1]
            current_job_lines = [line]
        elif current_job_id:
            current_job_lines.append(line)

    # Save the last job
    if current_job_id:
        jobs[current_job_id] = "\n".join(current_job_lines)

    return jobs


def rename_job_in_text(job_text: str, old_id: str, new_id: str) -> str:
    """Rename a job ID in its text block, preserving everything else."""
    # The job ID is on the first non-empty line, at the end before :
    # Pattern: <indent>old_id:
    lines = job_text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]
        if stripped == f"{old_id}:" or stripped.startswith(f"{old_id}:"):
            lines[i] = f"{indent}{new_id}:{stripped[len(old_id)+1:]}"
            break
    return "\n".join(lines)


def add_migration_comment(job_text: str, source_file: str) -> str:
    """Add a comment above the job block indicating its source."""
    lines = job_text.split("\n")
    if not lines:
        return job_text
    # Find the indentation of the job ID line (first non-empty line)
    first_line = lines[0]
    stripped = first_line.lstrip()
    indent = first_line[:len(first_line) - len(stripped)]
    # Insert comment before the first line
    comment = f"{indent}# ─── Migrated from {source_file} ───"
    return comment + "\n" + job_text


def append_jobs_to_keep_file(
    keep_path: Path,
    jobs_to_append: list[tuple[str, str, str]],  # (job_id, job_text, source_file)
) -> str:
    """Append job text blocks to the keep file, preserving its existing content.

    Returns the new file content. Does NOT write to disk (caller does that).
    """
    original = keep_path.read_text(encoding="utf-8-sig", errors="ignore")

    # Ensure file ends with newline
    if not original.endswith("\n"):
        original += "\n"

    # Load existing jobs to detect ID conflicts
    existing_parsed = load_yaml(keep_path) or {}
    existing_jobs = extract_jobs(existing_parsed)
    existing_ids = set(existing_jobs.keys())

    new_content = original
    appended_blocks: list[tuple[str, str]] = []  # (job_id, source_file)

    for job_id, job_text, source_file in jobs_to_append:
        # Resolve ID conflicts
        new_id = job_id
        counter = 2
        while new_id in existing_ids or any(new_id == a[0] for a in appended_blocks):
            new_id = f"{job_id}_{counter}"
            counter += 1

        # Rename if needed
        if new_id != job_id:
            job_text = rename_job_in_text(job_text, job_id, new_id)

        # Add migration comment
        job_text = add_migration_comment(job_text, source_file)

        # Append with separator
        new_content += "\n" + job_text + "\n"
        appended_blocks.append((new_id, source_file))

    return new_content, appended_blocks


# ═══════════════════════════════════════════════════════════════════════
# VERSION FIXES (text-based, preserves formatting)
# ═══════════════════════════════════════════════════════════════════════

def apply_version_fixes(yaml_text: str) -> tuple[str, list[str]]:
    """Apply action version standardization via regex. Preserves all formatting."""
    fixes_applied: list[str] = []
    fixed = yaml_text
    for pattern, replacement in ACTION_VERSION_FIXES:
        new_fixed, count = re.subn(pattern, replacement, fixed)
        if count > 0:
            fixes_applied.append(f"Replaced {count}x: {pattern} → {replacement}")
            fixed = new_fixed
    return (fixed, fixes_applied)


# ═══════════════════════════════════════════════════════════════════════
# ARCHIVE
# ═══════════════════════════════════════════════════════════════════════

def archive_workflow(source_file: Path, archive_dir: Path, apply: bool) -> bool:
    if not source_file.exists():
        return False
    archive_dir.mkdir(parents=True, exist_ok=True)
    target = archive_dir / source_file.name
    if target.exists():
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
        prog="consolidate_cicd_v2",
        description="Eco Nojin Phase 2.1: Smart CI/CD consolidator (text-based, preserves formatting).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--root", type=str, default=".", help="Repo root")
    parser.add_argument("--apply", action="store_true", help="Actually modify files")
    parser.add_argument("--only", type=str, default=None, help="Process only these redundant files")
    parser.add_argument("--skip", type=str, default=None, help="Skip these redundant files")
    parser.add_argument("--report", type=str, default="consolidation_report_v2.json")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    if not HAS_YAML:
        print("Error: PyYAML required. Install: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    root = Path(args.root).expanduser().resolve()
    workflows_dir = root / ".github" / "workflows"
    archive_dir = workflows_dir / ".archived"

    if not workflows_dir.exists():
        print(f"Error: .github/workflows/ not found at: {workflows_dir}", file=sys.stderr)
        sys.exit(1)

    only_set = {s.strip() for s in args.only.split(",")} if args.only else None
    skip_set = {s.strip() for s in args.skip.split(",")} if args.skip else set()

    mode_label = "APPLY" if args.apply else "DRY-RUN (pass --apply to execute)"
    print("=" * 78)
    print("  Eco Nojin — Phase 2.1: Smart CI/CD Consolidator v2 (TEXT-BASED)")
    print(f"  Mode: {mode_label}")
    print(f"  Root: {root}")
    print("=" * 78)
    print()

    report = ConsolidationReport(
        root=str(root),
        mode="apply" if args.apply else "dry-run",
        executed_at=datetime.now().isoformat(timespec="seconds"),
    )

    current_workflows = sorted(
        list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    )
    report.total_workflows_before = len(current_workflows)

    # Step 1: Verify keep files exist
    print("  [1/4] Verifying keep workflows exist...")
    keep_files = set(KEEP_WORKFLOWS.values())
    for kf in keep_files:
        path = workflows_dir / kf
        if path.exists():
            report.files_kept.append(kf)
            if args.verbose:
                print(f"    ✓ {kf}")
        else:
            print(f"    ⚠ Missing: {kf}")
    print()

    # Step 2: Process each redundant file
    print("  [2/4] Processing redundant workflows (TEXT-BASED, preserves formatting)...")
    # Group migrations by keep file
    migrations_by_keep: dict[str, list[tuple[str, str, str]]] = {}  # keep_file → [(job_id, job_text, source)]

    for redundant_name, keep_name in ARCHIVE_PLAN.items():
        if only_set and redundant_name not in only_set:
            continue
        if redundant_name in skip_set:
            continue

        redundant_path = workflows_dir / redundant_name
        if not redundant_path.exists():
            if args.verbose:
                print(f"    ⊘ {redundant_name} — not found")
            continue

        # Parse for job inspection (read-only)
        redundant_parsed = load_yaml(redundant_path)
        if redundant_parsed is None:
            report.parse_errors.append(redundant_name)
            print(f"    ⚠ {redundant_name} — parse error, archiving without migration")
            if archive_workflow(redundant_path, archive_dir, args.apply):
                report.files_archived.append(redundant_name)
            continue

        source_jobs = extract_jobs(redundant_parsed)
        if not source_jobs:
            print(f"    ⊘ {redundant_name} — no jobs, archiving")
            if archive_workflow(redundant_path, archive_dir, args.apply):
                report.files_archived.append(redundant_name)
            continue

        # Load keep file's parsed jobs for duplicate detection
        keep_path = workflows_dir / keep_name
        keep_parsed = load_yaml(keep_path)
        if keep_parsed is None:
            print(f"    ⚠ {redundant_name} → {keep_name}: keep parse error, skipping")
            report.errors.append(f"{redundant_name}: keep file parse error")
            continue

        target_jobs = extract_jobs(keep_parsed)
        unique_jobs = find_unique_jobs(source_jobs, target_jobs)

        if unique_jobs:
            # Extract raw text blocks from the redundant file
            redundant_text = redundant_path.read_text(encoding="utf-8-sig", errors="ignore")
            job_text_blocks = extract_job_text_blocks(redundant_text)

            print(f"    📦 {redundant_name} → {keep_name}: "
                  f"migrating {len(unique_jobs)} unique job(s)")

            for job_id, job_def, reason in unique_jobs:
                if args.verbose:
                    print(f"       • {job_id}: {reason[:70]}")
                # Get the raw text block for this job
                if job_id in job_text_blocks:
                    migrations_by_keep.setdefault(keep_name, []).append(
                        (job_id, job_text_blocks[job_id], redundant_name)
                    )
                    report.jobs_migrated.append(JobMigration(
                        source_file=redundant_name,
                        job_id=job_id,
                        job_name=job_def.get("name", job_id),
                        reason=reason,
                    ))
                else:
                    print(f"       ⚠ {job_id}: could not extract text block, skipping")
        else:
            print(f"    📦 {redundant_name} → {keep_name}: no unique jobs, archiving")

        # Archive the redundant file
        if archive_workflow(redundant_path, archive_dir, args.apply):
            report.files_archived.append(redundant_name)
            if args.verbose:
                print(f"    → archived to .archived/{redundant_name}")
    print()

    # Step 3: Append migrated jobs to each keep file (TEXT-BASED)
    print("  [3/4] Appending migrated jobs to keep workflows (text-based)...")
    for keep_name, jobs_to_append in migrations_by_keep.items():
        keep_path = workflows_dir / keep_name
        if not keep_path.exists():
            continue

        # Read original content
        original = keep_path.read_text(encoding="utf-8-sig", errors="ignore")

        # Append jobs
        new_content, appended = append_jobs_to_keep_file(keep_path, jobs_to_append)

        # Apply version fixes to the COMBINED content
        new_content, version_fixes = apply_version_fixes(new_content)
        report.version_fixes_applied.extend(version_fixes)

        # Also apply version fixes to the ORIGINAL content (for jobs that were already there)
        # Actually, we already applied to combined, so original is covered.

        if args.apply:
            # Backup
            backup_path = keep_path.with_suffix(
                f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
            )
            shutil.copy2(keep_path, backup_path)
            # Write
            keep_path.write_text(new_content, encoding="utf-8")
            report.files_modified.append(keep_name)
            print(f"    ✓ {keep_name}: appended {len(appended)} job(s), "
                  f"{len(version_fixes)} version fix(es), backup: {backup_path.name}")
            if args.verbose:
                for jid, src in appended:
                    print(f"       • {jid} (from {src})")
                for vf in version_fixes:
                    print(f"       • fix: {vf}")
        else:
            print(f"    📝 {keep_name}: would append {len(appended)} job(s), "
                  f"{len(version_fixes)} version fix(es)")
    print()

    # Step 4: Apply version fixes to keep files that weren't modified above
    print("  [4/4] Applying version fixes to remaining keep workflows...")
    for keep_name in report.files_kept:
        if keep_name in report.files_modified:
            continue  # Already processed
        keep_path = workflows_dir / keep_name
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
                backup_path = keep_path.with_suffix(
                    f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yml"
                )
                shutil.copy2(keep_path, backup_path)
                keep_path.write_text(fixed, encoding="utf-8")
            report.version_fixes_applied.extend(fixes)
            if keep_name not in report.files_modified:
                report.files_modified.append(keep_name)
    print()

    # Summary
    if args.apply:
        final_workflows = sorted(
            list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        )
        report.total_workflows_after = len(final_workflows)
    else:
        report.total_workflows_after = (
            report.total_workflows_before - len(report.files_archived)
        )

    print("=" * 78)
    print("  SUMMARY")
    print("=" * 78)
    print(f"  Before: {report.total_workflows_before} workflows")
    print(f"  After:  {report.total_workflows_after} workflows")
    print(f"  Archived: {len(report.files_archived)}")
    print(f"  Modified: {len(report.files_modified)}")
    print(f"  Jobs migrated: {len(report.jobs_migrated)}")
    print(f"  Version fixes: {len(report.version_fixes_applied)}")
    if report.parse_errors:
        print(f"  Parse errors: {len(report.parse_errors)}")
    if report.errors:
        print(f"  Errors: {len(report.errors)}")
    print()

    if report.files_archived:
        print(f"  Archived ({len(report.files_archived)}):")
        for f in report.files_archived:
            print(f"    📦 {f}")
    if report.jobs_migrated:
        print(f"  Jobs migrated ({len(report.jobs_migrated)}):")
        for m in report.jobs_migrated:
            print(f"    • {m.source_file} :: {m.job_id}")
    if not args.apply:
        print()
        print("  ⚠ DRY-RUN. To execute:")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())

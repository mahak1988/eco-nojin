#!/usr/bin/env python3
"""
Eco Nojin — Phase 2.1: CI/CD Workflow Analyzer
=================================================
Analyzes all GitHub Actions workflows in .github/workflows/*.yml and
reports:
  - Each workflow's name, triggers, jobs, runner OS, and steps
  - Functionally duplicated workflows (same trigger + similar jobs)
  - Estimated monthly GitHub Actions minutes (rough)
  - Recommended consolidation plan

The script is read-only: it never modifies workflow files.

Dependencies:
  - PyYAML (for parsing YAML) — falls back to a basic parser if unavailable

Usage:
    python3 analyze_cicd.py                          # scan repo at cwd
    python3 analyze_cicd.py --root D:\\econojin.com  # custom repo
    python3 analyze_cicd.py --json                   # JSON output
    python3 analyze_cicd.py --verbose                # show all jobs/steps
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────
# YAML PARSING — prefer PyYAML, fall back to basic parser
# ─────────────────────────────────────────────────────────────────────

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


def parse_yaml(text: str) -> Optional[dict]:
    """Parse YAML text. Returns None if parsing fails."""
    if HAS_YAML:
        try:
            # Use utf-8-sig to strip BOM if present
            return yaml.safe_load(text)
        except yaml.YAMLError:
            return None
    else:
        # Very basic fallback: just extract top-level keys
        # This won't handle nested structures properly, but it's better than nothing.
        result: dict = {}
        try:
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                # Match "key: value" or "key:"
                m = re.match(r'^(\w[\w-]*)\s*:\s*(.*)$', stripped)
                if m:
                    key = m.group(1)
                    value = m.group(2).strip()
                    if not value:
                        result[key] = {}  # nested
                    else:
                        result[key] = value
            return result
        except Exception:
            return None


# ─────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ─────────────────────────────────────────────────────────────────────

@dataclass
class JobInfo:
    name: str
    runs_on: str = ""
    steps_count: int = 0
    step_names: list = field(default_factory=list)
    needs: list = field(default_factory=list)  # job dependencies


@dataclass
class WorkflowInfo:
    file_name: str               # e.g. "01-ci-main.yml"
    file_path: str               # relative path
    name: str = ""               # workflow "name:" field
    triggers: list = field(default_factory=list)  # ["push", "pull_request", "workflow_dispatch", ...]
    trigger_branches: list = field(default_factory=list)  # branches filter
    jobs: list = field(default_factory=list)  # list of JobInfo
    total_steps: int = 0
    size_bytes: int = 0
    line_count: int = 0
    has_secrets: bool = False
    uses_actions: list = field(default_factory=list)  # third-party actions used
    parse_error: str = ""


@dataclass
class DuplicateGroup:
    purpose: str                  # inferred purpose: "CI", "Quality Gate", etc.
    workflows: list = field(default_factory=list)  # list of file_names
    recommended_keep: str = ""    # which one to keep
    reason: str = ""              # why this one


# ─────────────────────────────────────────────────────────────────────
# CORE ANALYZER
# ─────────────────────────────────────────────────────────────────────

# Patterns to infer workflow purpose from filename or "name:" field
PURPOSE_PATTERNS = [
    (re.compile(r'\b(ci|continuous.integration|build|test)\b', re.IGNORECASE), "CI"),
    (re.compile(r'\b(quality|lint|check|gate)\b', re.IGNORECASE), "Quality Gate"),
    (re.compile(r'\b(security|scan|sast|dependabot)\b', re.IGNORECASE), "Security Scan"),
    (re.compile(r'\b(deploy|cd|release|publish)\b', re.IGNORECASE), "Deploy"),
    (re.compile(r'\b(schedule|cron|nightly)\b', re.IGNORECASE), "Scheduled"),
]


def infer_purpose(workflow: WorkflowInfo) -> str:
    """Guess the workflow's purpose from filename + name."""
    text = f"{workflow.file_name} {workflow.name}".lower()
    for pattern, label in PURPOSE_PATTERNS:
        if pattern.search(text):
            return label
    # Fallback: look at triggers
    if "schedule" in workflow.triggers:
        return "Scheduled"
    if "workflow_dispatch" in workflow.triggers and not workflow.triggers:
        return "Manual"
    return "Unknown"


def extract_triggers(parsed: dict) -> tuple[list[str], list[str]]:
    """Extract trigger types and branch filters from parsed YAML."""
    triggers: list[str] = []
    branches: list[str] = []
    on = parsed.get("on", parsed.get(True, {}))  # "on" can be parsed as True (YAML 1.1)
    if isinstance(on, str):
        triggers.append(on)
    elif isinstance(on, list):
        triggers.extend(str(t) for t in on)
    elif isinstance(on, dict):
        for key in on.keys():
            triggers.append(str(key))
            # Extract branch filters
            if key in ("push", "pull_request") and isinstance(on[key], dict):
                br = on[key].get("branches", [])
                if isinstance(br, list):
                    branches.extend(str(b) for b in br)
                elif isinstance(br, str):
                    branches.append(br)
    return triggers, branches


def extract_jobs(parsed: dict) -> list[JobInfo]:
    """Extract job info from parsed YAML."""
    jobs: list[JobInfo] = []
    jobs_dict = parsed.get("jobs", {})
    if not isinstance(jobs_dict, dict):
        return jobs
    for job_id, job_def in jobs_dict.items():
        if not isinstance(job_def, dict):
            continue
        info = JobInfo(name=str(job_id))
        info.runs_on = str(job_def.get("runs-on", ""))
        # Steps
        steps = job_def.get("steps", [])
        if isinstance(steps, list):
            info.steps_count = len(steps)
            for step in steps:
                if isinstance(step, dict):
                    # Step name (could be in "name:" or inferred from "uses:"/"run:")
                    step_name = step.get("name", "")
                    if not step_name:
                        if "uses" in step:
                            step_name = f"uses: {step['uses']}"
                        elif "run" in step:
                            run_cmd = str(step["run"]).split("\n")[0][:60]
                            step_name = f"run: {run_cmd}"
                    info.step_names.append(step_name)
        # Dependencies
        needs = job_def.get("needs", [])
        if isinstance(needs, str):
            info.needs = [needs]
        elif isinstance(needs, list):
            info.needs = [str(n) for n in needs]
        jobs.append(info)
    return jobs


def extract_uses(workflow_text: str) -> list[str]:
    """Extract all 'uses: action@version' references from raw YAML text."""
    # Match: uses: owner/repo@version  OR  uses: ./local-action
    pattern = re.compile(r'^\s*-?\s*uses:\s+([^\s]+)', re.MULTILINE)
    matches = pattern.findall(workflow_text)
    # Dedupe while preserving order
    seen = set()
    result = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            result.append(m)
    return result


def analyze_workflow(file_path: Path, root: Path) -> WorkflowInfo:
    """Parse and analyze a single workflow file."""
    rel_path = str(file_path.relative_to(root)).replace("\\", "/")
    info = WorkflowInfo(
        file_name=file_path.name,
        file_path=rel_path,
    )
    try:
        text = file_path.read_text(encoding="utf-8-sig", errors="ignore")
    except OSError as e:
        info.parse_error = f"read error: {e}"
        return info

    info.size_bytes = len(text.encode("utf-8"))
    info.line_count = text.count("\n") + 1
    info.has_secrets = "${{ secrets." in text or "${{secrets." in text
    info.uses_actions = extract_uses(text)

    parsed = parse_yaml(text)
    if parsed is None:
        info.parse_error = "YAML parse failed (install PyYAML for accurate parsing)"
        return info
    if not isinstance(parsed, dict):
        info.parse_error = "top-level YAML is not a dict"
        return info

    info.name = str(parsed.get("name", ""))
    info.triggers, info.trigger_branches = extract_triggers(parsed)
    info.jobs = extract_jobs(parsed)
    info.total_steps = sum(j.steps_count for j in info.jobs)

    return info


def find_duplicates(workflows: list[WorkflowInfo]) -> list[DuplicateGroup]:
    """Group workflows that appear to serve the same purpose."""
    groups: dict[str, list[WorkflowInfo]] = defaultdict(list)
    for w in workflows:
        purpose = infer_purpose(w)
        groups[purpose].append(w)

    duplicates: list[DuplicateGroup] = []
    for purpose, ws in groups.items():
        if len(ws) < 2:
            continue
        # Among workflows of the same purpose, find which one to keep
        # Heuristic: prefer numbered filenames (01-, 02-) — they suggest intentional ordering
        # If no numbered, prefer the one with the most jobs (likely most complete)
        def sort_key(w: WorkflowInfo) -> tuple:
            has_number_prefix = bool(re.match(r'^\d+-', w.file_name))
            # Sort: numbered first (lower number = higher priority), then by name
            num_match = re.match(r'^(\d+)-', w.file_name)
            num = int(num_match.group(1)) if num_match else 999
            return (0 if has_number_prefix else 1, num, w.file_name)

        sorted_ws = sorted(ws, key=sort_key)
        keep = sorted_ws[0]
        dup = DuplicateGroup(
            purpose=purpose,
            workflows=[w.file_name for w in sorted_ws],
            recommended_keep=keep.file_name,
            reason=(
                f"Numbered filename ({keep.file_name}) suggests intentional ordering; "
                f"keep this one and consolidate others into it."
                if re.match(r'^\d+-', keep.file_name)
                else f"Most complete workflow ({len(keep.jobs)} jobs, {keep.total_steps} steps)."
            ),
        )
        duplicates.append(dup)

    return sorted(duplicates, key=lambda d: d.purpose)


def estimate_minutes(w: WorkflowInfo) -> int:
    """Rough estimate of monthly minutes for this workflow.

    Assumptions:
      - push trigger: 30 runs/month per active branch
      - pull_request: 20 runs/month
      - schedule: 30 runs/month (daily) or 4 (weekly)
      - workflow_dispatch: 5 runs/month (manual)
      - Each job runs for ~3 minutes on average
    """
    runs_per_month = 0
    for trigger in w.triggers:
        if trigger == "push":
            runs_per_month += 30
        elif trigger == "pull_request":
            runs_per_month += 20
        elif trigger == "schedule":
            runs_per_month += 30  # assume daily
        elif trigger == "workflow_dispatch":
            runs_per_month += 5
        elif trigger == "release":
            runs_per_month += 2
    # Multiply by job count × avg 3 min per job
    return runs_per_month * len(w.jobs) * 3


# ─────────────────────────────────────────────────────────────────────
# OUTPUT FORMATTERS
# ─────────────────────────────────────────────────────────────────────

def format_text_report(workflows: list[WorkflowInfo],
                        duplicates: list[DuplicateGroup],
                        root: Path) -> str:
    out: list[str] = []
    bar = "═" * 78

    out.append(bar)
    out.append("  Eco Nojin — Phase 2.1: CI/CD Workflow Analyzer")
    out.append(bar)
    out.append(f"  Repo root       : {root}")
    out.append(f"  Workflows found : {len(workflows)}")
    out.append(f"  YAML parser     : {'PyYAML (accurate)' if HAS_YAML else 'fallback (limited)'}")
    out.append(f"  Analyzed at     : {datetime.now().isoformat(timespec='seconds')}")
    out.append("")

    # ── Workflow inventory
    out.append("─" * 78)
    out.append("  1. WORKFLOW INVENTORY")
    out.append("─" * 78)
    out.append(f"  {'File':<35} {'Name':<25} {'Triggers':<20} {'Jobs':>5} {'Steps':>6}")
    out.append(f"  {'-'*35} {'-'*25} {'-'*20} {'-'*5} {'-'*6}")
    for w in sorted(workflows, key=lambda x: x.file_name):
        triggers_str = ",".join(w.triggers[:3]) if w.triggers else "(none)"
        if len(w.triggers) > 3:
            triggers_str += f"+{len(w.triggers)-3}"
        name_short = (w.name[:23] + "..") if len(w.name) > 25 else w.name
        out.append(f"  {w.file_name:<35} {name_short:<25} {triggers_str:<20} {len(w.jobs):>5} {w.total_steps:>6}")
        if w.parse_error:
            out.append(f"    ! parse error: {w.parse_error}")
    out.append("")

    # ── Triggers summary
    out.append("─" * 78)
    out.append("  2. TRIGGER ANALYSIS")
    out.append("─" * 78)
    trigger_counts: dict[str, int] = defaultdict(int)
    for w in workflows:
        for t in w.triggers:
            trigger_counts[t] += 1
    out.append(f"  {'Trigger':<25} {'Workflows using it':>20}")
    out.append(f"  {'-'*25} {'-'*20}")
    for trig, count in sorted(trigger_counts.items(), key=lambda x: -x[1]):
        out.append(f"  {trig:<25} {count:>20}")
    out.append("")

    # ── Duplicate groups
    out.append("─" * 78)
    out.append("  3. DUPLICATE WORKFLOWS (same purpose)")
    out.append("─" * 78)
    if not duplicates:
        out.append("  No duplicates found.")
    else:
        total_redundant = sum(len(d.workflows) - 1 for d in duplicates)
        out.append(f"  Found {len(duplicates)} group(s) with {total_redundant} redundant workflow(s).")
        out.append("")
        for d in duplicates:
            out.append(f"  📦 {d.purpose}")
            for wf in d.workflows:
                marker = "★" if wf == d.recommended_keep else "✗"
                out.append(f"     {marker} {wf}")
            out.append(f"     → Keep: {d.recommended_keep}")
            out.append(f"     Reason: {d.reason}")
            out.append("")

    # ── Actions used
    out.append("─" * 78)
    out.append("  4. THIRD-PARTY ACTIONS USED")
    out.append("─" * 78)
    action_counts: dict[str, list[str]] = defaultdict(list)
    for w in workflows:
        for action in w.uses_actions:
            action_counts[action].append(w.file_name)
    if action_counts:
        out.append(f"  {'Action':<45} {'Used in':>10}")
        out.append(f"  {'-'*45} {'-'*10}")
        for action in sorted(action_counts.keys()):
            users = action_counts[action]
            out.append(f"  {action:<45} {len(users):>3} workflow(s)")
    else:
        out.append("  No third-party actions found.")
    out.append("")

    # ── Estimated minutes
    out.append("─" * 78)
    out.append("  5. ESTIMATED MONTHLY GitHub Actions MINUTES (rough)")
    out.append("─" * 78)
    total_min = 0
    out.append(f"  {'File':<35} {'Est. min/month':>15}")
    out.append(f"  {'-'*35} {'-'*15}")
    for w in sorted(workflows, key=lambda x: -estimate_minutes(x)):
        mins = estimate_minutes(w)
        total_min += mins
        out.append(f"  {w.file_name:<35} {mins:>15}")
    out.append(f"  {'TOTAL':<35} {total_min:>15}")
    out.append("")

    # ── Consolidation plan
    out.append("─" * 78)
    out.append("  6. RECOMMENDED CONSOLIDATION PLAN")
    out.append("─" * 78)
    if duplicates:
        kept = [d.recommended_keep for d in duplicates]
        non_dup = [w for w in workflows if not any(w.file_name in d.workflows for d in duplicates)]
        out.append(f"  Target: {len(kept) + len(non_dup)} workflows (down from {len(workflows)})")
        out.append("")
        out.append("  KEEP:")
        for w in workflows:
            if w.file_name in kept or not any(w.file_name in d.workflows for d in duplicates):
                purpose = infer_purpose(w)
                out.append(f"    ✓ {w.file_name:<35} ({purpose})")
        out.append("")
        out.append("  CONSOLIDATE INTO:")
        for d in duplicates:
            for wf in d.workflows:
                if wf != d.recommended_keep:
                    out.append(f"    ✗ {wf:<35} → merge into {d.recommended_keep}")
        out.append("")
        # Estimated savings
        saved_min = sum(
            estimate_minutes(next(w for w in workflows if w.file_name == wf))
            for d in duplicates
            for wf in d.workflows if wf != d.recommended_keep
        )
        out.append(f"  Estimated savings: ~{saved_min} minutes/month "
                   f"({saved_min * 100 // max(total_min, 1)}% of total)")
    else:
        out.append(f"  No consolidation needed. All {len(workflows)} workflows are unique.")
    out.append("")

    out.append(bar)
    out.append("  End of report — this script is READ-ONLY. No files were modified.")
    out.append(bar)
    return "\n".join(out)


# ─────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog="analyze_cicd",
        description="Eco Nojin Phase 2.1: Analyze GitHub Actions workflows for duplication.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--root", type=str, default=".",
        help="Path to the repo root (default: current directory)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of text",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show all jobs and steps for each workflow",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write report to this file (default: stdout)",
    )
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        print(f"Error: .github/workflows/ not found at: {workflows_dir}", file=sys.stderr)
        sys.exit(1)

    # Find all .yml and .yaml files
    workflow_files = sorted(
        list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    )
    if not workflow_files:
        print(f"No workflow files found in {workflows_dir}", file=sys.stderr)
        sys.exit(1)

    # Analyze each
    workflows: list[WorkflowInfo] = []
    for wf_path in workflow_files:
        workflows.append(analyze_workflow(wf_path, root))

    # Find duplicates
    duplicates = find_duplicates(workflows)

    # Output
    if args.json:
        output = {
            "tool": "analyze_cicd.py",
            "analyzed_at": datetime.now().isoformat(timespec="seconds"),
            "root": str(root),
            "yaml_parser": "PyYAML" if HAS_YAML else "fallback",
            "workflows": [asdict(w) for w in workflows],
            "duplicates": [asdict(d) for d in duplicates],
            "total_workflows": len(workflows),
            "total_redundant": sum(len(d.workflows) - 1 for d in duplicates),
            "estimated_total_minutes_per_month": sum(estimate_minutes(w) for w in workflows),
        }
        text = json.dumps(output, indent=2, ensure_ascii=False, default=str)
    else:
        text = format_text_report(workflows, duplicates, root)
        if args.verbose:
            text += "\n\n"
            text += "═" * 78 + "\n"
            text += "  VERBOSE: ALL JOBS AND STEPS\n"
            text += "═" * 78 + "\n\n"
            for w in workflows:
                text += f"  ─── {w.file_name} ───\n"
                text += f"  Name: {w.name}\n"
                text += f"  Triggers: {', '.join(w.triggers) or '(none)'}\n"
                if w.trigger_branches:
                    text += f"  Branches: {', '.join(w.trigger_branches)}\n"
                text += f"  Uses secrets: {w.has_secrets}\n"
                if w.uses_actions:
                    text += f"  Actions used:\n"
                    for a in w.uses_actions:
                        text += f"    - {a}\n"
                text += f"  Jobs ({len(w.jobs)}):\n"
                for j in w.jobs:
                    text += f"    • {j.name} (runs-on: {j.runs_on or '?'}, steps: {j.steps_count})"
                    if j.needs:
                        text += f" [needs: {', '.join(j.needs)}]"
                    text += "\n"
                    for step in j.step_names:
                        text += f"        - {step}\n"
                text += "\n"

    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(text)

    return 0


if __name__ == "__main__":
    sys.exit(main())

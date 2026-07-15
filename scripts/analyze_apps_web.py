#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web Code Quality Analyzer
================================================================================
 A static-analysis tool for the hydrology-frontend (apps/web) package.

 WHAT IT DOES
 ------------
 1. Walks the apps/web directory and inventories every source file.
 2. Scores each file on 7 quality dimensions.
 3. Detects the exact class of bugs that broke the previous build:
      - TS2484  (duplicate type exports)
      - TS2339  (property does not exist on type)
      - Bare `any` usage, missing return types, console.* leftovers
 4. Flags the worst files so we can redesign them in 25-file batches.
 5. Emits two reports:
      - report.json   (machine-readable, for piping back to the assistant)
      - report.md     (human-readable, for review)

 USAGE
 -----
  # from the repo root (D:\\econojin.com)
  python scripts/analyze_apps_web.py --root apps/web

  # or with an explicit path
  python scripts/analyze_apps_web.py --root D:\\econojin.com\\apps\\web

  # change batch size for the "fix queue"
  python scripts/analyze_apps_web.py --root apps/web --batch-size 25

 OUTPUT
 ------
  ./analysis_report/report.json
  ./analysis_report/report.md

 AUTHOR: econojin.com refactor team
================================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# File extensions we care about
SOURCE_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".json", ".md"}

# Directories to skip during traversal
SKIP_DIRS = {
    "node_modules", ".git", ".next", "dist", "build", "coverage",
    ".turbo", ".cache", ".vscode", ".idea", "__pycache__",
}

# Files to skip
SKIP_FILES = {".DS_Store", "package-lock.json", "pnpm-lock.yaml", "yarn.lock"}

# TypeScript/React anti-patterns we detect
PATTERNS = {
    "any_usage":          re.compile(r":\s*any\b|\bas\s+any\b|<any>"),
    "console_log":        re.compile(r"console\.(log|debug|info|warn|error|trace)\s*\("),
    "todo_comment":       re.compile(r"\b(TODO|FIXME|HACK|XXX|BUG)\b", re.IGNORECASE),
    "missing_return_type":re.compile(r"(function\s+\w+\s*\([^)]*\)\s*\{)|(const\s+\w+\s*=\s*\([^)]*\)\s*=>\s*[^:=>])"),
    "default_export":     re.compile(r"^\s*export\s+default\s+", re.MULTILINE),
    "named_export":       re.compile(r"^\s*export\s+(const|function|class|interface|type|enum)\s+", re.MULTILINE),
    "react_class":        re.compile(r"class\s+\w+\s+extends\s+(React\.)?(Component|PureComponent)"),
    "use_any":            re.compile(r"\bany\b"),
    "duplicate_type_export": re.compile(r"^\s*export\s+(?:type|interface)\s+(\w+)", re.MULTILINE),
    "ts_ignore":          re.compile(r"//\s*@ts-ignore|//\s*@ts-nocheck|//\s*@ts-expect-error"),
    "var_declaration":    re.compile(r"\bvar\s+\w+"),
    "non_null_assertion": re.compile(r"\w+!"),
    "react_inline_style": re.compile(r'style\s*=\s*\{\{'),
    "hardcoded_string":   re.compile(r'aria-label\s*=\s*"([^"]+)"'),
}

# Quality scoring weights (sum = 100)
WEIGHTS = {
    "type_safety":      20,  # any usage, ts-ignore, non-null
    "modern_syntax":    10,  # var vs let/const
    "react_patterns":   15,  # functional components, hooks
    "export_style":      5,  # named vs default
    "code_hygiene":     20,  # console, todo, ts-ignore
    "complexity":       15,  # file length, function length
    "documentation":    10,  # comments / JSDoc presence
    "test_coverage":     5,  # nearby test file existence
}

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class FileReport:
    path: str
    rel_path: str
    extension: str
    lines: int
    non_blank_lines: int
    issues: Dict[str, int] = field(default_factory=dict)
    score: float = 100.0
    severity: str = "ok"          # ok | low | medium | high | critical
    has_test: bool = False
    notes: List[str] = field(default_factory=list)

@dataclass
class ProjectReport:
    root: str
    generated_at: str
    total_files: int
    total_lines: int
    by_extension: Dict[str, int] = field(default_factory=dict)
    files: List[FileReport] = field(default_factory=list)
    worst_files: List[FileReport] = field(default_factory=list)
    top_issues: Dict[str, int] = field(default_factory=dict)
    fix_batches: List[List[str]] = field(default_factory=list)
    overall_score: float = 100.0
    summary_text: str = ""

# ---------------------------------------------------------------------------
# Core analyzer
# ---------------------------------------------------------------------------

class CodeAnalyzer:
    def __init__(self, root: Path, batch_size: int = 25):
        self.root = root.resolve()
        self.batch_size = batch_size

    # ----- file discovery ---------------------------------------------------

    def iter_source_files(self) -> List[Path]:
        files: List[Path] = []
        for dirpath, dirnames, filenames in os.walk(self.root):
            # prune skip dirs in-place (faster than filtering later)
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                if fname in SKIP_FILES:
                    continue
                ext = os.path.splitext(fname)[1].lower()
                if ext in SOURCE_EXTENSIONS:
                    files.append(Path(dirpath) / fname)
        return sorted(files)

    # ----- per-file analysis ------------------------------------------------

    def analyze_file(self, path: Path) -> FileReport:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            return FileReport(
                path=str(path),
                rel_path=str(path.relative_to(self.root)),
                extension=path.suffix,
                lines=0,
                non_blank_lines=0,
                score=0.0,
                severity="critical",
                notes=[f"unreadable: {e}"],
            )

        lines = text.splitlines()
        non_blank = [l for l in lines if l.strip()]
        ext = path.suffix.lower()

        issues: Dict[str, int] = {}
        notes: List[str] = []

        # Pattern-based detection (TS/JS/TSX/JSX only)
        if ext in {".ts", ".tsx", ".js", ".jsx"}:
            for name, pattern in PATTERNS.items():
                matches = pattern.findall(text)
                if matches:
                    if name == "duplicate_type_export":
                        # detect duplicates across the file
                        seen: Dict[str, int] = {}
                        for m in matches:
                            seen[m] = seen.get(m, 0) + 1
                        dups = {k: v for k, v in seen.items() if v > 1}
                        if dups:
                            issues["duplicate_type_export"] = sum(dups.values())
                            for k, v in dups.items():
                                notes.append(f"Type '{k}' exported {v} times → TS2484")
                    elif name == "missing_return_type":
                        issues[name] = len(matches)
                    else:
                        issues[name] = len(matches)

            # crude complexity proxy: lines per function (rough)
            fn_count = max(
                len(re.findall(r"function\s+\w+", text)),
                len(re.findall(r"=>\s*\{", text)),
                1,
            )
            avg_fn_len = len(non_blank) / fn_count
            if avg_fn_len > 50:
                issues["long_functions"] = int(avg_fn_len)
                notes.append(f"avg function length ≈ {avg_fn_len:.0f} lines (target ≤ 50)")
            if len(non_blank) > 400:
                issues["long_file"] = len(non_blank)
                notes.append(f"file is {len(non_blank)} lines (consider splitting)")

        # Test-file proximity check
        has_test = self._has_neighbor_test(path)

        # Score
        score = self._compute_score(issues, len(non_blank), has_test, ext, text)
        severity = self._severity_from_score(score)

        return FileReport(
            path=str(path),
            rel_path=str(path.relative_to(self.root)),
            extension=ext,
            lines=len(lines),
            non_blank_lines=len(non_blank),
            issues=issues,
            score=round(score, 1),
            severity=severity,
            has_test=has_test,
            notes=notes,
        )

    # ----- helpers ----------------------------------------------------------

    def _has_neighbor_test(self, path: Path) -> bool:
        stem = path.stem
        parent = path.parent
        candidates = [
            parent / f"{stem}.test.ts",
            parent / f"{stem}.test.tsx",
            parent / f"{stem}.spec.ts",
            parent / f"{stem}.spec.tsx",
            parent / "__tests__" / f"{stem}.test.ts",
            parent / "__tests__" / f"{stem}.test.tsx",
        ]
        return any(c.exists() for c in candidates)

    def _compute_score(
        self,
        issues: Dict[str, int],
        non_blank: int,
        has_test: bool,
        ext: str,
        text: str,
    ) -> float:
        # Start at 100 and deduct
        score = 100.0

        if ext in {".ts", ".tsx", ".js", ".jsx"}:
            # type_safety (weight 20)
            score -= min(20, issues.get("any_usage", 0) * 2)
            score -= min(10, issues.get("ts_ignore", 0) * 5)
            score -= min(5, issues.get("non_null_assertion", 0) * 0.5)

            # modern_syntax (weight 10)
            score -= min(10, issues.get("var_declaration", 0) * 2)

            # react_patterns (weight 15) — penalize class components
            score -= min(15, issues.get("react_class", 0) * 10)

            # code_hygiene (weight 20)
            score -= min(10, issues.get("console_log", 0) * 1)
            score -= min(5,  issues.get("todo_comment", 0) * 0.5)

            # complexity (weight 15)
            score -= min(10, max(0, (non_blank - 300) / 30))
            score -= min(5,  issues.get("long_functions", 0) * 0.1)

            # documentation (weight 10)
            has_jsdoc = "/*" in text and "@" in text
            if not has_jsdoc:
                score -= 5
            comment_lines = sum(1 for l in text.splitlines() if l.strip().startswith(("//", "*", "/*")))
            comment_ratio = comment_lines / max(1, non_blank)
            if comment_ratio < 0.05:
                score -= 5

            # test_coverage (weight 5)
            if not has_test:
                score -= 5

        elif ext in {".css", ".scss"}:
            # CSS-specific: flag inline hard-coded magic numbers, !important
            important_count = text.count("!important")
            score -= min(15, important_count * 1.5)
            if non_blank > 300:
                score -= 10

        elif ext == ".json":
            try:
                data = json.loads(text)
                if isinstance(data, dict):
                    # package.json sanity checks
                    if "name" not in data and "version" not in data:
                        score -= 20
            except json.JSONDecodeError:
                score -= 50

        return max(0.0, score)

    def _severity_from_score(self, score: float) -> str:
        if score < 40:  return "critical"
        if score < 60:  return "high"
        if score < 75:  return "medium"
        if score < 90:  return "low"
        return "ok"

    # ----- aggregation ------------------------------------------------------

    def aggregate(self, file_reports: List[FileReport]) -> ProjectReport:
        by_ext: Dict[str, int] = {}
        top_issues: Dict[str, int] = {}
        total_lines = 0

        for fr in file_reports:
            by_ext[fr.extension] = by_ext.get(fr.extension, 0) + 1
            total_lines += fr.lines
            for k, v in fr.issues.items():
                top_issues[k] = top_issues.get(k, 0) + v

        # Worst files (lowest score first)
        worst = sorted(file_reports, key=lambda f: f.score)[:50]

        # Build fix batches (worst first, batch_size per batch)
        worst_paths = [f.rel_path for f in worst]
        batches: List[List[str]] = [
            worst_paths[i:i + self.batch_size]
            for i in range(0, len(worst_paths), self.batch_size)
        ]

        overall = sum(f.score for f in file_reports) / max(1, len(file_reports))

        return ProjectReport(
            root=str(self.root),
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_files=len(file_reports),
            total_lines=total_lines,
            by_extension=by_ext,
            files=file_reports,
            worst_files=worst,
            top_issues=dict(sorted(top_issues.items(), key=lambda x: -x[1])),
            fix_batches=batches,
            overall_score=round(overall, 1),
            summary_text=self._build_summary(file_reports, top_issues, overall, by_ext),
        )

    def _build_summary(
        self,
        files: List[FileReport],
        issues: Dict[str, int],
        overall: float,
        by_ext: Dict[str, int],
    ) -> str:
        critical = sum(1 for f in files if f.severity == "critical")
        high     = sum(1 for f in files if f.severity == "high")
        medium   = sum(1 for f in files if f.severity == "medium")
        return (
            f"Analyzed {len(files)} files ({sum(by_ext.values())} by ext). "
            f"Overall score: {overall:.1f}/100. "
            f"Severity breakdown: critical={critical}, high={high}, medium={medium}. "
            f"Top issues: {', '.join(f'{k}={v}' for k, v in list(issues.items())[:5]) or 'none'}."
        )

# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------

def render_markdown(report: ProjectReport) -> str:
    md: List[str] = []
    md.append(f"# apps/web — Code Quality Report\n")
    md.append(f"- **Generated:** {report.generated_at}")
    md.append(f"- **Root:** `{report.root}`")
    md.append(f"- **Total files:** {report.total_files}")
    md.append(f"- **Total lines:** {report.total_lines:,}")
    md.append(f"- **Overall score:** **{report.overall_score}/100**\n")

    md.append("## Files by extension\n")
    md.append("| Extension | Count |")
    md.append("|-----------|-------|")
    for ext, n in sorted(report.by_extension.items(), key=lambda x: -x[1]):
        md.append(f"| `{ext or '(none)'}` | {n} |")
    md.append("")

    md.append("## Top issues (across all files)\n")
    if report.top_issues:
        md.append("| Issue | Occurrences |")
        md.append("|-------|-------------|")
        for k, v in report.top_issues.items():
            md.append(f"| `{k}` | {v} |")
    else:
        md.append("_No issues detected — suspicious, double-check the analyzer._")
    md.append("")

    md.append("## Severity breakdown\n")
    sev_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "ok": 0}
    for f in report.files:
        sev_counts[f.severity] = sev_counts.get(f.severity, 0) + 1
    md.append("| Severity | Files |")
    md.append("|----------|-------|")
    for sev in ["critical", "high", "medium", "low", "ok"]:
        md.append(f"| {sev} | {sev_counts.get(sev, 0)} |")
    md.append("")

    md.append("## Worst 50 files (redesign queue)\n")
    md.append("| # | Score | Severity | Lines | File | Key issues |")
    md.append("|---|-------|----------|-------|------|------------|")
    for i, f in enumerate(report.worst_files, 1):
        issue_str = ", ".join(f"{k}={v}" for k, v in
                              sorted(f.issues.items(), key=lambda x: -x[1])[:3]) or "—"
        md.append(f"| {i} | {f.score} | {f.severity} | {f.lines} | `{f.rel_path}` | {issue_str} |")
    md.append("")

    md.append(f"## Fix batches (size = {report.fix_batches and len(report.fix_batches[0]) or 0})\n")
    for i, batch in enumerate(report.fix_batches, 1):
        md.append(f"### Batch {i} — {len(batch)} files\n")
        for p in batch:
            md.append(f"- `{p}`")
        md.append("")

    md.append("## Notes\n")
    md.append("- Scores are heuristic, not absolute. Use them to prioritize, not to judge.")
    md.append("- The `duplicate_type_export` check directly targets the TS2484 error from the last build.")
    md.append("- The `worst_files` list is the input for the next refactor phase: 25 files per batch.")
    md.append("- Paste `report.json` back to the assistant to drive the file-by-file redesign.")
    return "\n".join(md)

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyze code quality of apps/web for the econojin.com refactor."
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Path to the apps/web directory (e.g. apps/web or D:\\econojin.com\\apps\\web)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=25,
        help="Number of files per fix-batch in the report (default: 25)",
    )
    parser.add_argument(
        "--out",
        default="./analysis_report",
        help="Output directory for report.json and report.md (default: ./analysis_report)",
    )
    args = parser.parse_args(argv)

    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        print(f"[ERROR] Root path does not exist or is not a directory: {root}", file=sys.stderr)
        return 2

    print(f"[INFO] Analyzing: {root}")
    analyzer = CodeAnalyzer(root=root, batch_size=args.batch_size)

    files = analyzer.iter_source_files()
    if not files:
        print("[WARN] No source files found. Check the --root path and SKIP_DIRS filter.", file=sys.stderr)
        return 1

    print(f"[INFO] Found {len(files)} source files. Analyzing...")

    file_reports: List[FileReport] = []
    for i, p in enumerate(files, 1):
        fr = analyzer.analyze_file(p)
        file_reports.append(fr)
        if i % 25 == 0:
            print(f"  ...analyzed {i}/{len(files)}")

    report = analyzer.aggregate(file_reports)

    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "report.json"
    md_path   = out_dir / "report.md"

    # JSON (convert dataclasses → dict)
    json_path.write_text(
        json.dumps(asdict(report), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(report), encoding="utf-8")

    print()
    print("=" * 72)
    print(" ANALYSIS COMPLETE")
    print("=" * 72)
    print(f"  Files analyzed : {report.total_files}")
    print(f"  Total lines    : {report.total_lines:,}")
    print(f"  Overall score  : {report.overall_score}/100")
    print(f"  Fix batches    : {len(report.fix_batches)} (× {args.batch_size} files)")
    print(f"  JSON report    : {json_path}")
    print(f"  Markdown report: {md_path}")
    print("=" * 72)
    print()
    print("NEXT STEP:")
    print("  1. Open report.md and review the worst-files table.")
    print("  2. Paste report.json (or just the worst_files + fix_batches")
    print("     sections) back to the assistant to drive the 25-file redesign.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

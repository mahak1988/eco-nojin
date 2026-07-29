#!/usr/bin/env python3
"""
scan_i18n_issues.py — Phase P0, Step 1
========================================
Scans the entire repository for:
  1. Persian / Arabic / RTL script inside source-code comments (//, #, /* */, """ """)
  2. Persian / Arabic / RTL script inside Python / JS docstrings
  3. Hard-coded user-facing strings in JSX / TSX that should go through i18n
  4. Non-English content in README / docs / config files

Usage:
    python scripts/scan_i18n_issues.py

Output:
    - reports/i18n_scan_report.json   — machine-readable
    - reports/i18n_scan_report.md     — human-readable summary
"""

import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

ROOT = Path(__file__).resolve().parent.parent

EXCLUDE_DIRS: Set[str] = {
    ".git", ".github", ".venv", ".turbo", ".pnpm-store",
    ".mypy_cache", ".pytest_cache", ".security_backup",
    "__pycache__", "node_modules", "dist", "build", ".next",
    "cache", "artifacts", "typechain-types", ".zcode",
}

EXCLUDE_FILES: Set[str] = {
    "pnpm-lock.yaml", "package-lock.json", "yarn.lock",
    ".env", ".env.docker", "econojin.db",
}

SCAN_EXTENSIONS: Set[str] = {
    ".py", ".pyi", ".ts", ".tsx", ".js", ".jsx",
    ".html", ".css", ".scss",
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    ".md", ".rst", ".txt",
    ".sol", ".sh", ".ps1", ".bat",
}

RTL_RE = re.compile(
    "[\u0600-\u06FF"
    "\u0750-\u077F"
    "\u08A0-\u08FF"
    "\uFB50-\uFDFF"
    "\uFE70-\uFEFF"
    "]"
)

PERSIAN_DIGITS_RE = re.compile("[\u0660-\u0669\u06F0-\u06F9]")


def _is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDE_DIRS:
            return True
    return False


def _is_binary(path: Path) -> bool:
    try:
        with open(path, "rb") as fh:
            return b"\x00" in fh.read(8192)
    except OSError:
        return True


def _has_rtl(text: str) -> bool:
    return bool(RTL_RE.search(text))


def _get_line_context(lines: List[str], lineno: int, window: int = 1) -> str:
    start = max(0, lineno - window)
    end = min(len(lines), lineno + window + 1)
    ctx: List[str] = []
    for i in range(start, end):
        prefix = ">" if i == lineno else " "
        ctx.append(f"  {prefix} {i+1:>6d} | {lines[i].rstrip()}")
    return "\n".join(ctx)


def scan_source_file(path: Path) -> List[dict]:
    results: List[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return results

    lines = text.split("\n")
    ext = path.suffix.lower()

    # Inline comments
    if ext in {".py", ".pyi"}:
        comment_pattern = re.compile(r"#\s*(.*)")
    elif ext in {".ts", ".tsx", ".js", ".jsx", ".sol", ".css", ".scss"}:
        comment_pattern = re.compile(r"//\s*(.*)")
    else:
        comment_pattern = None

    if comment_pattern:
        for i, line in enumerate(lines):
            m = comment_pattern.search(line)
            if m:
                content = m.group(1)
                if _has_rtl(content):
                    results.append({
                        "line": i,
                        "column": m.start(),
                        "type": "comment",
                        "snippet": content.strip()[:120],
                        "context": _get_line_context(lines, i),
                    })

    # Multi-line comments / docstrings
    if ext in {".py", ".pyi"}:
        for m in re.finditer(r'"""\s*(.*?)\s*"""', text, re.DOTALL):
            content = m.group(1)
            if _has_rtl(content):
                lineno = text[: m.start()].count("\n")
                results.append({
                    "line": lineno,
                    "column": 0,
                    "type": "docstring",
                    "snippet": content.strip()[:120],
                    "context": _get_line_context(lines, lineno),
                })
    elif ext in {".ts", ".tsx", ".js", ".jsx", ".sol"}:
        for m in re.finditer(r"/\*\*\s*(.*?)\s*\*/", text, re.DOTALL):
            content = m.group(1)
            if _has_rtl(content):
                lineno = text[: m.start()].count("\n")
                results.append({
                    "line": lineno,
                    "column": 0,
                    "type": "jsdoc",
                    "snippet": content.strip()[:120],
                    "context": _get_line_context(lines, lineno),
                })

    # Hard-coded strings in JSX/TSX
    if ext in {".tsx", ".jsx"}:
        for m in re.finditer(r"""["']([^"']{4,})["']""", text):
            content = m.group(1)
            if _has_rtl(content):
                lineno = text[: m.start()].count("\n")
                results.append({
                    "line": lineno,
                    "column": m.start() - text.rfind("\n", 0, m.start()),
                    "type": "hardcoded_ui",
                    "snippet": content.strip()[:120],
                    "context": _get_line_context(lines, lineno),
                })

    return results


def scan_markdown_file(path: Path) -> List[dict]:
    results: List[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return results

    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("    "):
            continue
        if _has_rtl(stripped):
            results.append({
                "line": i,
                "column": 0,
                "type": "markdown",
                "snippet": stripped[:120],
                "context": _get_line_context(lines, i),
            })
    return results


def scan_config_file(path: Path) -> List[dict]:
    results: List[dict] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return results

    lines = text.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith(";"):
            continue
        if _has_rtl(stripped):
            results.append({
                "line": i,
                "column": 0,
                "type": "config_value",
                "snippet": stripped[:120],
                "context": _get_line_context(lines, i),
            })
    return results


def scan_repository() -> Dict[str, List[dict]]:
    report: Dict[str, List[dict]] = defaultdict(list)
    total_files = 0
    scanned_files = 0
    found_files = 0

    for root_str, dirs, files in os.walk(ROOT):
        root = Path(root_str)
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        if _is_excluded(root):
            continue

        for fname in files:
            if fname in EXCLUDE_FILES:
                continue
            fpath = root / fname
            ext = fpath.suffix.lower()
            stem = fname.lower()

            if ext not in SCAN_EXTENSIONS and stem not in {"dockerfile", "makefile"}:
                continue
            if _is_binary(fpath):
                continue

            total_files += 1
            rel = str(fpath.relative_to(ROOT)).replace("\\", "/")
            matches: List[dict] = []

            try:
                if ext in {".md", ".rst", ".txt"}:
                    matches = scan_markdown_file(fpath)
                elif ext in {".yaml", ".yml", ".toml", ".ini", ".cfg"} or stem in {"dockerfile"}:
                    matches = scan_config_file(fpath)
                elif ext in {".py", ".pyi", ".ts", ".tsx", ".js", ".jsx", ".sol", ".css", ".scss"}:
                    matches = scan_source_file(fpath)
                elif ext in {".json", ".html"}:
                    matches = scan_markdown_file(fpath)
            except Exception as exc:
                print(f"  [WARN] error scanning {rel}: {exc}", file=sys.stderr)
                continue

            if matches:
                found_files += 1
                report[rel] = matches
            scanned_files += 1

    print(
        f"\nScanned {scanned_files} files ({total_files} eligible), "
        f"found RTL content in {found_files} files.\n",
        file=sys.stderr,
    )
    return report


def write_json_report(report: Dict[str, List[dict]], path: Path) -> None:
    output = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "generator": "scan_i18n_issues.py",
        "total_files_with_issues": len(report),
        "total_issues": sum(len(v) for v in report.values()),
        "files": report,
    }
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  -> {path}  ({output['total_issues']} issues)", file=sys.stderr)


def write_markdown_report(report: Dict[str, List[dict]], path: Path) -> None:
    lines: List[str] = [
        "# i18n Scan Report - Phase P0",
        "",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**Files with issues:** {len(report)}",
        f"**Total issues:** {sum(len(v) for v in report.values())}",
        "",
        "---",
        "",
    ]
    for rel_path in sorted(report.keys()):
        matches = report[rel_path]
        lines.append(f"## `{rel_path}`  ({len(matches)} issue(s))")
        lines.append("")
        lines.append("| Line | Type | Snippet |")
        lines.append("|------|------|---------|")
        for m in matches:
            snippet = m["snippet"].replace("\n", "\\n")[:80]
            lines.append(f"| {m['line']+1} | {m['type']} | `{snippet}` |")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  -> {path}", file=sys.stderr)


def main():
    print("=" * 60, file=sys.stderr)
    print("  i18n Scanner - Phase P0 / Step 1", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    out_dir = ROOT / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)

    report = scan_repository()

    write_json_report(report, out_dir / "i18n_scan_report.json")
    write_markdown_report(report, out_dir / "i18n_scan_report.md")

    total = sum(len(v) for v in report.values())
    print(f"\nDone - {total} potential i18n issues found across {len(report)} files.", file=sys.stderr)


if __name__ == "__main__":
    main()

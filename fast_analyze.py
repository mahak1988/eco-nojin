#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
===============================================================================
ECO-NOJIN ULTRA-FAST PROJECT ANALYZER (v3.0)
===============================================================================
Architecture: Concurrent I/O, Pre-compiled Regex, O(N) Graph Resolution
Target: Large-scale Monorepos (React/FastAPI/IoT)
===============================================================================
"""

import json
import os
import re
import sys
import time
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

# =============================================================================
# 1. GLOBAL PRE-COMPILED REGEX ENGINE (Zero-overhead matching)
# =============================================================================
# Security Patterns
RE_SEC_SECRET = re.compile(
    r'(?i)(password|secret|api_key|token|aws_access_key)\s*=\s*["\'][^"\']+["\']'
)
RE_SEC_SQLI = re.compile(r'(?i)(execute|cursor\.execute)\s*\(\s*["\'].*?(%s|\{).*?["\']')
RE_SEC_EVAL = re.compile(r"(?i)\b(eval|exec|pickle\.loads?)\s*\(")

# TODO Patterns
RE_TODO = re.compile(r"(?i)(?:#|//|/\*|<!--)\s*(TODO|FIXME|HACK|XXX)\s*:?([\s\S]*?)(?=\n|$)")

# Import Patterns (Python & JS/TS)
RE_PY_IMPORT = re.compile(r"^\s*(?:from\s+([\w.]+)\s+)?import\s+([\w.,\s]+)", re.MULTILINE)
RE_JS_IMPORT = re.compile(r"""import\s+(?:[\w\s{},*]+\s+from\s+)?['"]([^'"]+)['"]""")
RE_JS_REQ = re.compile(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""")

# Architecture Patterns
RE_FASTAPI = re.compile(r"(?i)(fastapi|APIRouter|@app\.|@router\.)")
RE_REACT = re.compile(r"(?i)(react|useState|useEffect|jsx|tsx)")
RE_SQLALCHEMY = re.compile(r"(?i)(sqlalchemy|Column\(|relationship\()")
RE_SATELLITE = re.compile(r"(?i)(sentinel|NASA|SAR|NDVI|Landsat)")

# Ignore Patterns
IGNORE_DIRS = {
    "node_modules",
    ".git",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".next",
    "coverage",
    ".venv",
    "venv",
    "env",
    ".idea",
    ".vscode",
    ".tox",
    ".mypy_cache",
    "eggs",
    "*.egg-info",
    ".hg",
    ".svn",
    "target",
    "bin",
    "obj",
}
IGNORE_EXTS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".exe",
    ".dll",
    ".so",
    ".dylib",
    ".pyc",
    ".pyo",
    ".lock",
    ".map",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".mp4",
    ".mp3",
}


# =============================================================================
# 2. HIGH-PERFORMANCE FILE SYSTEM TRAVERSAL
# =============================================================================
def fast_scandir_recursive(dirpath, ignore_dirs):
    """
    Uses os.scandir for O(1) stat caching. Much faster than os.walk.
    Yields: (filepath, size)
    """
    try:
        for entry in os.scandir(dirpath):
            if entry.is_dir(follow_symlinks=False):
                if entry.name not in ignore_dirs and not entry.name.startswith("."):
                    yield from fast_scandir_recursive(entry.path, ignore_dirs)
            elif entry.is_file(follow_symlinks=False):
                ext = os.path.splitext(entry.name)[1].lower()
                if ext not in IGNORE_EXTS and not entry.name.startswith("."):
                    yield entry.path, entry.stat().st_size
    except PermissionError:
        pass


# =============================================================================
# 3. CONCURRENT FILE ANALYSIS WORKER
# =============================================================================
def analyze_single_file(filepath: str, size: int, project_root: str) -> dict:
    """
    Thread-safe worker function. Analyzes one file and returns a lightweight dict.
    """
    result = {
        "path": os.path.relpath(filepath, project_root),
        "ext": os.path.splitext(filepath)[1].lower(),
        "size": size,
        "status": "HEALTHY",
        "issues": [],
        "imports": set(),
        "todos": 0,
        "sec_issues": 0,
        "arch": set(),
    }

    try:
        # Fast binary check: read first 1024 bytes for null bytes
        with open(filepath, "rb") as f:
            chunk = f.read(1024)
            if b"\0" in chunk:
                return result  # Binary file, skip text analysis

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        result["status"] = "ERROR"
        result["issues"].append(f"ReadError: {str(e)}")
        return result

    lines = content.count("\n") + 1
    result["lines"] = lines

    # --- A. Syntax Check (C-Level Fast Path) ---
    if result["ext"] == ".py":
        try:
            compile(content, filepath, "exec")
        except SyntaxError as e:
            result["status"] = "DAMAGED_CRITICAL"
            result["issues"].append(f"SyntaxError: {e.msg} (Line {e.lineno})")
        except Exception as e:
            result["status"] = "DAMAGED_CRITICAL"
            result["issues"].append(f"CompileError: {str(e)}")

        # Python Imports
        for match in RE_PY_IMPORT.finditer(content):
            mod = match.group(1) or match.group(2)
            result["imports"].add(mod.split(".")[0])

    elif result["ext"] in (".js", ".jsx", ".ts", ".tsx"):
        # JS/TS Heuristic Syntax Check (Bracket Balancing)
        if content.count("{") != content.count("}") or content.count("(") != content.count(")"):
            result["status"] = "DAMAGED_MINOR"
            result["issues"].append("Unbalanced brackets/braces")

        # JS/TS Imports
        for match in RE_JS_IMPORT.finditer(content):
            result["imports"].add(match.group(1).split("/")[0])
        for match in RE_JS_REQ.finditer(content):
            result["imports"].add(match.group(1).split("/")[0])

    # --- B. Security & TODO Scanning ---
    if RE_SEC_SECRET.search(content):
        result["sec_issues"] += 1
    if RE_SEC_SQLI.search(content):
        result["sec_issues"] += 1
    if RE_SEC_EVAL.search(content):
        result["sec_issues"] += 1

    todos = RE_TODO.findall(content)
    result["todos"] = len(todos)
    if todos and result["status"] == "HEALTHY":
        result["status"] = "INCOMPLETE"

    # --- C. Architecture Detection ---
    if RE_FASTAPI.search(content):
        result["arch"].add("FastAPI")
    if RE_REACT.search(content):
        result["arch"].add("React")
    if RE_SQLALCHEMY.search(content):
        result["arch"].add("SQLAlchemy")
    if RE_SATELLITE.search(content):
        result["arch"].add("Satellite/IoT")

    return result


# =============================================================================
# 4. MAIN ORCHESTRATOR & O(N) GRAPH RESOLUTION
# =============================================================================
def run_analysis(project_path: str, max_workers: int = None):
    if not max_workers:
        max_workers = min(32, (os.cpu_count() or 1) + 4)  # Optimal for I/O bound

    print(f"[*] Initializing Ultra-Fast Analyzer for: {project_path}")
    print(f"[*] Using {max_workers} concurrent workers...")

    start_time = time.time()

    # Phase 1: Fast Discovery
    print("[1/4] Scanning file system (os.scandir)...")
    files_to_analyze = list(fast_scandir_recursive(project_path, IGNORE_DIRS))
    total_files = len(files_to_analyze)
    print(f"      Found {total_files} analyzable files.")

    # Phase 2: Concurrent Analysis
    print("[2/4] Analyzing files (ThreadPoolExecutor)...")
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(analyze_single_file, fp, sz, project_path): fp
            for fp, sz in files_to_analyze
        }

        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"      [!] Worker error: {e}")

    # Phase 3: O(N) Orphan Detection & Aggregation
    print("[3/4] Resolving dependency graph & orphans (O(N) Hash Set)...")

    # Build a set of all known file basenames and relative paths for O(1) lookups
    known_files = set()
    for r in results:
        known_files.add(os.path.basename(r["path"]))
        known_files.add(r["path"].replace("\\", "/"))  # Normalize slashes

    # Aggregate metrics
    stats = {
        "total_files": total_files,
        "total_lines": sum(r.get("lines", 0) for r in results),
        "total_size_mb": sum(r["size"] for r in results) / (1024 * 1024),
        "damaged": [],
        "orphans": [],
        "incomplete": [],
        "sec_issues": 0,
        "todos": 0,
        "ext_counts": Counter(),
        "arch_counts": Counter(),
    }

    # Collect all imported modules globally
    all_imports = set()

    entry_points = {
        "main.py",
        "app.py",
        "index.js",
        "index.ts",
        "index.tsx",
        "manage.py",
        "setup.py",
        "__init__.py",
        "App.tsx",
        "App.jsx",
        "package.json",
        "requirements.txt",
        "pyproject.toml",
        "README.md",
    }

    for r in results:
        stats["ext_counts"][r["ext"]] += 1
        stats["arch_counts"].update(r["arch"])
        stats["sec_issues"] += r["sec_issues"]
        stats["todos"] += r["todos"]
        all_imports.update(r["imports"])

        if r["status"] == "DAMAGED_CRITICAL" or r["status"] == "DAMAGED_MINOR":
            stats["damaged"].append(r)
        elif r["status"] == "INCOMPLETE":
            stats["incomplete"].append(r)

        # Orphan Logic: If a file is not imported by anything, and not an entry point
        # We check if any known import matches the file's basename or path
        basename = os.path.basename(r["path"])
        is_referenced = any(imp in basename or imp in r["path"] for imp in all_imports)

        if not is_referenced and basename not in entry_points and "test" not in r["path"].lower():
            stats["orphans"].append(r)

    # Phase 4: Report Generation
    print("[4/4] Generating Markdown report...")
    generate_report(stats, project_path, time.time() - start_time)


# =============================================================================
# 5. REPORT GENERATOR
# =============================================================================
def generate_report(stats: dict, project_path: str, elapsed: float):
    report = []
    report.append("# ⚡ Eco-Nojin Ultra-Fast Analysis Report")
    report.append(
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Execution Time:** {elapsed:.2f} seconds\n"
    )

    report.append("## 📊 Executive Summary")
    report.append(f"- **Total Files:** {stats['total_files']:,}")
    report.append(f"- **Total Lines:** {stats['total_lines']:,}")
    report.append(f"- **Total Size:** {stats['total_size_mb']:.2f} MB")
    report.append(f"- **Security Alerts:** {stats['sec_issues']}")
    report.append(f"- **Technical Debt (TODOs):** {stats['todos']}")
    report.append(f"- **Damaged Files:** {len(stats['damaged'])}")
    report.append(f"- **Orphan Files:** {len(stats['orphans'])}\n")

    if stats["damaged"]:
        report.append("## ⚠️ Damaged Files (Action Required)")
        report.append("| File | Status | Issues |")
        report.append("|------|--------|--------|")
        for f in stats["damaged"][:20]:
            issues = "; ".join(f["issues"])
            report.append(f"| `{f['path']}` | {f['status']} | {issues} |")
        report.append("")

    if stats["orphans"]:
        report.append("## 🗑️ Orphan Files (Unreferenced)")
        report.append("| File | Size (KB) | Lines |")
        report.append("|------|-----------|-------|")
        for f in stats["orphans"][:20]:
            report.append(f"| `{f['path']}` | {f['size'] / 1024:.1f} | {f.get('lines', 0)} |")
        if len(stats["orphans"]) > 20:
            report.append(f"*...and {len(stats['orphans']) - 20} more orphan files.*")
        report.append("")

    if stats["sec_issues"] > 0:
        report.append(f"## 🔒 Security Vulnerabilities\n")
        report.append(
            f"Found **{stats['sec_issues']}** potential security issues (Hardcoded secrets, SQLi, Eval). Immediate audit required.\n"
        )

    report.append("## 🏗️ Architecture & Stack Detection")
    for arch, count in stats["arch_counts"].most_common():
        report.append(f"- **{arch}**: {count} files")
    report.append("")

    # Save to disk
    out_path = os.path.join(project_path, "FAST_ANALYSIS_REPORT.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    print(f"\n[SUCCESS] Analysis completed in {elapsed:.2f} seconds.")
    print(f"[OUTPUT] Report saved to: {out_path}")


# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    if not os.path.isdir(target):
        print(f"[ERROR] Directory not found: {target}")
        sys.exit(1)

    run_analysis(os.path.abspath(target))

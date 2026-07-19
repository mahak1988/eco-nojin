#!/usr/bin/env python3
"""
Check for God Files - Code Quality Gate
======================================
Identifies overly large files that violate single responsibility principle.
Files with > 500 lines are flagged as potential 'God Files'.
"""

import os
import sys
from pathlib import Path
from typing import NamedTuple

MAX_FILE_LINES = 500
MAX_FUNCTION_LINES = 100

# Exclude directories and generated scripts
EXCLUDE_DIRS = {
    ".venv", "node_modules", ".git", "__pycache__", 
    "dist", "build", "htmlcov", "__repo_sync_tmp__"
}
EXCLUDE_FILES = {
    "generate_languages.py", "generate_batch2.py", 
    "generate_advanced.py", "fix_build_errors.py"
}


class FileReport(NamedTuple):
    path: str
    lines: int
    status: str


def count_lines(file_path: Path) -> int:
    """Count non-empty, non-comment lines in a file."""
    count = 0
    try:
        with open(file_path, encoding="utf-8") as f:
            in_multiline_string = False
            for line in f:
                stripped = line.strip()
                
                # Skip empty lines
                if not stripped:
                    continue
                
                # Skip single-line comments
                if stripped.startswith("#"):
                    continue
                
                # Handle docstrings
                if '"""' in stripped or "'''" in stripped:
                    if stripped.count('"""') == 2 or stripped.count("'''") == 2:
                        continue
                    in_multiline_string = not in_multiline_string
                    continue
                
                if not in_multiline_string:
                    count += 1
    except Exception:
        pass
    return count


def check_project_structure(project_root: Path) -> list[FileReport]:
    """Check all Python files in the project for god files."""
    reports = []
    
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.endswith(".py") and file not in EXCLUDE_FILES:
                file_path = Path(root) / file
                lines = count_lines(file_path)
                
                status = "OK"
                if lines > MAX_FILE_LINES:
                    status = f"GOD FILE ({lines} lines)"
                
                reports.append(FileReport(str(file_path), lines, status))
    
    return reports


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    
    print(f"Checking Python files in {project_root}")
    print(f"Max allowed lines: {MAX_FILE_LINES}")
    print("-" * 60)
    
    reports = check_project_structure(project_root)
    god_files = [r for r in reports if "GOD FILE" in r.status]
    
    for report in sorted(reports, key=lambda r: r.lines, reverse=True):
        if report.lines > MAX_FILE_LINES * 0.8:
            rel_path = Path(report.path).relative_to(project_root)
            print(f"{report.status}: {rel_path} ({report.lines} lines)")
    
    print("-" * 60)
    
    if god_files:
        print(f"\nFound {len(god_files)} God Files!")
        for god_file in god_files:
            rel_path = Path(god_file.path).relative_to(project_root)
            print(f"  - {rel_path}: {god_file.lines} lines")
        sys.exit(1)
    else:
        print(f"\nAll files are under {MAX_FILE_LINES} lines. Good structure!")
        sys.exit(0)


if __name__ == "__main__":
    main()
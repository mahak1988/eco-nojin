#!/usr/bin/env python3
"""
Simple scanner for potential hardcoded secrets in Python files.
"""

import re
from pathlib import Path


def scan_file_for_secrets(file_path: Path):
    """Scans a single file for potential hardcoded secrets."""
    patterns = [
        # Matches strings like password="...", api_key = '...', etc.
        # Captures the value part to check its strength/validity.
        r"(?i)(?:password|passwd|pwd|secret|token|api[_\-]?key|apikey|access[_\-]?key|auth[_\-]?token|client[_\-]?secret)\s*[:=]\s*[\"']([^\"'\s]{8,128})[\"']",
        # Matches long hex/base64-like strings which might be keys
        r"([A-Za-z0-9+/]{20,}={0,2})", 
    ]
    
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    issues = []
    for i, pattern in enumerate(patterns):
        matches = re.finditer(pattern, content)
        for match in matches:
            # For the first pattern, we check the captured group
            if i == 0 and match.group(1):
                value = match.group(1)
                # Flag common weak passwords regardless of pattern
                if value.lower() in ["password", "123456", "admin", "changeme", "secret"]:
                     issues.append(f"  Weak hardcoded value '{value}' at {match.start()}-{match.end()}")
            # For the second pattern (long string), just report the match
            elif i == 1:
                value = match.group(0)
                # Avoid reporting long strings that look like legitimate code (e.g., SQL queries)
                if not ('SELECT' in value or 'FROM' in value or 'WHERE' in value):
                    issues.append(f"  Potential hardcoded key/token at {match.start()}-{match.end()}: '{value[:30]}...'")

    return issues


def scan_directory(directory: Path):
    """Scans all Python files in a directory."""
    py_files = directory.rglob("*.py")
    all_issues = {}
    for file_path in py_files:
        issues = scan_file_for_secrets(file_path)
        if issues:
            all_issues[file_path] = issues
    
    return all_issues


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    print(f"Scanning {project_root} for potential hardcoded secrets...")
    issues = scan_directory(project_root)
    
    if issues:
        print("\nPotential issues found:")
        for file_path, file_issues in issues.items():
            print(f"\n{file_path}:")
            for issue in file_issues:
                print(issue)
    else:
        print("\nNo obvious hardcoded secrets found.")
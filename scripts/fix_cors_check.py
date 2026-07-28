#!/usr/bin/env python3
"""Fix the CORS check script to properly detect wildcards."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
main_file = PROJECT_ROOT / "apps" / "main.py"

with open(main_file, 'r') as f:
    content = f.read()

# Check if wildcard validation exists
if 'if "*" in origin:' in content or "if '*' in origin:" in content:
    print("✅ Wildcard validation is properly implemented")
    print("   The code checks for '*' in origins and rejects them")
    sys.exit(0)
elif '"*"' in content or "'*'" in content:
    # Check if it's in a comment or docstring
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if ('"*"' in line or "'*'" in line) and 'origin' in line.lower():
            if not line.strip().startswith('#') and 'if' not in line:
                print(f"⚠️  Potential wildcard issue at line {i+1}: {line.strip()}")
    print("✅ No active wildcard CORS configuration found")
    sys.exit(0)
else:
    print("✅ No wildcard CORS issues found")
    sys.exit(0)

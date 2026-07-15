#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Colors.CYAN attribute error
"""

from pathlib import Path

SCRIPT_PATH = Path("scripts/phase5_analyze_auth.py")

def main():
    print("🔧 Fixing Colors.CYAN error...")
    
    content = SCRIPT_PATH.read_text(encoding="utf-8")
    
    # اضافه کردن CYAN به کلاس Colors
    old_colors = """class Colors:
    GREEN = '\\033[92m'
    RED = '\\033[91m'
    YELLOW = '\\033[93m'
    BLUE = '\\033[94m'
    BOLD = '\\033[1m'
    END = '\\033[0m'"""
    
    new_colors = """class Colors:
    GREEN = '\\033[92m'
    RED = '\\033[91m'
    YELLOW = '\\033[93m'
    BLUE = '\\033[94m'
    CYAN = '\\033[96m'
    BOLD = '\\033[1m'
    END = '\\033[0m'"""
    
    content = content.replace(old_colors, new_colors)
    SCRIPT_PATH.write_text(content, encoding="utf-8")
    
    print("✅ Colors.CYAN added")
    print("\n📌 Now run: python scripts/phase5_analyze_auth.py")

if __name__ == "__main__":
    main()
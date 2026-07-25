#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_analyzer.py — بازگردانی project_analyzer.py و patch صحیح
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
۱. بازگردانی از آخرین commit سالم
۲. patch صحیح SKIP_FILE_NAMES (با validate)
۳. تست import
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ANALYZER = ROOT / "project_analyzer.py"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def main() -> int:
    apply = "--apply" in sys.argv
    print("═" * 60)
    print("  🔧 بازگردانی و patch صحیح project_analyzer.py")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    # ── ۱. بازگردانی از آخرین commit سالم ──
    print("\n  → بازگردانی از آخرین commit سالم …")
    r = git("checkout", "HEAD", "--", "project_analyzer.py", check=False)
    if r.returncode == 0:
        print("  ✅ بازگردانی شد")
    else:
        print(f"  ⚠️  {r.stderr.strip()}")

    # ── ۲. validate syntax اولیه ──
    text = ANALYZER.read_text(encoding="utf-8")
    try:
        ast.parse(text)
        print("  ✅ syntax اولیه معتبر است")
    except SyntaxError as e:
        print(f"  ❌ syntax نامعتبر پس از بازگردانی: {e}")
        print("  → ممکن است commit قبلی هم مشکل داشته باشد")
        return 1

    # ── ۳. patch صحیح SKIP_FILE_NAMES ──
    new_items = ['".env"', '".env.bak"', '".env.local"',
                 '".env.production"', '".gh_token"']

    # بررسی اینکه آیا قبلاً وجود دارند
    already = all(item in text for item in new_items)
    if already:
        print("  ✅ .env و .gh_token قبلاً در SKIP_FILE_NAMES هستند")
    else:
        # پیدا کردن SKIP_FILE_NAMES = { ... }
        m = re.search(r'(SKIP_FILE_NAMES\s*=\s*\{)([^}]*?)(\})', text, re.DOTALL)
        if m:
            existing = m.group(2).rstrip()
            # ساخت رشته افزودنی
            additions = ", ".join(item for item in new_items if item not in existing)
            if additions:
                # اطمینان از کاما قبل از افزودن
                if existing.strip() and not existing.strip().endswith(","):
                    existing += ","
                new_block = m.group(1) + existing + " " + additions + m.group(3)
                text = text[:m.start()] + new_block + text[m.end():]
                print(f"  🔧 افزوده شد: {additions}")
        else:
            print("  ⚠️  SKIP_FILE_NAMES یافت نشد — patch اعمال نمی‌شود")

    # ── ۴. validate پس از patch ──
    try:
        ast.parse(text)
        print("  ✅ syntax پس از patch معتبر است")
    except SyntaxError as e:
        print(f"  ❌ patch نامعتبر: {e}")
        print("  → بازگردانی به نسخه سالم (بدون patch)")
        git("checkout", "HEAD", "--", "project_analyzer.py", check=False)
        return 1

    # ── ۵. اعمال ──
    if apply:
        ANALYZER.write_text(text, encoding="utf-8")
        print("  ✅ patch اعمال شد")

        # تست import
        r = subprocess.run([sys.executable, "-c",
                            "from project_analyzer import ProjectAnalyzer, setup_logging; print('OK')"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0 and "OK" in r.stdout:
            print("  ✅ import موفق — hook کار می‌کند")
        else:
            print(f"  ❌ import ناموفق: {r.stderr[:200]}")
            print("  → بازگردانی به نسخه سالم")
            git("checkout", "HEAD", "--", "project_analyzer.py", check=False)
            return 1
    else:
        print("  → برای اعمال: python fix_analyzer.py --apply")

    return 0


if __name__ == "__main__":
    sys.exit(main())
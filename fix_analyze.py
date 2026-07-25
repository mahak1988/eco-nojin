#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''fix_analyze.py — رفع باگ analyze_apps.py + اسکن مجدد'''
from __future__ import annotations
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET = ROOT / 'analyze_apps.py'

def main() -> int:
    apply = '--apply' in sys.argv
    text = TARGET.read_text(encoding='utf-8')

    # ── رفع باگ ۱: split('/') → Path.parts ──
    old = "app = str(pkg.relative_to(ROOT)).split('/')[1]"
    new = ("rel_parts = pkg.relative_to(ROOT).parts\n"
           "            app = rel_parts[1] if len(rel_parts) > 1 else 'root'")
    if old in text:
        text = text.replace(old, new)
        print('  ✅ باگ split("/") اصلاح شد')
    else:
        print('  ⚪ باگ قبلاً اصلاح شده')

    # ── رفع باگ ۲: split('/') در جای دیگر ──
    old2 = "app = str(pkg.relative_to(ROOT)).split('/')[1]"
    if old2 in text:
        text = text.replace(old2, new)

    # ── رفع باگ ۳: Windows path separator ──
    text = text.replace(
        "if any(skip in str(f) for skip in",
        "if any(skip in str(f).replace('\\\\', '/') for skip in"
    )

    if apply:
        TARGET.write_text(text, encoding='utf-8')
        print('  ✅ فایل ذخیره شد')

        # اسکن مجدد
        print('\n  📊 اسکن مجدد …')
        r = subprocess.run(
            [sys.executable, str(TARGET)],
            cwd=ROOT, timeout=120,
        )
        return r.returncode
    else:
        print('  → برای اعمال: python fix_analyze.py --apply')
    return 0

if __name__ == '__main__':
    sys.exit(main())
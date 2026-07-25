#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mask_readmes.py — mask کردن رشته‌های حساس در READMEها (آخرین قدم)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = [
    ("apps/cms/README.md", [
        (r'(postgresql://[^:/\s"\']+:)[^@\s"\']+(@)', r'\1*****\2'),
        (r'(DATABASE_URL=postgresql://[^:/\s"\']+:)[^@\s"\']+(@)', r'\1*****\2'),
        (r'(DATABASE_URL=)["\']?postgresql://[^\s"\']+["\']?',
         r'\1postgresql://user:*****@host:5432/db'),
    ]),
    ("apps/users/README.md", [
        (r'(Bearer\s+)[A-Za-z0-9\-_\.]{20,}',
         r'\1eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'),
        (r'("password":\s*")[^"]{4,}(")', r'\1*****\2'),
        (r'("password":\s*")[^"]{4,}(")', r'\1*****\2'),
    ]),
]


def main() -> int:
    apply = "--apply" in sys.argv
    print("═" * 60)
    print("  🔒 mask کردن رشته‌های حساس در READMEها")
    print("═" * 60)
    if not apply:
        print("  ℹ️  حالت گزارش — برای اعمال: --apply")

    total_all = 0
    for rel, patterns in FILES:
        f = ROOT / rel
        if not f.exists():
            print(f"\n  ⚪ {rel} — یافت نشد")
            continue
        text = f.read_text(encoding="utf-8")
        total = 0
        for pat, repl in patterns:
            text, n = re.subn(pat, repl, text)
            total += n
        if total:
            print(f"\n  🔧 {rel} — {total} مورد یافت شد")
            if apply:
                f.write_text(text, encoding="utf-8")
                print(f"  ✅ mask شد")
                total_all += total
        else:
            print(f"\n  ✅ {rel} — قبلاً mask شده")

    if apply and total_all:
        print(f"\n  🎉 مجموعاً {total_all} مورد mask شد")
    elif not apply:
        print(f"\n  → برای اعمال: python mask_readmes.py --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
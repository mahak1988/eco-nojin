#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
staged_scan.py — اسکن امنیتی فقط فایل‌های staged (برای pre-commit hook)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
به‌جای اسکن کل پروژه (۲۸۲ ثانیه)، فقط فایل‌هایی که در حال commit هستند
را اسکن می‌کند (<۱ ثانیه). از موتور project_analyzer.py استفاده می‌کند.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

try:
    from project_analyzer import ProjectAnalyzer, setup_logging
except ImportError:
    print("❌ project_analyzer.py یافت نشد (باید در همین دایرکتوری باشد)")
    sys.exit(2)

ROOT = Path(__file__).resolve().parent
FAIL_SEVERITIES = {"critical", "high"}


def get_staged_files() -> list[str]:
    """فهرست فایل‌های staged (افزوده/تغییرکرده/کپی/تغییرنام)."""
    r = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--cached",
         "--name-only", "--diff-filter=ACMR", "-z"],
        capture_output=True, text=True, check=False, timeout=30,
    )
    if r.returncode != 0:
        return []
    # خروجی -z با \0 جدا می‌شود (امن برای نام‌های دارای space)
    return [f for f in r.stdout.split("\0") if f.strip()]


def main() -> int:
    staged = get_staged_files()
    if not staged:
        print("✅ هیچ فایل staged برای اسکن وجود ندارد")
        return 0

    print(f"🔍 اسکن {len(staged)} فایل staged …")

    # Namespace مصنوعی برای موتور اسکن (بدون نیاز به تغییر project_analyzer)
    args = argparse.Namespace(
        max_file_mb=2.0,
        max_depth=12,
        exclude=[],
        no_network=True,
        no_git=True,
        fail_on="critical,high",
        json_out=".git/staged-scan.json",
        html_out=".git/staged-scan.html",
        verbose=False,
    )
    logger = setup_logging(False)
    analyzer = ProjectAnalyzer(ROOT, args, logger)
    analyzer._validate_root()

    for rel in staged:
        path = ROOT / rel
        if path.is_file():
            analyzer._process_file(path, rel)

    if analyzer.findings:
        print(f"\n  ⚠️  {len(analyzer.findings)} یافته امنیتی:")
        for f in sorted(analyzer.findings,
                        key=lambda x: ("critical", "high", "medium", "low", "info").index(x.severity)):
            loc = f"{f.file}:{f.line}" if f.line else f.file
            print(f"   • [{f.severity}] {f.title} — {loc}")

    blocking = {f.severity for f in analyzer.findings} & FAIL_SEVERITIES
    if blocking:
        print(f"\n  ⛔ commit مسدود شد (یافته در سطح: {', '.join(sorted(blocking))})")
        print("     برای عبور موقت (توصیه نمی‌شود): git commit --no-verify")
        return 1

    print(f"\n  ✅ {len(staged)} فایل staged پاک بود")
    return 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fix_git.py — رفع مشکل nested repository و پاکسازی دایرکتوری‌های موقت
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REMOVE_DIRS = ["__repo_sync_tmp__"]
REMOVE_GLOBS = [".sync_backup_*"]


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def main() -> int:
    print("═" * 60)
    print("  🔧 رفع مشکل nested repository")
    print("═" * 60)

    # ۱. حذف فیزیکی دایرکتوری‌های موقت
    removed = []
    for name in REMOVE_DIRS:
        p = ROOT / name
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)
            removed.append(name)
            print(f"  🗑️  حذف شد: {name}")
    for pattern in REMOVE_GLOBS:
        for p in ROOT.glob(pattern):
            if p.exists():
                shutil.rmtree(p, ignore_errors=True)
                removed.append(p.name)
                print(f"  🗑️  حذف شد: {p.name}")
    if not removed:
        print("  ✅ هیچ دایرکتوری موقتی یافت نشد")

    # ۲. حذف از git index (اگر به‌عنوان gitlink tracked باشد)
    for name in REMOVE_DIRS:
        r = git("rm", "--cached", "-r", "--ignore-unmatch", name, check=False)
        if r.returncode == 0 and r.stdout.strip():
            print(f"  ✅ از git index حذف شد: {name}")
    for pattern in REMOVE_GLOBS:
        for p in ROOT.glob(pattern):
            git("rm", "--cached", "-r", "--ignore-unmatch", p.name, check=False)

    # ۳. اطمینان از وجود الگوها در .gitignore
    gitignore = ROOT / ".gitignore"
    content = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    needed = ["__repo_sync_tmp__/", ".sync_backup_*/"]
    missing = [n for n in needed if n not in content]
    if missing:
        with gitignore.open("a", encoding="utf-8") as f:
            f.write("\n# Nested repos / temp\n")
            for n in missing:
                f.write(n + "\n")
        print(f"  ✅ .gitignore به‌روزرسانی شد: {', '.join(missing)}")
    else:
        print("  ✅ .gitignore کامل است")

    # ۴. بررسی وضعیت git
    r = git("status", "--short", check=False)
    if r.returncode == 0:
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        print(f"\n  📋 {len(lines)} فایل تغییرکرده آماده commit:")
        for ln in lines[:10]:
            print(f"     {ln}")
        if len(lines) > 10:
            print(f"     … و {len(lines) - 10} مورد دیگر")

    print("\n" + "═" * 60)
    print("  ✅ اکنون دستورات زیر را اجرا کنید:")
    print("     git add -A")
    print('     git commit -m "security: remove hardcoded secrets from configs and docs"')
    print("     git push")
    print("═" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
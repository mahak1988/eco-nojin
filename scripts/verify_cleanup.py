#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  🔍 Verify Cleanup - بررسی نتیجه پاکسازی
  نسخه: 1.0.0
============================================================

اسکریپت ساده برای بررسی اینکه آیا پاکسازی موفق بوده یا نه.

نحوه اجرا:
  python verify_cleanup.py
  python verify_cleanup.py "D:\\econojin.com"
"""

import os
import sys
import platform
from pathlib import Path
from datetime import datetime


class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"

    @staticmethod
    def enable_windows():
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass


# آیتم‌هایی که نباید بعد از پاکسازی وجود داشته باشن
JUNK_FILES = {
    'files.txt', 'report.json', 'orphans_list.txt', 'dependency_graph.dot',
    'MERGE_PLAN.json', 'project_analyzer', 'react-18.2.0.tgz',
    'restore_from_backup.ps1', 'fix_venv.ps1',
}

BACKUP_DIRS = {
    '.cleanup_backup', '.migration_backup', '.structure_backup',
    'apps_backup_20260711_025121', '_COLD_STORAGE',
}

CACHE_DIRS = {
    '.pnpm-store', '.venv-1', '.venv-2', 'venv-1', 'venv-2',
}

SCRIPTS_TO_MOVE = {
    'eco.py', 'migration_script.py', 'discover.py', 'run_econojin.py',
    'analyze_project.py', 'apps_analyzer_v1.1.py', 'apps_analyzer_v1.2.py',
    'dependency_analyzer.py', 'deep_secret_scanner.py', 'project_analyzer.py',
    'install_venv.ps1', 'install_packages.sh',
}


def h(size: int) -> str:
    for u in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {u}"
        size /= 1024
    return f"{size:.2f} PB"


def dir_size(d: Path) -> int:
    total = 0
    try:
        for root, dirs, files in os.walk(d):
            for f in files:
                try:
                    total += (Path(root) / f).stat().st_size
                except:
                    pass
    except:
        pass
    return total


def main():
    C.enable_windows()

    project = Path(sys.argv[1] if len(sys.argv) > 1 else r'D:\econojin.com').resolve()

    print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}║  🔍 Verify Cleanup - بررسی نتیجه پاکسازی{' '*16}║{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(project):<51}║{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

    if not project.exists():
        print(f"{C.RED}❌ مسیر وجود ندارد!{C.RESET}")
        sys.exit(1)

    score = 0
    total_checks = 0
    issues = []

    # ۱. بررسی فایل‌های junk
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۱. فایل‌های غیرضروری ━━━{C.RESET}")
    for name in JUNK_FILES:
        total_checks += 1
        if (project / name).exists():
            issues.append(f"  {C.RED}✗ هنوز موجوده:{C.RESET} {name}")
        else:
            score += 1

    if all(not (project / n).exists() for n in JUNK_FILES):
        print(f"  {C.GREEN}✓ همه فایل‌های غیرضروری حذف شده‌اند{C.RESET}")
    else:
        for issue in issues:
            print(issue)
        issues = [i for i in issues if 'فایل‌های غیرضروری' not in i]

    # ۲. بررسی پوشه‌های backup
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۲. پوشه‌های پشتیبان ━━━{C.RESET}")
    backup_issues = []
    for name in BACKUP_DIRS:
        total_checks += 1
        if (project / name).exists():
            size = dir_size(project / name)
            backup_issues.append(f"  {C.RED}✗ {name}/ ({h(size)}){C.RESET}")
        else:
            score += 1

    if backup_issues:
        for issue in backup_issues:
            print(issue)
    else:
        print(f"  {C.GREEN}✓ همه پوشه‌های پشتیبان حذف شده‌اند{C.RESET}")

    # ۳. بررسی cache
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۳. پوشه‌های cache ━━━{C.RESET}")
    cache_issues = []
    for name in CACHE_DIRS:
        total_checks += 1
        if (project / name).exists():
            size = dir_size(project / name)
            cache_issues.append(f"  {C.RED}✗ {name}/ ({h(size)}){C.RESET}")
        else:
            score += 1

    if cache_issues:
        for issue in cache_issues:
            print(issue)
    else:
        print(f"  {C.GREEN}✓ همه cache ها حذف شده‌اند{C.RESET}")

    # ۴. بررسی انتقال اسکریپت‌ها
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۴. اسکریپت‌های ریشه ━━━{C.RESET}")
    script_issues = []
    scripts_dir = project / 'scripts'
    moved_count = 0
    for name in SCRIPTS_TO_MOVE:
        total_checks += 1
        root_file = project / name
        scripts_file = scripts_dir / name
        if root_file.exists():
            script_issues.append(f"  {C.RED}✗ هنوز در ریشه:{C.RESET} {name}")
        elif scripts_file.exists():
            score += 1
            moved_count += 1
        else:
            score += 1  # اگه اصلا وجود نداره هم خوبه

    if script_issues:
        for issue in script_issues:
            print(issue)
    else:
        print(f"  {C.GREEN}✓ اسکریپت‌ها منتقل/حذف شده‌اند{C.RESET}")
        if moved_count:
            print(f"  {C.GRAY}{moved_count} اسکریپت در scripts/ هست{C.RESET}")

    # ۵. بررسی .venv (محیط فعال)
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۵. محیط فعال .venv ━━━{C.RESET}")
    total_checks += 1
    venv = project / '.venv'
    if venv.exists():
        size = dir_size(venv)
        print(f"  {C.GREEN}✓ محیط فعال حفظ شد:{C.RESET} .venv/ ({h(size)})")
        score += 1
    else:
        print(f"  {C.YELLOW}⚠ .venv وجود ندارد - ممکن است نیاز به ساخت مجدد داشته باشی{C.RESET}")

    # ۶. بررسی .gitignore
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۶. .gitignore ━━━{C.RESET}")
    gi = project / '.gitignore'
    total_checks += 1
    if gi.exists():
        content = gi.read_text(encoding='utf-8', errors='ignore')
        if '*.db' in content:
            print(f"  {C.GREEN}✓ .gitignore شامل *.db است{C.RESET}")
            score += 1
        else:
            print(f"  {C.YELLOW}⚠ *.db در .gitignore نیست{C.RESET}")
    else:
        print(f"  {C.RED}✗ .gitignore وجود ندارد{C.RESET}")

    # ۷. بررسی ساختار اصلی
    print(f"\n{C.CYAN}{C.BOLD}━━━ ۷. ساختار اصلی پروژه ━━━{C.RESET}")
    essential = ['apps', 'packages', 'package.json', 'pyproject.toml']
    for item in essential:
        total_checks += 1
        if (project / item).exists():
            print(f"  {C.GREEN}✓{C.RESET} {item}/")
            score += 1
        else:
            print(f"  {C.RED}✗{C.RESET} {item}/ وجود ندارد!")

    # خلاصه
    print(f"\n{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}  📊 نتیجه نهایی{C.RESET}")
    print(f"{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")
    pct = (score / total_checks) * 100 if total_checks else 0

    if pct == 100:
        grade = 'A+'
        color = C.GREEN
        msg = "پاکسازی کامل و عالی!"
    elif pct >= 80:
        grade = 'A'
        color = C.GREEN
        msg = "پاکسازی خوب"
    elif pct >= 60:
        grade = 'B'
        color = C.YELLOW
        msg = "نیمه کامل - ادامه بده"
    else:
        grade = 'C'
        color = C.RED
        msg = "نیاز به کار بیشتر"

    print(f"  {C.CYAN}امتیاز:{C.RESET} {color}{C.BOLD}{score}/{total_checks} ({pct:.0f}%){C.RESET}")
    print(f"  {C.CYAN}نمره:{C.RESET} {color}{C.BOLD}{grade}{C.RESET}")
    print(f"  {C.CYAN}وضعیت:{C.RESET} {color}{msg}{C.RESET}")

    print(f"\n  {C.GRAY}برای ادامه به فاز ۱، امتیاز باید A یا A+ باشد.{C.RESET}")
    print()


if __name__ == '__main__':
    main()

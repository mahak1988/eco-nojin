#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  🧹 Econojin Cleanup v2.0 - پاکسازی پروژه
  نسخه: 2.0.0
  سازنده: Super Z (Z.ai)
============================================================

یک اسکریپت ساده، سریع و قابل اعتماد برای پاکسازی پروژه.

⚡ ویژگی‌ها:
  • حالت پیش‌نمایش (Dry-Run) به‌صورت پیش‌فرض
  • تأیید قبل از هر عملیات
  • گزارش کامل JSON
  • بدون وابستگی خارجی
  • سازگار با Windows / Linux / macOS
  • محافظت از فایل‌های مهم (مثل .venv فعال)

📋 کارهایی که انجام می‌دهد:
  1. حذف فایل‌های غیرضروری ریشه
  2. انتقال اسکریپت‌های پراکنده به scripts/
  3. حذف پوشه‌های پشتیبان و آرشیو
  4. حذف cache پکیج‌ها (.pnpm-store, .venv-1, .venv-2)
  5. شناسایی فایل‌های تکراری
  6. بررسی .gitignore
  7. پیشنهاد بهبود

🚀 نحوه اجرا:
  python cleanup_v2.py                              # فقط گزارش
  python cleanup_v2.py --execute                    # اجرا با تأیید
  python cleanup_v2.py --execute --force            # اجرای خودکار
  python cleanup_v2.py "D:\\my-project" --execute   # مسیر دلخواه
  python cleanup_v2.py --no-color                   # بدون رنگ
"""

import os
import sys
import re
import json
import hashlib
import argparse
import platform
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict


# ============================================================
#  رنگ‌ها
# ============================================================
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

    @staticmethod
    def disable():
        for attr in dir(C):
            if attr.isupper():
                setattr(C, attr, "")


# ============================================================
#  پیکربندی
# ============================================================

# فایل‌های غیرضروری در ریشه (حذف قطعی)
JUNK_FILES = {
    'files.txt',
    'report.json',
    'orphans_list.txt',
    'dependency_graph.dot',
    'MERGE_PLAN.json',
    'project_analyzer',           # کپی بدون پسوند
    'react-18.2.0.tgz',           # پکیج آفلاین
    'restore_from_backup.ps1',    # اسکریپت بازیابی قدیمی
    'fix_venv.ps1',               # فایل خالی
}

# اسکریپت‌هایی که باید به scripts/ منتقل بشن
SCRIPTS_TO_MOVE = {
    'eco.py',
    'migration_script.py',
    'discover.py',
    'run_econojin.py',
    'analyze_project.py',
    'apps_analyzer_v1.1.py',
    'apps_analyzer_v1.2.py',
    'dependency_analyzer.py',
    'deep_secret_scanner.py',
    'project_analyzer.py',
    'install_venv.ps1',
    'install_packages.sh',
    'setup_dev.sh',
}

# پوشه‌های پشتیبان (حذف قطعی)
BACKUP_DIRS = {
    '.cleanup_backup',
    '.migration_backup',
    '.structure_backup',
    'apps_backup_20260711_025121',
    '_COLD_STORAGE',
    'cold_storage',
    'archive',
}

# پوشه‌های cache/venv اضافی (حذف قطعی)
# توجه: .venv (محیط فعال) در این لیست نیست!
CACHE_DIRS = {
    '.pnpm-store',     # cache پکیج‌ها (3.43 GB!)
    '.venv-1',         # محیط قدیمی
    '.venv-2',         # محیط قدیمی
    'venv-1',
    'venv-2',
}

# پسوندهای فایل‌های باینری که نباید در repo باشن
BINARY_EXTS = {'.safetensors', '.bin', '.pth', '.pt', '.ckpt', '.onnx'}

# پسوندهای فایل‌های دیتابیس
DB_EXTS = {'.db', '.sqlite', '.sqlite3', '.mdb'}

# پوشه‌هایی که نباید اسکن بشن
SKIP_DIRS = {
    'node_modules', '.git', '__pycache__', '.next', '.nuxt', 'dist',
    'build', '.cache', '.pytest_cache', '.mypy_cache',
    '.gradle', 'target', 'bin', 'obj',
    'analysis_reports', 'scripts',
    # محیط فعال - هرگز اسکن/حذف نشه
    '.venv',
}

# الگوهای ضروری .gitignore
REQUIRED_GITIGNORE = {
    'node_modules': 'node_modules',
    '.env': r'\.env',
    '__pycache__': '__pycache__',
    '.venv': r'\.venv',
    'dist': r'^dist',
    'build': r'^build',
    '.pnpm-store': r'\.pnpm-store',
    '*.db': r'\*\.db',
    '*.log': r'\*\.log',
    '.DS_Store': r'\.DS_Store',
    '*.safetensors': r'\*\.safetensors',
}


# ============================================================
#  کلاس اصلی
# ============================================================
class Cleaner:
    def __init__(self, project_path: str, dry_run: bool = True, force: bool = False):
        self.path = Path(project_path).resolve()
        self.dry_run = dry_run
        self.force = force
        self.reclaimed = 0
        self.deleted_files = 0
        self.deleted_dirs = 0
        self.moved_files = 0
        self.skipped = 0
        self.report = {
            "meta": {
                "project": str(self.path),
                "timestamp": datetime.now().isoformat(),
                "mode": "dry-run" if dry_run else "execute",
                "platform": platform.system(),
            },
            "actions": [],
            "skipped": [],
            "warnings": [],
        }

    # ----------------------------------------------------------
    def _h(self, size: int) -> str:
        """حجم قابل خواندن."""
        for u in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.2f} {u}"
            size /= 1024
        return f"{size:.2f} PB"

    def _dir_size(self, d: Path) -> int:
        """محاسبه حجم پوشه."""
        total = 0
        try:
            for root, dirs, files in os.walk(d):
                dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
                for f in files:
                    try:
                        total += (Path(root) / f).stat().st_size
                    except:
                        pass
        except:
            pass
        return total

    def _confirm(self, msg: str) -> bool:
        if self.force or self.dry_run:
            return True
        r = input(f"  {C.YELLOW}{msg} (y/N): {C.RESET}").strip().lower()
        return r in ['y', 'yes']

    def _log(self, action: str, target: str, size: int = 0, status: str = "ok"):
        self.report['actions'].append({
            "action": action,
            "target": target,
            "size": size,
            "status": status,
        })

    # ============================================================
    #  بخش ۱: حذف فایل‌های junk
    # ============================================================
    def step1_junk_files(self):
        print(f"\n{C.CYAN}{C.BOLD}━━━ ۱. فایل‌های غیرضروری ━━━{C.RESET}")
        found = []
        for name in JUNK_FILES:
            f = self.path / name
            if f.exists() and f.is_file():
                size = f.stat().st_size
                found.append((f, size))
                self.reclaimed += size

        if not found:
            print(f"  {C.GREEN}✓ همه چیز تمیز است{C.RESET}")
            return

        print(f"  {C.YELLOW}{len(found)} فایل پیدا شد:{C.RESET}")
        for f, size in found:
            print(f"    {C.RED}✗{C.RESET} {self._h(size):>10}  {f.name}")

        if self.dry_run:
            print(f"  {C.GRAY}(حالت پیش‌نمایش - حذف نمی‌شود){C.RESET}")
            return

        for f, size in found:
            if self._confirm(f"حذف '{f.name}'؟"):
                try:
                    f.unlink()
                    self.deleted_files += 1
                    self._log('delete_file', str(f), size)
                    print(f"    {C.GREEN}✓ حذف شد:{C.RESET} {f.name}")
                except Exception as e:
                    self.report['warnings'].append(f"خطا در حذف {f}: {e}")
                    print(f"    {C.RED}✗ خطا:{C.RESET} {e}")

    # ============================================================
    #  بخش ۲: انتقال اسکریپت‌ها
    # ============================================================
    def step2_move_scripts(self):
        print(f"\n{C.CYAN}{C.BOLD}━━━ ۲. انتقال اسکریپت‌ها به scripts/ ━━━{C.RESET}")
        found = []
        for name in SCRIPTS_TO_MOVE:
            f = self.path / name
            if f.exists() and f.is_file():
                found.append(f)

        if not found:
            print(f"  {C.GREEN}✓ اسکریپت پراکنده‌ای نیست{C.RESET}")
            return

        print(f"  {C.YELLOW}{len(found)} اسکریپت پیدا شد:{C.RESET}")
        for f in found:
            print(f"    {C.BLUE}→{C.RESET} {f.name}")

        if self.dry_run:
            print(f"  {C.GRAY}(حالت پیش‌نمایش - انتقال نمی‌شود){C.RESET}")
            return

        scripts_dir = self.path / 'scripts'
        scripts_dir.mkdir(exist_ok=True)

        for f in found:
            if self._confirm(f"انتقال '{f.name}'؟"):
                try:
                    dst = scripts_dir / f.name
                    if dst.exists():
                        dst.unlink()
                    shutil.move(str(f), str(dst))
                    self.moved_files += 1
                    self._log('move', f"{f} → {dst}")
                    print(f"    {C.GREEN}✓ منتقل شد:{C.RESET} {f.name}")
                except Exception as e:
                    self.report['warnings'].append(f"خطا در انتقال {f}: {e}")
                    print(f"    {C.RED}✗ خطا:{C.RESET} {e}")

    # ============================================================
    #  بخش ۳: حذف پوشه‌های پشتیبان
    # ============================================================
    def step3_backup_dirs(self):
        print(f"\n{C.CYAN}{C.BOLD}━━━ ۳. پوشه‌های پشتیبان و آرشیو ━━━{C.RESET}")
        found = []
        for name in BACKUP_DIRS:
            d = self.path / name
            if d.exists() and d.is_dir():
                size = self._dir_size(d)
                found.append((d, size))
                self.reclaimed += size

        if not found:
            print(f"  {C.GREEN}✓ پوشه پشتیبانی نیست{C.RESET}")
            return

        print(f"  {C.YELLOW}{len(found)} پوشه پیدا شد:{C.RESET}")
        for d, size in found:
            print(f"    {C.RED}✗{C.RESET} {self._h(size):>10}  {d.name}/")

        if self.dry_run:
            print(f"  {C.GRAY}(حالت پیش‌نمایش - حذف نمی‌شود){C.RESET}")
            return

        for d, size in found:
            if self._confirm(f"حذف پوشه '{d.name}' ({self._h(size)})؟"):
                try:
                    shutil.rmtree(d)
                    self.deleted_dirs += 1
                    self._log('delete_dir', str(d), size)
                    print(f"    {C.GREEN}✓ حذف شد:{C.RESET} {d.name}/")
                except Exception as e:
                    self.report['warnings'].append(f"خطا در حذف {d}: {e}")
                    print(f"    {C.RED}✗ خطا:{C.RESET} {e}")

    # ============================================================
    #  بخش ۴: حذف cache ها
    # ============================================================
    def step4_cache_dirs(self):
        print(f"\n{C.CYAN}{C.BOLD}━━━ ۴. پوشه‌های cache و venv قدیمی ━━━{C.RESET}")
        print(f"  {C.GRAY}(محیط فعال .venv/ محافظت می‌شود){C.RESET}")

        found = []
        for name in CACHE_DIRS:
            d = self.path / name
            if d.exists() and d.is_dir():
                size = self._dir_size(d)
                found.append((d, size))
                self.reclaimed += size

        if not found:
            print(f"  {C.GREEN}✓ پوشه cache اضافی نیست{C.RESET}")
            return

        print(f"  {C.YELLOW}{len(found)} پوشه پیدا شد:{C.RESET}")
        for d, size in found:
            print(f"    {C.RED}✗{C.RESET} {self._h(size):>10}  {d.name}/")

        if self.dry_run:
            print(f"  {C.GRAY}(حالت پیش‌نمایش - حذف نمی‌شود){C.RESET}")
            return

        for d, size in found:
            if self._confirm(f"حذف پوشه '{d.name}' ({self._h(size)})؟"):
                try:
                    shutil.rmtree(d)
                    self.deleted_dirs += 1
                    self._log('delete_cache', str(d), size)
                    print(f"    {C.GREEN}✓ حذف شد:{C.RESET} {d.name}/")
                except Exception as e:
                    self.report['warnings'].append(f"خطا در حذف {d}: {e}")
                    print(f"    {C.RED}✗ خطا:{C.RESET} {e}")

    # ============================================================
    #  بخش ۵: فایل‌های باینری و دیتابیس
    # ============================================================
    def step5_binary_db(self):
        print(f"\n{C.CYAN}{C.BOLD}━━━ ۵. فایل‌های باینری و دیتابیس ━━━{C.RESET}")
        binaries = []
        databases = []

        for root, dirs, files in os.walk(self.path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and d not in BACKUP_DIRS and d not in CACHE_DIRS]
            for f in files:
                fp = Path(root) / f
                ext = fp.suffix.lower()
                if ext in BINARY_EXTS:
                    try:
                        size = fp.stat().st_size
                        binaries.append((fp, size))
                        self.reclaimed += size
                    except:
                        pass
                elif ext in DB_EXTS:
                    try:
                        size = fp.stat().st_size
                        databases.append((fp, size))
                    except:
                        pass

        if binaries:
            print(f"\n  {C.YELLOW}فایل‌های باینری ({len(binaries)}):{C.RESET}")
            for fp, size in binaries:
                rel = fp.relative_to(self.path)
                print(f"    {C.MAGENTA}📦{C.RESET} {self._h(size):>10}  {rel}")
                self.report['warnings'].append(f"binary: {rel} ({self._h(size)}) - اگه مدل ML نیاز دارد، به .gitignore اضافه کن")

        if databases:
            print(f"\n  {C.YELLOW}فایل‌های دیتابیس ({len(databases)}):{C.RESET}")
            for fp, size in databases:
                rel = fp.relative_to(self.path)
                print(f"    {C.YELLOW}🗄️{C.RESET} {self._h(size):>10}  {rel}")

        if not binaries and not databases:
            print(f"  {C.GREEN}✓ فایل باینری/دیتابیسی نیست{C.RESET}")

        # پیشنهاد به .gitignore اضافه کردن
        if binaries or databases:
            print(f"\n  {C.CYAN}💡 پیشنهاد:{C.RESET} این فایل‌ها رو به .gitignore اضافه کن:")
            if binaries:
                print(f"     {C.GRAY}*.safetensors{C.RESET}")
                print(f"     {C.GRAY}*.bin{C.RESET}")
                print(f"     {C.GRAY}*.onnx{C.RESET}")
                print(f"     {C.GRAY}models/{C.RESET}")
            if databases:
                print(f"     {C.GRAY}*.db{C.RESET}")
                print(f"     {C.GRAY}*.sqlite{C.RESET}")
                print(f"     {C.GRAY}*.sqlite3{C.RESET}")

    # ============================================================
    #  بخش ۶: بررسی .gitignore
    # ============================================================
    def step6_gitignore(self):
        print(f"\n{C.CYAN}{C.BOLD}━━━ ۶. بررسی .gitignore ━━━{C.RESET}")
        gi = self.path / '.gitignore'
        if not gi.exists():
            print(f"  {C.RED}✗ فایل .gitignore وجود ندارد!{C.RESET}")
            self.report['warnings'].append(".gitignore missing")
            return

        content = gi.read_text(encoding='utf-8', errors='ignore')
        missing = []
        for name, pattern in REQUIRED_GITIGNORE.items():
            if not re.search(pattern, content, re.MULTILINE):
                missing.append(name)

        if missing:
            print(f"  {C.YELLOW}{len(missing)} الگو ناقص است:{C.RESET}")
            for m in missing:
                print(f"    {C.YELLOW}⚠{C.RESET} {m}")

            # اضافه‌ کردن خودکار
            if not self.dry_run and self._confirm("اضافه کردن الگوهای ناقص به .gitignore؟"):
                with open(gi, 'a', encoding='utf-8') as f:
                    f.write("\n# Added by cleanup_v2.py\n")
                    for m in missing:
                        if m == 'node_modules':
                            f.write("node_modules/\n")
                        elif m == '.env':
                            f.write(".env\n.env.local\n.env.*.local\n")
                        elif m == '__pycache__':
                            f.write("__pycache__/\n*.pyc\n")
                        elif m == '.venv':
                            f.write(".venv/\n.venv-*/\nvenv/\nvenv-*/\n")
                        elif m == 'dist':
                            f.write("dist/\n")
                        elif m == 'build':
                            f.write("build/\n")
                        elif m == '.pnpm-store':
                            f.write(".pnpm-store/\n")
                        elif m == '*.db':
                            f.write("*.db\n*.sqlite\n*.sqlite3\n")
                        elif m == '*.log':
                            f.write("*.log\n")
                        elif m == '.DS_Store':
                            f.write(".DS_Store\nThumbs.db\n")
                        elif m == '*.safetensors':
                            f.write("*.safetensors\n*.bin\n*.onnx\nmodels/\n")
                print(f"  {C.GREEN}✓ .gitignore به‌روزرسانی شد{C.RESET}")
                self._log('update_gitignore', str(gi))
        else:
            print(f"  {C.GREEN}✓ .gitignore کامل است{C.RESET}")

    # ============================================================
    #  بخش ۷: خلاصه
    # ============================================================
    def summary(self):
        print(f"\n{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}  📊 خلاصه{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}{'━'*50}{C.RESET}")

        if self.dry_run:
            print(f"  {C.YELLOW}حالت پیش‌نمایش{C.RESET} — هیچ تغییری اعمال نشد")
            print(f"  {C.GRAY}برای اجرای واقعی از --execute استفاده کن{C.RESET}")
            print()
            print(f"  {C.CYAN}فضای قابل بازیابی:{C.RESET} {C.GREEN}{C.BOLD}{self._h(self.reclaimed)}{C.RESET}")
        else:
            print(f"  {C.GREEN}✓ فایل‌های حذف شده:{C.RESET} {self.deleted_files}")
            print(f"  {C.GREEN}✓ پوشه‌های حذف شده:{C.RESET} {self.deleted_dirs}")
            print(f"  {C.GREEN}✓ فایل‌های منتقل شده:{C.RESET} {self.moved_files}")
            print(f"  {C.CYAN}فضای بازیابی شده:{C.RESET} {C.GREEN}{C.BOLD}{self._h(self.reclaimed)}{C.RESET}")
            if self.report['warnings']:
                print(f"  {C.YELLOW}⚠ هشدارها:{C.RESET} {len(self.report['warnings'])}")

        # ذخیره گزارش
        reports_dir = self.path / 'analysis_reports'
        reports_dir.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"cleanup_v2_{ts}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        print(f"\n  {C.GRAY}گزارش:{C.RESET} {report_path}")

    # ============================================================
    #  اجرا
    # ============================================================
    def run(self):
        print(f"\n{C.MAGENTA}{C.BOLD}╔{'═'*58}╗{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  🧹 Cleanup v2.0 - پاکسازی پروژه econojin{' '*11}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}║  مسیر: {str(self.path):<51}║{C.RESET}")
        mode = "پیش‌نمایش (Dry-Run)" if self.dry_run else "اجرا (Execute)"
        print(f"{C.MAGENTA}{C.BOLD}║  حالت: {mode:<49}║{C.RESET}")
        print(f"{C.MAGENTA}{C.BOLD}╚{'═'*58}╝{C.RESET}")

        if not self.path.exists():
            print(f"{C.RED}❌ مسیر وجود ندارد!{C.RESET}")
            return False

        self.step1_junk_files()
        self.step2_move_scripts()
        self.step3_backup_dirs()
        self.step4_cache_dirs()
        self.step5_binary_db()
        self.step6_gitignore()
        self.summary()

        print(f"\n{C.GREEN}{C.BOLD}✓ کامل شد!{C.RESET}\n")
        return True


# ============================================================
#  ورودی
# ============================================================
def main():
    C.enable_windows()

    parser = argparse.ArgumentParser(
        description='پاکسازی پروژه econojin v2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌ها:
  python cleanup_v2.py                              # فقط پیش‌نمایش
  python cleanup_v2.py --execute                    # اجرا با تأیید
  python cleanup_v2.py --execute --force            # اجرای خودکار
  python cleanup_v2.py "D:\\econojin.com" --execute # مسیر دلخواه
        """
    )
    parser.add_argument('path', nargs='?', default=r'D:\econojin.com',
                        help='مسیر پروژه (پیش‌فرض: D:\\econojin.com)')
    parser.add_argument('--execute', action='store_true',
                        help='اجرای واقعی (پیش‌فرض: dry-run)')
    parser.add_argument('--force', action='store_true',
                        help='بدون تأیید برای هر مورد')
    parser.add_argument('--no-color', action='store_true',
                        help='غیرفعال کردن رنگ')

    args = parser.parse_args()

    if args.no_color:
        C.disable()

    cleaner = Cleaner(
        project_path=args.path,
        dry_run=not args.execute,
        force=args.force,
    )
    success = cleaner.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

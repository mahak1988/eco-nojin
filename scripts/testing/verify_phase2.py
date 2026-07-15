#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 2 Diagnostic & Fix v2.0
==========================================
تشخیص دقیق مشکلات و رفع خودکار

نحوه اجرا:
    python scripts/testing/verify_phase2.py
"""

import sys
import os
import shutil
import re
from pathlib import Path
from typing import List, Tuple, Dict, Set
from collections import defaultdict

# ============================================================
# تنظیم مسیر پروژه (مهم!)
# ============================================================

# پیدا کردن ریشه پروژه با جستجوی فایل‌های مشخص
def find_project_root() -> Path:
    """پیدا کردن ریشه پروژه با جستجوی apps/"""
    current = Path(__file__).resolve().parent
    
    # جستجو تا ۵ سطح بالا
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    
    # اگر پیدا نشد، از مسیر فعلی استفاده کن
    return Path.cwd()

PROJECT_ROOT = find_project_root()
APPS_DIR = PROJECT_ROOT / "apps"

# اضافه کردن به sys.path (حل مشکل No module named 'apps')
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"📂 ریشه پروژه: {PROJECT_ROOT}")
print(f"📂 پوشه apps: {APPS_DIR}")
print(f"📂 sys.path: {sys.path[0]}")

# ============================================================
# Terminal Colors (اصلاح شده)
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# Diagnostic Class
# ============================================================

class Phase2Diagnostic:
    def __init__(self):
        self.checks: List[Tuple[str, bool, str]] = []
        self.fixes_applied: List[str] = []
        self.found_files: Dict[str, List[Path]] = defaultdict(list)
    
    def diagnose_and_fix(self) -> bool:
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("🔍 Phase 2 Diagnostic & Fix v2.0", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        # ۱. اسکن کامل فایل‌سیستم
        self._scan_filesystem()
        
        # ۲. بررسی ماژول‌های جدید
        self._check_new_modules()
        
        # ۳. بررسی پوشه shared قدیمی
        self._check_old_shared()
        
        # ۴. بررسی importها
        self._check_imports()
        
        # ۵. اعمال اصلاحات
        self._apply_fixes()
        
        # ۶. چاپ نتایج
        self._print_results()
        
        passed = sum(1 for _, success, _ in self.checks if success)
        total = len(self.checks)
        
        return passed == total
    
    def _scan_filesystem(self):
        """اسکن کامل فایل‌سیستم برای یافتن فایل‌های منتقل‌شده"""
        cprint("\n🔎 گام ۱: اسکن فایل‌سیستم...", Colors.BLUE)
        
        if not APPS_DIR.exists():
            cprint(f"   ❌ پوشه apps یافت نشد: {APPS_DIR}", Colors.RED)
            return
        
        # لیست تمام دایرکتوری‌ها در apps/
        cprint(f"\n   📁 دایرکتوری‌های apps/:")
        for item in sorted(APPS_DIR.iterdir()):
            if item.is_dir():
                file_count = len(list(item.rglob("*.py")))
                cprint(f"      • {item.name}/ ({file_count} فایل Python)", Colors.CYAN)
        
        # جستجوی فایل‌های کلیدی
        key_files = [
            "session.py",
            "repository.py",
            "base_agent.py",
            "llm_factory.py",
            "models.py",
        ]
        
        cprint(f"\n   🔍 جستجوی فایل‌های کلیدی:")
        for key_file in key_files:
            found = list(APPS_DIR.rglob(key_file))
            if found:
                self.found_files[key_file] = found
                cprint(f"      ✅ {key_file}:", Colors.GREEN)
                for f in found:
                    rel = f.relative_to(PROJECT_ROOT)
                    cprint(f"         → {rel}", Colors.DIM)
            else:
                cprint(f"      ❌ {key_file} یافت نشد", Colors.RED)
    
    def _check_new_modules(self):
        """بررسی وجود ماژول‌های جدید"""
        cprint("\n📦 گام ۲: بررسی ماژول‌های جدید...", Colors.BLUE)
        
        modules = ["shared-core", "shared-ai", "shared-sim", "shared-knowledge"]
        
        for module in modules:
            module_path = APPS_DIR / module
            init_file = module_path / "__init__.py"
            
            exists = module_path.exists()
            has_init = init_file.exists()
            
            if exists and has_init:
                file_count = len(list(module_path.rglob("*.py")))
                msg = f"{module} OK ({file_count} فایل)"
                success = True
                cprint(f"   ✅ {msg}", Colors.GREEN)
            elif exists:
                msg = f"{module} وجود دارد اما __init__.py ندارد"
                success = False
                cprint(f"   ⚠️  {msg}", Colors.YELLOW)
            else:
                msg = f"{module} ایجاد نشده"
                success = False
                cprint(f"   ❌ {msg}", Colors.RED)
            
            self.checks.append((f"Module: {module}", success, msg))
    
    def _check_old_shared(self):
        """بررسی پوشه shared قدیمی"""
        cprint("\n🗑️  گام ۳: بررسی پوشه shared قدیمی...", Colors.BLUE)
        
        shared_dir = APPS_DIR / "shared"
        
        if not shared_dir.exists():
            cprint("   ✅ پوشه shared حذف شده", Colors.GREEN)
            self.checks.append(("Old shared removed", True, "حذف شده"))
            return
        
        # بررسی محتویات
        py_files = list(shared_dir.rglob("*.py"))
        
        if not py_files:
            cprint(f"   ⚠️  پوشه shared وجود دارد اما خالی است (یا فقط cache)", Colors.YELLOW)
            try:
                shutil.rmtree(shared_dir)
                cprint("   ✅ پوشه shared حذف شد", Colors.GREEN)
                self.checks.append(("Old shared removed", True, "حذف شد"))
                self.fixes_applied.append("Removed empty shared directory")
            except Exception as e:
                cprint(f"   ❌ خطا در حذف: {e}", Colors.RED)
                self.checks.append(("Old shared removed", False, f"خطا: {e}"))
        else:
            cprint(f"   ❌ {len(py_files)} فایل Python در shared باقی‌مانده:", Colors.RED)
            for f in py_files[:10]:
                cprint(f"      • {f.relative_to(shared_dir)}", Colors.RED)
            self.checks.append(("Old shared removed", False, f"{len(py_files)} فایل باقی‌مانده"))
    
    def _check_imports(self):
        """بررسی صحت importها"""
        cprint("\n🔄 گام ۴: بررسی importها...", Colors.BLUE)
        
        test_imports = [
            ("shared-core database", "from apps.shared_core.database.session import get_db"),
            ("shared-ai llm", "from apps.shared_ai.ai.llm_factory import get_llm"),
            ("main app", "from apps.main import app"),
        ]
        
        for name, import_stmt in test_imports:
            try:
                exec(import_stmt)
                cprint(f"   ✅ {name}", Colors.GREEN)
                self.checks.append((f"Import: {name}", True, "OK"))
            except Exception as e:
                error_msg = str(e).split('\n')[0]
                cprint(f"   ❌ {name}: {error_msg}", Colors.RED)
                self.checks.append((f"Import: {name}", False, error_msg))
    
    def _apply_fixes(self):
        """اعمال اصلاحات"""
        cprint("\n🔧 گام ۵: اعمال اصلاحات...", Colors.BLUE)
        
        # اصلاح ۱: ایجاد __init__.py برای ماژول‌های موجود
        self._create_missing_init_files()
        
        # اصلاح ۲: حذف پوشه shared قدیمی
        self._remove_old_shared_if_empty()
        
        # اصلاح ۳: اصلاح importهای قدیمی
        self._fix_old_imports()
        
        # اصلاح ۴: بررسی و اصلاح ساختار
        self._fix_structure()
        
        if self.fixes_applied:
            cprint(f"\n   📊 {len(self.fixes_applied)} اصلاح اعمال شد:", Colors.GREEN)
            for fix in self.fixes_applied:
                cprint(f"      • {fix}", Colors.GREEN)
        else:
            cprint("   ℹ️  نیازی به اصلاح نبود", Colors.CYAN)
    
    def _create_missing_init_files(self):
        """ایجاد __init__.py برای ماژول‌های موجود"""
        modules = ["shared-core", "shared-ai", "shared-sim", "shared-knowledge"]
        
        for module in modules:
            module_path = APPS_DIR / module
            if module_path.exists():
                init_file = module_path / "__init__.py"
                if not init_file.exists():
                    try:
                        content = f'"""Eco Nojin - {module} module"""\n\n__version__ = "1.0.0"\n'
                        init_file.write_text(content, encoding="utf-8")
                        cprint(f"   ✅ ایجاد شد: {module}/__init__.py", Colors.GREEN)
                        self.fixes_applied.append(f"Created {module}/__init__.py")
                    except Exception as e:
                        cprint(f"   ❌ خطا در ایجاد {module}/__init__.py: {e}", Colors.RED)
    
    def _remove_old_shared_if_empty(self):
        """حذف پوشه shared اگر خالی است"""
        shared_dir = APPS_DIR / "shared"
        if shared_dir.exists():
            py_files = list(shared_dir.rglob("*.py"))
            if not py_files:
                try:
                    shutil.rmtree(shared_dir)
                    cprint(f"   🗑️  حذف شد: shared/", Colors.YELLOW)
                    self.fixes_applied.append("Removed empty shared directory")
                except Exception as e:
                    cprint(f"   ❌ خطا در حذف shared: {e}", Colors.RED)
    
    def _fix_old_imports(self):
        """اصلاح importهای قدیمی"""
        old_pattern = re.compile(r'from\s+apps\.shared\.')
        files_fixed = 0
        
        for py_file in APPS_DIR.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                
                if old_pattern.search(content):
                    # جایگزینی importها
                    new_content = content
                    new_content = re.sub(r'from\s+apps\.shared\.database\.', 'from apps.shared_core.database.', new_content)
                    new_content = re.sub(r'from\s+apps\.shared\.ai\.', 'from apps.shared_ai.ai.', new_content)
                    new_content = re.sub(r'from\s+apps\.shared\.knowledge\.', 'from apps.shared_knowledge.knowledge.', new_content)
                    new_content = re.sub(r'from\s+apps\.shared\.utils\.', 'from apps.shared_core.utils.', new_content)
                    new_content = re.sub(r'from\s+apps\.shared\.schemas\.', 'from apps.shared_core.schemas.', new_content)
                    
                    if new_content != content:
                        py_file.write_text(new_content, encoding="utf-8")
                        files_fixed += 1
            except Exception:
                continue
        
        if files_fixed > 0:
            cprint(f"   🔄 {files_fixed} فایل با import قدیمی اصلاح شد", Colors.GREEN)
            self.fixes_applied.append(f"Fixed imports in {files_fixed} files")
    
    def _fix_structure(self):
        """بررسی و اصلاح ساختار"""
        # بررسی اینکه فایل‌های کلیدی در جای درست هستند
        expected_structure = {
            "shared-core": ["database/session.py", "database/repository.py"],
            "shared-ai": ["ai/base_agent.py", "ai/llm_factory.py"],
            "shared-knowledge": ["knowledge/models.py"],
        }
        
        for module, files in expected_structure.items():
            module_path = APPS_DIR / module
            if not module_path.exists():
                cprint(f"   ⚠️  {module} وجود ندارد - نیاز به بررسی دستی", Colors.YELLOW)
                continue
            
            for file_rel in files:
                file_path = module_path / file_rel
                if not file_path.exists():
                    # جستجو در جای دیگر
                    file_name = Path(file_rel).name
                    if file_name in self.found_files:
                        found_locations = self.found_files[file_name]
                        if len(found_locations) == 1:
                            # فقط یک جا پیدا شده - احتمالاً مسیر درست است
                            actual_path = found_locations[0]
                            expected_rel = actual_path.relative_to(module_path)
                            cprint(f"   ℹ️  {file_name} در {expected_rel} یافت شد", Colors.CYAN)
    
    def _print_results(self):
        """چاپ نتایج نهایی"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📊 نتایج بررسی", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        passed = sum(1 for _, success, _ in self.checks if success)
        total = len(self.checks)
        failed = total - passed
        
        cprint(f"\n   ✅ Passed: {Colors.GREEN}{passed}{Colors.END}")
        cprint(f"   ❌ Failed: {Colors.RED}{failed}{Colors.END}")
        cprint(f"   📊 Total:  {Colors.BOLD}{total}{Colors.END}")
        
        if failed > 0:
            cprint(f"\n   {Colors.RED}❌ بررسی‌های ناموفق:{Colors.END}")
            for name, success, msg in self.checks:
                if not success:
                    cprint(f"      • {name}: {msg}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if failed == 0:
            cprint("\n✅ فاز ۲ با موفقیت کامل تأیید شد!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
            cprint("   1. اجرای سرور: python apps/main.py")
            cprint("   2. اجرای تست‌ها: pytest apps/*/tests/")
            cprint("   3. Commit: git add . && git commit -m 'Phase 2 complete'")
        else:
            cprint(f"\n❌ {failed} بررسی ناموفق بود.", Colors.RED)
            cprint("\n💡 اقدامات پیشنهادی:", Colors.YELLOW)
            cprint("   1. بررسی دستی ساختار پوشه‌ها")
            cprint("   2. اجرای: tree apps /F")
            cprint("   3. در صورت نیاز، rollback:")
            cprint("      python scripts/phase2_split_shared.py --rollback")

# ============================================================
# Main
# ============================================================

def main():
    diagnostic = Phase2Diagnostic()
    success = diagnostic.diagnose_and_fix()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطای غیرمنتظره: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
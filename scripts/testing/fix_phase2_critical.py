#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 2 Critical Fix
=================================
رفع ۳ باگ بحرانی فاز ۲

نحوه اجرا:
    python scripts/testing/fix_phase2_critical.py
"""

import sys
import os
import shutil
import re
from pathlib import Path
from typing import List, Dict, Tuple

# ============================================================
# تنظیم مسیر
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()
APPS_DIR = PROJECT_ROOT / "apps"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"📂 ریشه پروژه: {PROJECT_ROOT}")

# ============================================================
# Colors
# ============================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# Fix Script
# ============================================================

class Phase2CriticalFix:
    def __init__(self):
        self.fixes_applied: List[str] = []
        self.errors: List[str] = []
        
        # نقشه تغییر نام
        self.rename_map = {
            "shared-core": "shared_core",
            "shared-ai": "shared_ai",
            "shared-sim": "shared_sim",
            "shared-knowledge": "shared_knowledge",
        }
        
        # نقشه اصلاح import
        self.import_fix_map = {
            "apps.shared-core": "apps.shared_core",
            "apps.shared-ai": "apps.shared_ai",
            "apps.shared-sim": "apps.shared_sim",
            "apps.shared-knowledge": "apps.shared_knowledge",
        }
    
    def execute(self):
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("🔧 Phase 2 Critical Fix", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        # گام ۱: تغییر نام پوشه‌ها
        self._rename_modules()
        
        # گام ۲: حذف shared قدیمی
        self._remove_old_shared()
        
        # گام ۳: بررسی و اصلاح main.py
        self._fix_main_py()
        
        # گام ۴: به‌روزرسانی تمام importها
        self._fix_all_imports()
        
        # گام ۵: ایجاد __init__.py در تمام زیرپوشه‌ها
        self._create_all_init_files()
        
        # گام ۶: تست نهایی
        self._test_imports()
        
        # چاپ نتایج
        self._print_results()
    
    def _rename_modules(self):
        """تغییر نام پوشه‌ها از shared-* به shared_*"""
        cprint("\n📝 گام ۱: تغییر نام پوشه‌ها...", Colors.BLUE)
        
        for old_name, new_name in self.rename_map.items():
            old_path = APPS_DIR / old_name
            new_path = APPS_DIR / new_name
            
            if not old_path.exists():
                if new_path.exists():
                    cprint(f"   ⏩ {old_name} قبلاً به {new_name} تغییر نام داده", Colors.DIM)
                else:
                    cprint(f"   ⚠️  {old_name} یافت نشد", Colors.YELLOW)
                continue
            
            if new_path.exists():
                cprint(f"   ⚠️  {new_name} از قبل وجود دارد. ادغام...", Colors.YELLOW)
                # ادغام فایل‌ها
                for item in old_path.rglob("*"):
                    if item.is_file():
                        rel = item.relative_to(old_path)
                        dest = new_path / rel
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item), str(dest))
                shutil.rmtree(old_path)
                cprint(f"   ✅ ادغام و حذف {old_name}", Colors.GREEN)
            else:
                try:
                    old_path.rename(new_path)
                    cprint(f"   ✅ {old_name} → {new_name}", Colors.GREEN)
                    self.fixes_applied.append(f"Renamed {old_name} to {new_name}")
                except Exception as e:
                    cprint(f"   ❌ خطا: {e}", Colors.RED)
                    self.errors.append(f"Rename error: {e}")
    
    def _remove_old_shared(self):
        """حذف کامل پوشه shared قدیمی"""
        cprint("\n🗑️  گام ۲: حذف پوشه shared قدیمی...", Colors.BLUE)
        
        shared_dir = APPS_DIR / "shared"
        
        if not shared_dir.exists():
            cprint("   ✅ پوشه shared از قبل حذف شده", Colors.GREEN)
            return
        
        try:
            # شمارش فایل‌ها
            files = list(shared_dir.rglob("*"))
            cprint(f"   ℹ️  {len(files)} فایل/پوشه در shared یافت شد", Colors.CYAN)
            
            # حذف کامل
            shutil.rmtree(shared_dir)
            cprint("   ✅ پوشه shared کامل حذف شد", Colors.GREEN)
            self.fixes_applied.append("Removed old shared directory completely")
        except Exception as e:
            cprint(f"   ❌ خطا: {e}", Colors.RED)
            self.errors.append(f"Remove shared error: {e}")
    
    def _fix_main_py(self):
        """بررسی و اصلاح main.py"""
        cprint("\n🔧 گام ۳: بررسی main.py...", Colors.BLUE)
        
        main_file = APPS_DIR / "main.py"
        
        if not main_file.exists():
            cprint("   ⚠️  main.py یافت نشد", Colors.YELLOW)
            return
        
        try:
            content = main_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # نمایش خط ۵ برای بررسی
            if len(lines) >= 5:
                cprint(f"   ℹ️  خط ۵: {lines[4][:80]}", Colors.CYAN)
            
            # بررسی syntax
            try:
                compile(content, str(main_file), "exec")
                cprint("   ✅ main.py syntax OK", Colors.GREEN)
            except SyntaxError as e:
                cprint(f"   ❌ Syntax Error در خط {e.lineno}: {e.msg}", Colors.RED)
                
                # تلاش برای اصلاح
                if "import" in lines[e.lineno - 1] if e.lineno else False:
                    # احتمالاً مشکل از import است
                    cprint("   🔧 تلاش برای اصلاح import...", Colors.YELLOW)
                    
                    # اصلاح importهای اشتباه
                    content = re.sub(r'from\s+apps\.shared-core\.', 'from apps.shared_core.', content)
                    content = re.sub(r'from\s+apps\.shared-ai\.', 'from apps.shared_ai.', content)
                    content = re.sub(r'from\s+apps\.shared-sim\.', 'from apps.shared_sim.', content)
                    content = re.sub(r'from\s+apps\.shared-knowledge\.', 'from apps.shared_knowledge.', content)
                    
                    main_file.write_text(content, encoding="utf-8")
                    cprint("   ✅ main.py اصلاح شد", Colors.GREEN)
                    self.fixes_applied.append("Fixed main.py imports")
                    
                    # تست مجدد
                    try:
                        compile(content, str(main_file), "exec")
                        cprint("   ✅ main.py syntax OK پس از اصلاح", Colors.GREEN)
                    except SyntaxError as e2:
                        cprint(f"   ❌ هنوز syntax error: {e2}", Colors.RED)
                        self.errors.append(f"main.py still has syntax error: {e2}")
        
        except Exception as e:
            cprint(f"   ❌ خطا: {e}", Colors.RED)
            self.errors.append(f"main.py error: {e}")
    
    def _fix_all_imports(self):
        """به‌روزرسانی تمام importها در کل پروژه"""
        cprint("\n🔄 گام ۴: به‌روزرسانی تمام importها...", Colors.BLUE)
        
        files_fixed = 0
        patterns_to_fix = [
            (r'from\s+apps\.shared-core\.', 'from apps.shared_core.'),
            (r'from\s+apps\.shared-ai\.', 'from apps.shared_ai.'),
            (r'from\s+apps\.shared-sim\.', 'from apps.shared_sim.'),
            (r'from\s+apps\.shared-knowledge\.', 'from apps.shared_knowledge.'),
            (r'import\s+apps\.shared-core\.', 'import apps.shared_core.'),
            (r'import\s+apps\.shared-ai\.', 'import apps.shared_ai.'),
            (r'import\s+apps\.shared-sim\.', 'import apps.shared_sim.'),
            (r'import\s+apps\.shared-knowledge\.', 'import apps.shared_knowledge.'),
        ]
        
        for py_file in APPS_DIR.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                original = content
                
                for pattern, replacement in patterns_to_fix:
                    content = re.sub(pattern, replacement, content)
                
                if content != original:
                    py_file.write_text(content, encoding="utf-8")
                    files_fixed += 1
                    cprint(f"   🔄 {py_file.relative_to(PROJECT_ROOT)}", Colors.CYAN)
            except Exception:
                continue
        
        if files_fixed > 0:
            cprint(f"\n   ✅ {files_fixed} فایل اصلاح شد", Colors.GREEN)
            self.fixes_applied.append(f"Fixed imports in {files_fixed} files")
        else:
            cprint("   ℹ️  نیازی به اصلاح import نبود", Colors.CYAN)
    
    def _create_all_init_files(self):
        """ایجاد __init__.py در تمام زیرپوشه‌های ماژول‌های جدید"""
        cprint("\n📝 گام ۵: ایجاد __init__.py در زیرپوشه‌ها...", Colors.BLUE)
        
        modules = ["shared_core", "shared_ai", "shared_sim", "shared_knowledge"]
        created = 0
        
        for module in modules:
            module_path = APPS_DIR / module
            if not module_path.exists():
                continue
            
            # ایجاد __init__.py در خود ماژول
            init_file = module_path / "__init__.py"
            if not init_file.exists():
                init_file.write_text(f'"""Eco Nojin - {module} module"""\n', encoding="utf-8")
                created += 1
            
            # ایجاد __init__.py در تمام زیرپوشه‌ها
            for subdir in module_path.rglob("*"):
                if subdir.is_dir() and not subdir.name.startswith("__"):
                    sub_init = subdir / "__init__.py"
                    if not sub_init.exists():
                        sub_init.write_text(f'"""Submodule of {module}"""\n', encoding="utf-8")
                        created += 1
        
        if created > 0:
            cprint(f"   ✅ {created} فایل __init__.py ایجاد شد", Colors.GREEN)
            self.fixes_applied.append(f"Created {created} __init__.py files")
        else:
            cprint("   ℹ️  تمام __init__.py ها از قبل وجود دارند", Colors.CYAN)
    
    def _test_imports(self):
        """تست نهایی importها"""
        cprint("\n🧪 گام ۶: تست importها...", Colors.BLUE)
        
        test_imports = [
            ("shared_core database", "from apps.shared_core.database.session import get_db"),
            ("shared_ai llm", "from apps.shared_ai.ai.llm_factory import get_llm"),
            ("shared_ai base_agent", "from apps.shared_ai.ai.base_agent import BaseAgent"),
            ("shared_knowledge models", "from apps.shared_knowledge.knowledge.models import KnowledgeItem"),
            ("main app", "from apps.main import app"),
        ]
        
        passed = 0
        for name, import_stmt in test_imports:
            try:
                exec(import_stmt)
                cprint(f"   ✅ {name}", Colors.GREEN)
                passed += 1
            except Exception as e:
                error_msg = str(e).split('\n')[0][:60]
                cprint(f"   ❌ {name}: {error_msg}", Colors.RED)
                self.errors.append(f"Import test failed: {name} - {e}")
        
        cprint(f"\n   📊 {passed}/{len(test_imports)} تست موفق", Colors.CYAN)
    
    def _print_results(self):
        """چاپ نتایج نهایی"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📊 نتایج اصلاحات", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        if self.fixes_applied:
            cprint(f"\n✅ {len(self.fixes_applied)} اصلاح اعمال شد:", Colors.GREEN)
            for fix in self.fixes_applied:
                cprint(f"   • {fix}", Colors.GREEN)
        
        if self.errors:
            cprint(f"\n❌ {len(self.errors)} خطا:", Colors.RED)
            for error in self.errors:
                cprint(f"   • {error}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if not self.errors:
            cprint("\n✅ تمام مشکلات فاز ۲ رفع شد!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
            cprint("   1. اجرای سرور: python apps/main.py")
            cprint("   2. اجرای تست‌ها: pytest apps/*/tests/")
            cprint("   3. Commit: git add . && git commit -m 'fix(phase-2): critical bugs'")
        else:
            cprint("\n⚠️  برخی مشکلات باقی‌مانده. لطفاً دستی بررسی کنید.", Colors.YELLOW)

# ============================================================
# Main
# ============================================================

def main():
    fixer = Phase2CriticalFix()
    fixer.execute()

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
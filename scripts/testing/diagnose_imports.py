#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 2 Deep Import Diagnostic v2.0 (Fixed)
========================================================
اصلاح باگ مسیر دوتایی apps/apps

نحوه اجرا:
    python scripts/testing/diagnose_imports.py
"""

import sys
import os
import ast
import re
from pathlib import Path
from typing import List, Dict

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
# Import Diagnostic (اصلاح شده)
# ============================================================

class ImportDiagnostic:
    def __init__(self):
        self.problems: List[Dict] = []
        self.successes: List[str] = []
    
    def diagnose(self):
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("🔍 Deep Import Diagnostic v2.0", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        problem_files = [
            ("apps.shared_core.database.session", "get_db"),
            ("apps.shared_ai.ai.llm_factory", "get_llm"),
            ("apps.shared_ai.ai.base_agent", "BaseAgent"),
            ("apps.shared_knowledge.knowledge.models", "KnowledgeItem"),
        ]
        
        for module_path, expected_name in problem_files:
            cprint(f"\n📄 بررسی: {module_path}", Colors.BLUE)
            self._analyze_file(module_path, expected_name)
        
        self._print_results()
    
    def _analyze_file(self, module_path: str, expected_name: str):
        """تحلیل دقیق یک فایل - نسخه اصلاح شده"""
        
        # 🔧 اصلاح باگ: حذف پیشوند "apps." از module_path
        if module_path.startswith("apps."):
            relative_path = module_path[5:]  # حذف "apps."
        else:
            relative_path = module_path
        
        # ساخت مسیر صحیح
        file_path = APPS_DIR / relative_path.replace(".", os.sep)
        if not file_path.suffix:
            file_path = file_path.with_suffix(".py")
        
        cprint(f"   📁 مسیر: {file_path.relative_to(PROJECT_ROOT)}", Colors.CYAN)
        
        # بررسی وجود فایل
        if not file_path.exists():
            cprint(f"   ❌ فایل یافت نشد", Colors.RED)
            self.problems.append({
                "module": module_path,
                "expected": expected_name,
                "issue": "file_not_found",
                "file": str(file_path)
            })
            return
        
        # خواندن محتوا
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            cprint(f"   📏 اندازه: {len(content)} کاراکتر، {len(lines)} خط", Colors.DIM)
        except Exception as e:
            cprint(f"   ❌ خطا در خواندن: {e}", Colors.RED)
            return
        
        # Parse AST
        try:
            tree = ast.parse(content, filename=str(file_path))
        except SyntaxError as e:
            cprint(f"   ❌ Syntax Error در خط {e.lineno}: {e.msg}", Colors.RED)
            # نمایش خط مشکل‌دار
            if e.lineno and e.lineno <= len(lines):
                cprint(f"   📝 خط {e.lineno}: {lines[e.lineno-1][:80]}", Colors.YELLOW)
            self.problems.append({
                "module": module_path,
                "expected": expected_name,
                "issue": "syntax_error",
                "line": e.lineno,
                "message": e.msg
            })
            return
        
        # استخراج توابع و کلاس‌ها
        functions = set()
        classes = set()
        imports = []
        errors_in_file = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.add(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.add(node.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        
        cprint(f"   🔧 توابع ({len(functions)}): {', '.join(sorted(functions)[:8])}", Colors.DIM)
        cprint(f"   🏗️  کلاس‌ها ({len(classes)}): {', '.join(sorted(classes)[:8])}", Colors.DIM)
        
        # بررسی وجود نام مورد انتظار
        if expected_name in functions or expected_name in classes:
            cprint(f"   ✅ {expected_name} تعریف شده", Colors.GREEN)
            
            # تست import واقعی
            try:
                exec(f"from {module_path} import {expected_name}")
                cprint(f"   ✅ Import موفق!", Colors.GREEN)
                self.successes.append(module_path)
            except Exception as e:
                error_msg = str(e)
                cprint(f"   ❌ Import ناموفق: {error_msg[:100]}", Colors.RED)
                
                # تحلیل خطا
                if "cannot import name" in error_msg:
                    cprint(f"   💡 علت: خطای داخلی در فایل یا وابستگی‌ها", Colors.YELLOW)
                    self._check_internal_errors(file_path, imports)
                elif "ModuleNotFoundError" in error_msg:
                    cprint(f"   💡 علت: ماژول وابسته یافت نشد", Colors.YELLOW)
                    self._check_internal_errors(file_path, imports)
                
                self.problems.append({
                    "module": module_path,
                    "expected": expected_name,
                    "issue": "import_failed",
                    "error": error_msg
                })
        else:
            cprint(f"   ❌ {expected_name} تعریف نشده", Colors.RED)
            
            # جستجوی نام‌های مشابه
            similar = []
            for name in functions | classes:
                if expected_name.lower() in name.lower() or name.lower() in expected_name.lower():
                    similar.append(name)
            
            if similar:
                cprint(f"   💡 نام‌های مشابه: {', '.join(similar)}", Colors.YELLOW)
            
            # پیشنهاد
            all_names = sorted(functions | classes)
            if all_names:
                cprint(f"   📝 نام‌های موجود: {', '.join(all_names[:10])}", Colors.CYAN)
            
            self.problems.append({
                "module": module_path,
                "expected": expected_name,
                "issue": "name_not_found",
                "available": all_names,
                "similar": similar
            })
    
    def _check_internal_errors(self, file_path: Path, imports: List[str]):
        """بررسی وابستگی‌های داخلی"""
        cprint(f"\n   🔍 بررسی وابستگی‌ها...", Colors.CYAN)
        
        checked = 0
        for imp in imports[:5]:
            if imp.startswith("apps."):
                # 🔧 اصلاح: حذف پیشوند apps.
                if imp.startswith("apps."):
                    rel = imp[5:]
                else:
                    rel = imp
                
                dep_path = APPS_DIR / rel.replace(".", os.sep)
                if not dep_path.suffix:
                    dep_path = dep_path.with_suffix(".py")
                
                if dep_path.exists():
                    cprint(f"      ✅ {imp}", Colors.DIM)
                else:
                    cprint(f"      ❌ {imp} - یافت نشد", Colors.RED)
                checked += 1
        
        if checked == 0:
            cprint(f"      ℹ️  وابستگی داخلی به apps ندارد", Colors.DIM)
    
    def _print_results(self):
        """چاپ نتایج"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📊 نتایج نهایی", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        cprint(f"\n✅ موفق: {Colors.GREEN}{len(self.successes)}{Colors.END}")
        cprint(f"❌ مشکل: {Colors.RED}{len(self.problems)}{Colors.END}")
        
        if self.successes:
            cprint(f"\n{Colors.GREEN}📗 ماژول‌های سالم:{Colors.END}")
            for s in self.successes:
                cprint(f"   ✅ {s}", Colors.GREEN)
        
        if self.problems:
            cprint(f"\n{Colors.RED}📕 مشکلات:{Colors.END}")
            for i, p in enumerate(self.problems, 1):
                cprint(f"\n   {i}. {p['module']}", Colors.BOLD)
                cprint(f"      انتظار: {p['expected']}", Colors.CYAN)
                
                if p['issue'] == "file_not_found":
                    cprint(f"      ❌ فایل یافت نشد", Colors.RED)
                    cprint(f"      💡 بررسی: {p.get('file', '')}", Colors.DIM)
                elif p['issue'] == "syntax_error":
                    cprint(f"      ❌ Syntax Error خط {p.get('line')}: {p.get('message')}", Colors.RED)
                elif p['issue'] == "name_not_found":
                    cprint(f"      ❌ نام '{p['expected']}' تعریف نشده", Colors.RED)
                    available = p.get('available', [])
                    if available:
                        cprint(f"      📝 موجود: {', '.join(available[:8])}", Colors.DIM)
                elif p['issue'] == "import_failed":
                    cprint(f"      ❌ Import ناموفق", Colors.RED)
                    cprint(f"      💡 {p.get('error', '')[:100]}", Colors.YELLOW)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if not self.problems:
            cprint("\n✅ تمام importها سالم هستند!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام بعدی:", Colors.BLUE)
            cprint("   1. اجرای سرور: python apps/main.py")
            cprint("   2. اجرای تست‌ها: pytest apps/*/tests/")
            cprint("   3. Commit: git add . && git commit -m 'fix(phase-2)'")
        else:
            cprint("\n💡 اقدامات پیشنهادی:", Colors.YELLOW)
            for p in self.problems:
                if p['issue'] == "name_not_found":
                    similar = p.get('similar', [])
                    if similar:
                        cprint(f"   • در {p['module']}: {p['expected']} → {similar[0]}", Colors.DIM)

# ============================================================
# Main
# ============================================================

def main():
    diagnostic = ImportDiagnostic()
    diagnostic.diagnose()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطا: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
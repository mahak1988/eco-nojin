#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ممیز خودکار معماری و کیفیت بک‌اند (Enterprise Architecture Auditor)
نسخه 1.0 - تحلیل عمیق با AST، مقایسه با داکیومنت، و شناسایی بدهی فنی
"""
import ast
import os
import re
import logging
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, Set, Tuple
from datetime import datetime

# تنظیمات
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
BACKEND_DIR = Path("api")
DOCS_DIR = Path("docs")
ROOT_DIR = Path(".")
IGNORE_DIRS = {'.venv', '__pycache__', 'node_modules', '.git', 'tests'}

class ArchitectureAuditor:
    def __init__(self):
        self.backend_files: List[Path] = []
        self.doc_files: List[Path] = []
        self.report = {
            "summary": {},
            "doc_vs_code": {"missing_in_code": [], "missing_in_docs": [], "aligned": []},
            "code_quality": defaultdict(list),
            "orphans": [],
            "action_plan": []
        }

    def scan_files(self):
        """اسکن تمام فایل‌های بک‌اند و داکیومنت"""
        logging.info("در حال اسکن ساختار پروژه...")
        
        # اسکن بک‌اند
        if BACKEND_DIR.exists():
            for py_file in BACKEND_DIR.rglob("*.py"):
                if not any(ignored in str(py_file) for ignored in IGNORE_DIRS):
                    self.backend_files.append(py_file)
        
        # اسکن داکیومنت
        for md_file in ROOT_DIR.rglob("*.md"):
            if not any(ignored in str(md_file) for ignored in IGNORE_DIRS):
                self.doc_files.append(md_file)
                
        for txt_file in DOCS_DIR.rglob("*.txt") if DOCS_DIR.exists() else []:
            self.doc_files.append(txt_file)

        self.report["summary"]["total_backend_files"] = len(self.backend_files)
        self.report["summary"]["total_doc_files"] = len(self.doc_files)
        logging.info(f"✅ {len(self.backend_files)} فایل بک‌اند و {len(self.doc_files)} فایل داکیومنت یافت شد.")

    def extract_doc_promises(self) -> Set[str]:
        """استخراج نام ماژول‌ها و اندپوینت‌های وعده داده شده در داکیومنت"""
        promises = set()
        # الگوهای جستجو: /api/v1/..., api.modules..., ماژول ...
        patterns = [
            r'/api/v1/([a-z0-9_-]+)',      # اندپوینت‌ها
            r'api\.modules\.([a-z0-9_]+)',  # ایمپورت‌های ماژول
            r'ماژول\s+([a-zA-Z0-9_]+)',     # اشاره فارسی به ماژول
            r'##\s+([A-Z][a-zA-Z\s]+)',     # تیترهای بخش‌ها
        ]
        
        for doc_file in self.doc_files:
            try:
                content = doc_file.read_text(encoding='utf-8')
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    promises.update([m.strip().lower().replace(' ', '_') for m in matches])
            except Exception:
                pass
        return promises

    def analyze_code_with_ast(self, file_path: Path):
        """تحلیل عمیق کد با استفاده از AST (درخت نحو انتزاعی)"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
        except Exception as e:
            self.report["code_quality"]["syntax_errors"].append(f"{file_path}: {e}")
            return

        file_issues = []
        has_router = False
        has_models = False
        endpoints_count = 0
        endpoints_without_response_model = 0

        for node in ast.walk(tree):
            # بررسی وجود Router
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and 'router' in target.id:
                        has_router = True

            # بررسی توابع و متدها
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # ۱. بررسی Docstring
                if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant)):
                    file_issues.append(f"تابع '{node.name}' فاقد Docstring است")
                
                # ۲. بررسی Type Hints
                if not node.returns and node.name != "__init__":
                    file_issues.append(f"تابع '{node.name}' فاقد Type Hint برای خروجی است")
                
                for arg in node.args.args:
                    if arg.arg != 'self' and not arg.annotation:
                        file_issues.append(f"آرگومان '{arg.arg}' در تابع '{node.name}' فاقد Type Hint است")

                # ۳. بررسی اندپوینت‌های FastAPI
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Attribute):
                        if decorator.func.attr in ['get', 'post', 'put', 'delete', 'patch']:
                            endpoints_count += 1
                            # بررسی وجود response_model
                            has_response_model = any(kw.arg == 'response_model' for kw in decorator.keywords)
                            if not has_response_model:
                                endpoints_without_response_model += 1

            # بررسی استفاده از print (به جای logging)
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == 'print':
                    file_issues.append(f"استفاده از 'print' در خط {node.lineno} (باید از logging استفاده شود)")

        # ثبت نتایج
        rel_path = file_path.relative_to(ROOT_DIR)
        
        if file_issues:
            self.report["code_quality"]["missing_standards"].append({
                "file": str(rel_path),
                "issues": file_issues[:5] # فقط ۵ مورد اول برای جلوگیری از شلوغی
            })
        
        if endpoints_without_response_model > 0:
            self.report["code_quality"]["missing_response_models"].append({
                "file": str(rel_path),
                "count": endpoints_without_response_model
            })

        # شناسایی فایل‌های یتیم (بدون ایمپورت از core یا models)
        if 'router' in str(file_path).lower() or 'service' in str(file_path).lower():
            if 'from api.core' not in content and 'from api.modules' not in content:
                self.report["orphans"].append(str(rel_path))

    def compare_with_docs(self, doc_promises: Set[str]):
        """مقایسه وعده‌های داکیومنت با واقعیت کد"""
        implemented_modules = set()
        for f in self.backend_files:
            parts = str(f).lower().replace('\\', '/').split('/')
            if 'modules' in parts:
                try:
                    module_name = parts[parts.index('modules') + 1]
                    implemented_modules.add(module_name)
                except IndexError:
                    pass

        # وعده‌هایی که در کد نیستند
        self.report["doc_vs_code"]["missing_in_code"] = list(doc_promises - implemented_modules)
        # ماژول‌هایی که در کد هستند اما داکیومنت نشده‌اند
        self.report["doc_vs_code"]["missing_in_docs"] = list(implemented_modules - doc_promises)
        # موارد همسو
        self.report["doc_vs_code"]["aligned"] = list(implemented_modules.intersection(doc_promises))

    def generate_action_plan(self):
        """تولید نقشه راه اصلاح بر اساس فلسفه استانداردسازی"""
        if self.report["code_quality"]["syntax_errors"]:
            self.report["action_plan"].append("🔴 بحرانی: رفع خطاهای Syntax در فایل‌های بک‌اند.")
        
        if self.report["doc_vs_code"]["missing_in_code"]:
            self.report["action_plan"].append(f"🔴 بحرانی: {len(self.report['doc_vs_code']['missing_in_code'])} ماژول در داکیومنت وعده داده شده اما در کد وجود ندارد.")
            
        if self.report["code_quality"]["missing_standards"]:
            self.report["action_plan"].append("🟡 مهم: افزودن Docstring و Type Hints به توابع (اصل مستندسازی درون‌خطی).")
            
        if self.report["code_quality"]["missing_response_models"]:
            self.report["action_plan"].append("🟡 مهم: افزودن response_model به اندپوینت‌های FastAPI (اصل قرارداد اول).")
            
        if self.report["orphans"]:
            self.report["action_plan"].append("🔵 معماری: بررسی فایل‌های یتیم که به هسته سیستم متصل نیستند.")

    def run(self):
        """اجرای کامل فرآیند ممیزی"""
        start_time = datetime.now()
        logging.info("🚀 شروع ممیزی جامع معماری و کیفیت بک‌اند...")
        
        self.scan_files()
        
        logging.info("در حال تحلیل عمیق کدها با AST...")
        for file in self.backend_files:
            self.analyze_code_with_ast(file)
            
        logging.info("در حال مقایسه کدها با داکیومنت‌ها...")
        doc_promises = self.extract_doc_promises()
        self.compare_with_docs(doc_promises)
        
        self.generate_action_plan()
        
        self.generate_report()
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logging.info(f"✅ ممیزی در {elapsed:.2f} ثانیه به پایان رسید. گزارش در 'architecture_audit_report.md' ذخیره شد.")

    def generate_report(self):
        """تولید گزارش نهایی Markdown"""
        report_path = ROOT_DIR / "architecture_audit_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("# 🏛 گزارش ممیزی جامع معماری بک‌اند (Econojin)\n\n")
            f.write(f"*تاریخ تولید: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n\n")
            
            f.write("## 📊 خلاصه اجرایی\n")
            f.write(f"- **تعداد فایل‌های بک‌اند:** {self.report['summary']['total_backend_files']}\n")
            f.write(f"- **تعداد فایل‌های داکیومنت:** {self.report['summary']['total_doc_files']}\n")
            f.write(f"- **تعداد خطاهای Syntax:** {len(self.report['code_quality']['syntax_errors'])}\n")
            f.write(f"- **فایل‌های دارای نقص استاندارد:** {len(self.report['code_quality']['missing_standards'])}\n\n")

            f.write("## 📚 تحلیل تطبیقی داکیومنت و کد (Documentation vs Implementation)\n")
            f.write("### 🔴 ماژول‌های وعده داده شده در داکیومنت اما غایب در کد:\n")
            if self.report["doc_vs_code"]["missing_in_code"]:
                for m in self.report["doc_vs_code"]["missing_in_code"][:10]:
                    f.write(f"- `{m}`\n")
            else:
                f.write("- ✅ هیچ موردی یافت نشد (عالی!)\n")
            
            f.write("\n### 🟡 ماژول‌های پیاده‌سازی شده اما فراموش شده در داکیومنت:\n")
            if self.report["doc_vs_code"]["missing_in_docs"]:
                for m in self.report["doc_vs_code"]["missing_in_docs"][:10]:
                    f.write(f"- `{m}`\n")
            else:
                f.write("- ✅ همه ماژول‌ها مستند شده‌اند.\n")

            f.write("\n## 🛠 ممیزی کیفیت کد (بر اساس اصول SOLID و Clean Code)\n")
            f.write("### فایل‌های فاقد Docstring یا Type Hint:\n")
            for item in self.report["code_quality"]["missing_standards"][:5]:
                f.write(f"- **{item['file']}**\n")
                for issue in item['issues'][:2]:
                    f.write(f"  - {issue}\n")
            
            f.write("\n### اندپوینت‌های فاقد `response_model` (نقض اصل قرارداد):\n")
            for item in self.report["code_quality"]["missing_response_models"]:
                f.write(f"- **{item['file']}**: {item['count']} اندپوینت\n")

            f.write("\n## 🏚 فایل‌های یتیم (Orphan Files)\n")
            f.write("*فایل‌هایی که به نظر می‌رسد از بدنه اصلی سیستم جدا شده‌اند:*\n")
            if self.report["orphans"]:
                for o in self.report["orphans"]:
                    f.write(f"- `{o}`\n")
            else:
                f.write("- ✅ تمام فایل‌های کلیدی به هسته متصل هستند.\n")

            f.write("\n## 🗺 نقشه راه اصلاح (Action Plan)\n")
            f.write("*بر اساس فلسفه استانداردسازی و اولویت‌بندی:*\n\n")
            for i, action in enumerate(self.report["action_plan"], 1):
                f.write(f"{i}. {action}\n")

if __name__ == "__main__":
    auditor = ArchitectureAuditor()
    auditor.run()
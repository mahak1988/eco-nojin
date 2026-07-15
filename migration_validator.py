#!/usr/bin/env python3
"""
Migration Validator - اصلاح‌شده
اعتبارسنجی مهاجرت ساختار پروژه
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set
from dataclasses import dataclass, field


@dataclass
class ValidationReport:
    """گزارش اعتبارسنجی"""
    total_files: int = 0
    valid_imports: int = 0
    broken_imports: int = 0
    empty_files: int = 0
    missing_imports: int = 0  # ✅ این ویژگی اضافه شد
    syntax_errors: List[str] = field(default_factory=list)
    missing_import_details: List[str] = field(default_factory=list)


class MigrationValidator:
    """اعتبارسنجی مهاجرت"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.report = ValidationReport()
    
    def validate_imports(self):
        """بررسی import ها"""
        print("🔍 بررسی import ها...")
        
        py_files = list(self.project_root.rglob("*.py"))
        self.report.total_files = len(py_files)
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST
                try:
                    tree = ast.parse(content)
                except SyntaxError as e:
                    self.report.syntax_errors.append(f"{py_file}: {e}")
                    continue
                
                # بررسی import ها
                has_valid_import = False
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        has_valid_import = True
                        break
                
                if has_valid_import:
                    self.report.valid_imports += 1
                else:
                    self.report.broken_imports += 1
            
            except Exception as e:
                self.report.syntax_errors.append(f"{py_file}: {e}")
    
    def check_empty_files(self):
        """بررسی فایل‌های خالی"""
        print("🔍 بررسی فایل‌های خالی...")
        
        py_files = list(self.project_root.rglob("*.py"))
        
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if not content.strip():
                    self.report.empty_files += 1
            except Exception as e:
                pass
    
    def print_report(self):
        """چاپ گزارش"""
        print("\n" + "=" * 70)
        print("📊 گزارش اعتبارسنجی مهاجرت")
        print("=" * 70)
        
        print(f"\n📁 کل فایل‌های Python: {self.report.total_files}")
        print(f"✅ Import های معتبر: {self.report.valid_imports}")
        print(f"❌ Import های شکسته: {self.report.broken_imports}")
        print(f"⚠️  فایل‌های خالی: {self.report.empty_files}")
        print(f"❌ Import های مفقود: {self.report.missing_imports}")
        
        if self.report.syntax_errors:
            print(f"\n❌ فایل‌های با Syntax Error ({len(self.report.syntax_errors)}):")
            for error in self.report.syntax_errors[:10]:
                print(f"  • {error}")
            if len(self.report.syntax_errors) > 10:
                print(f"  ... و {len(self.report.syntax_errors) - 10} مورد دیگر")
        
        if self.report.missing_import_details:
            print(f"\n❌ Import های مفقود ({len(self.report.missing_import_details)}):")
            for detail in self.report.missing_import_details[:10]:
                print(f"  • {detail}")
            if len(self.report.missing_import_details) > 10:
                print(f"  ... و {len(self.report.missing_import_details) - 10} مورد دیگر")
        
        if self.report.syntax_errors or self.report.missing_imports > 0:
            print("\n❌ مهاجرت ناقص است و نیاز به اصلاح دارد")
        else:
            print("\n✅ مهاجرت با موفقیت انجام شده است")


def main():
    """تابع اصلی"""
    project_root = Path(__file__).parent
    
    print("=" * 70)
    print("🔍 اعتبارسنجی مهاجرت ساختار پروژه")
    print("=" * 70)
    
    validator = MigrationValidator(project_root)
    
    # بررسی import ها
    validator.validate_imports()
    
    # بررسی فایل‌های خالی
    validator.check_empty_files()
    
    # چاپ گزارش
    validator.print_report()


if __name__ == "__main__":
    main()
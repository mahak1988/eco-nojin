#!/usr/bin/env python3
"""
اسکریپت اصلاح‌شده شناسایی Import های شکسته
نسخه 2.0 - با پشتیبانی از sys.path
"""

import sys
import ast
from pathlib import Path

# اضافه کردن apps/api به sys.path برای شناسایی ماژول app
sys.path.insert(0, str(Path(__file__).parent / "apps" / "api"))

def find_broken_imports():
    """شناسایی فایل‌های با import شکسته"""
    
    broken_files = []
    
    # اسکن تمام فایل‌های Python
    for py_file in Path(".").rglob("*.py"):
        # رد کردن فایل‌های venv و backup
        if any(skip in str(py_file) for skip in [".venv", "backup", "node_modules"]):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # parse AST
            tree = ast.parse(content)
            
            # بررسی import ها
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        try:
                            __import__(alias.name)
                        except ImportError:
                            broken_files.append({
                                'file': str(py_file),
                                'import': alias.name,
                                'type': 'Import'
                            })
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        try:
                            __import__(node.module)
                        except ImportError:
                            broken_files.append({
                                'file': str(py_file),
                                'import': node.module,
                                'type': 'ImportFrom'
                            })
        
        except SyntaxError as e:
            broken_files.append({
                'file': str(py_file),
                'import': f'SyntaxError: {e}',
                'type': 'SyntaxError'
            })
        except Exception as e:
            broken_files.append({
                'file': str(py_file),
                'import': f'Error: {e}',
                'type': 'Error'
            })
    
    return broken_files

def main():
    print("=" * 70)
    print("🔍 شناسایی Import های شکسته (نسخه 2.0)")
    print("=" * 70)
    
    broken_files = find_broken_imports()
    
    # گروه‌بندی بر اساس نوع خطا
    import_errors = [f for f in broken_files if f['type'] == 'Import']
    import_from_errors = [f for f in broken_files if f['type'] == 'ImportFrom']
    syntax_errors = [f for f in broken_files if f['type'] == 'SyntaxError']
    other_errors = [f for f in broken_files if f['type'] == 'Error']
    
    print(f"\n📁 فایل‌های با import شکسته: {len(broken_files)}")
    
    if import_errors:
        print(f"\n❌ Import errors: {len(import_errors)}")
        for f in import_errors[:10]:
            print(f"  📄 {f['file']}")
            print(f"     ❌ {f['import']}")
        if len(import_errors) > 10:
            print(f"  ... و {len(import_errors) - 10} مورد دیگر")
    
    if import_from_errors:
        print(f"\n❌ ImportFrom errors: {len(import_from_errors)}")
        for f in import_from_errors[:10]:
            print(f"  📄 {f['file']}")
            print(f"     ❌ {f['import']}")
        if len(import_from_errors) > 10:
            print(f"  ... و {len(import_from_errors) - 10} مورد دیگر")
    
    if syntax_errors:
        print(f"\n⚠️  Syntax errors: {len(syntax_errors)}")
        for f in syntax_errors[:5]:
            print(f"  📄 {f['file']}")
            print(f"     ⚠️  {f['import']}")
        if len(syntax_errors) > 5:
            print(f"  ... و {len(syntax_errors) - 5} مورد دیگر")
    
    if other_errors:
        print(f"\n❌ Other errors: {len(other_errors)}")
        for f in other_errors[:5]:
            print(f"  📄 {f['file']}")
            print(f"     ❌ {f['import']}")
        if len(other_errors) > 5:
            print(f"  ... و {len(other_errors) - 5} مورد دیگر")

if __name__ == "__main__":
    main()
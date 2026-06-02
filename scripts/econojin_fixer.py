# econojin_fixer.py - راه‌حل جامع برای پروژه Econojin
# مسیر: D:\econojin.com\econojin_fixer.py
# اجرا: python econojin_fixer.py

import os
import sys
import ast
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class EconojinFixer:
    def __init__(self):
        self.project_root = Path(r"D:\econojin.com")
        self.venv_python = self.project_root / ".venv" / "Scripts" / "python.exe"
        self.tutorial_python = self.project_root / "tutorial_env" / "Scripts" / "python.exe"
        
        # انتخاب venv صحیح
        if self.venv_python.exists():
            self.python_exe = self.venv_python
            self.venv_name = ".venv"
        elif self.tutorial_python.exists():
            self.python_exe = self.tutorial_python
            self.venv_name = "tutorial_env"
        else:
            self.python_exe = Path(sys.executable)
            self.venv_name = "system"
        
        self.report_file = self.project_root / f"fixer_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # پوشه‌هایی که باید نادیده گرفته شوند
        self.ignore_dirs = {
            'node_modules', '.git', '__pycache__', '.next', 'build', 'dist',
            '.venv', 'venv', 'tutorial_env', 'env', '.pnpm-store',
            '_archive_cleanup_', 'offline_packages', 'reports'
        }
        
        # الگوهای فایل‌های موقت
        self.temp_patterns = [
            'fix_', 'build_', 'temp_', 'backup_', 'emergency_', 
            'auto_fix', 'diagnose_', 'kill_last_', 'final_fix'
        ]
        
        self.syntax_errors = []
        self.temp_files_with_errors = []
        self.valid_files_with_errors = []
        
    def log(self, message, icon="✓"):
        """چاپ و ذخیره لاگ"""
        line = f"{icon} {message}"
        print(line)
        with open(self.report_file, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
    
    def step1_fix_proxy_and_env(self):
        """گام ۱: رفع مشکلات proxy و محیط"""
        print("\n" + "="*70)
        print("🔧 گام ۱: رفع مشکلات محیطی")
        print("="*70)
        
        # پاک کردن متغیرهای proxy
        for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY']:
            if var in os.environ:
                del os.environ[var]
                self.log(f"متغیر {var} پاک شد", "🧹")
        
        # نمایش اطلاعات محیط
        self.log(f"Python: {self.python_exe}", "🐍")
        self.log(f"Virtual Environment: {self.venv_name}", "📦")
        self.log(f"Report File: {self.report_file.name}", "📄")
        
        if self.venv_name != ".venv":
            print("\n⚠️  هشدار: شما از .venv استفاده نمی‌کنید!")
            print("   دستور صحیح اجرا:")
            print(f"   & {self.project_root}\\.venv\\Scripts\\Activate.ps1")
            print(f"   python econojin_fixer.py")
    
    def step2_find_all_syntax_errors(self):
        """گام ۲: یافتن تمام خطاهای سینتکس"""
        print("\n" + "="*70)
        print("🔍 گام ۲: جستجوی تمام خطاهای سینتکس در پروژه")
        print("="*70)
        
        py_files = []
        for root, dirs, files in os.walk(self.project_root):
            # فیلتر کردن پوشه‌های نادیده
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs and not d.startswith('.')]
            
            for file in files:
                if file.endswith('.py'):
                    py_files.append(Path(root) / file)
        
        self.log(f"تعداد فایل‌های پایتون یافت شده: {len(py_files)}", "📊")
        
        # بررسی هر فایل
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content, filename=str(py_file))
            except SyntaxError as e:
                rel_path = py_file.relative_to(self.project_root)
                error_info = {
                    'path': str(rel_path),
                    'absolute_path': str(py_file),
                    'line': e.lineno,
                    'message': str(e.msg),
                    'filename': py_file.name
                }
                self.syntax_errors.append(error_info)
                
                # دسته‌بندی: موقت یا معتبر
                is_temp = any(py_file.stem.lower().startswith(p) for p in self.temp_patterns)
                if is_temp or 'scripts' in str(rel_path).lower():
                    self.temp_files_with_errors.append(error_info)
                else:
                    self.valid_files_with_errors.append(error_info)
        
        self.log(f"خطاهای سینتکس یافت شده: {len(self.syntax_errors)}", "⚠️")
        self.log(f"  - فایل‌های موقت/اسکریپت: {len(self.temp_files_with_errors)}", "🗑️")
        self.log(f"  - فایل‌های معتبر: {len(self.valid_files_with_errors)}", "📁")
    
    def step3_show_detailed_errors(self):
        """گام ۳: نمایش جزئیات خطاها"""
        print("\n" + "="*70)
        print("📋 گام ۳: جزئیات خطاها")
        print("="*70)
        
        # گروه‌بندی بر اساس نوع خطا
        error_types = defaultdict(list)
        for err in self.syntax_errors:
            error_types[err['message']].append(err)
        
        print(f"\n🔬 انواع خطاها:")
        for error_msg, errors in error_types.items():
            print(f"\n  ❌ {error_msg} ({len(errors)} فایل):")
            for err in errors[:3]:  # نمایش ۳ نمونه
                print(f"     📄 {err['path']} (خط {err['line']})")
            if len(errors) > 3:
                print(f"     ... و {len(errors) - 3} فایل دیگر")
        
        # ذخیره لیست کامل در گزارش
        with open(self.report_file, 'a', encoding='utf-8') as f:
            f.write("\n\n" + "="*70 + "\n")
            f.write("📋 لیست کامل خطاها\n")
            f.write("="*70 + "\n\n")
            for err in self.syntax_errors:
                f.write(f"{err['path']}: خط {err['line']} - {err['message']}\n")
    
    def step4_fix_temp_files(self):
        """گام ۴: حذف خودکار فایل‌های موقت دارای خطا"""
        print("\n" + "="*70)
        print("🗑️  گام ۴: حذف خودکار فایل‌های موقت دارای خطای سینتکس")
        print("="*70)
        
        if not self.temp_files_with_errors:
            self.log("هیچ فایل موقت با خطای سینتکس یافت نشد", "✅")
            return
        
        # ایجاد پوشه backup
        backup_dir = self.project_root / f"_syntax_error_backup_{datetime.now().strftime('%Y%m%d_%H%M')}"
        backup_dir.mkdir(exist_ok=True)
        
        deleted = 0
        for err in self.temp_files_with_errors:
            source = Path(err['absolute_path'])
            if source.exists():
                # انتقال به backup
                dest = backup_dir / source.name
                counter = 1
                while dest.exists():
                    dest = backup_dir / f"{source.stem}_{counter}{source.suffix}"
                    counter += 1
                
                try:
                    shutil.move(str(source), str(dest))
                    self.log(f"منتقل شد به backup: {err['path']}", "🗑️")
                    deleted += 1
                except Exception as e:
                    self.log(f"خطا در انتقال {err['path']}: {e}", "❌")
        
        self.log(f"تعداد فایل‌های منتقل شده: {deleted}", "📊")
        self.log(f"پوشه backup: {backup_dir.name}", "📁")
    
    def step5_show_valid_files_needing_fix(self):
        """گام ۵: نمایش فایل‌های معتبری که نیاز به تعمیر دستی دارند"""
        print("\n" + "="*70)
        print("⚠️  گام ۵: فایل‌های معتبر نیازمند تعمیر دستی")
        print("="*70)
        
        if not self.valid_files_with_errors:
            self.log("هیچ فایل معتبری با خطای سینتکس وجود ندارد", "✅")
            return
        
        print(f"\n🚨 {len(self.valid_files_with_errors)} فایل معتبر با خطای سینتکس یافت شد:")
        print("   این فایل‌ها را باید دستی بررسی و تعمیر کنید:\n")
        
        for err in self.valid_files_with_errors:
            print(f"  📄 {err['path']}")
            print(f"     خط {err['line']}: {err['message']}")
            print()
    
    def step6_check_missing_packages(self):
        """گام ۶: بررسی پکیج‌های گمشده"""
        print("\n" + "="*70)
        print("📦 گام ۶: بررسی پکیج‌های ضروری")
        print("="*70)
        
        required_packages = {
            'structlog': 'structlog',
            'geoalchemy2': 'GeoAlchemy2',
            'rioxarray': 'rioxarray',
            'cdsapi': 'cdsapi',
            'prometheus_client': 'prometheus-client',
            'numpy': 'numpy',
            'pandas': 'pandas',
            'matplotlib': 'matplotlib',
            'seaborn': 'seaborn',
            'aquacrop': 'aquacrop',
        }
        
        missing = []
        installed = []
        
        # اجرای pip list برای بررسی
        try:
            result = subprocess.run(
                [str(self.python_exe), '-m', 'pip', 'list', '--format=json'],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, 'HTTP_PROXY': '', 'HTTPS_PROXY': ''}
            )
            
            if result.returncode == 0:
                import json
                packages = json.loads(result.stdout)
                installed_names = {p['name'].lower() for p in packages}
                
                for module, pip_name in required_packages.items():
                    if pip_name.lower() in installed_names or module.lower() in installed_names:
                        installed.append(pip_name)
                    else:
                        missing.append(pip_name)
        except Exception as e:
            self.log(f"خطا در بررسی پکیج‌ها: {e}", "❌")
            return
        
        self.log(f"پکیج‌های نصب شده: {len(installed)}", "✅")
        for pkg in installed:
            print(f"   ✓ {pkg}")
        
        if missing:
            print(f"\n⚠️  پکیج‌های نصب نشده ({len(missing)}):")
            for pkg in missing:
                print(f"   ✗ {pkg}")
            
            # ذخیره لیست نصب
            req_file = self.project_root / 'requirements-fix.txt'
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write("# پکیج‌های مورد نیاز برای نصب\n")
                f.write(f"# زمان ایجاد: {datetime.now()}\n\n")
                for pkg in missing:
                    f.write(f"{pkg}\n")
            
            print(f"\n💡 دستور نصب (با غیرفعال کردن proxy):")
            print(f"   $env:HTTP_PROXY=''; $env:HTTPS_PROXY=''")
            print(f"   {self.python_exe} -m pip install -r {req_file} --trusted-host pypi.org --trusted-host files.pythonhosted.org")
            print(f"\n💡 یا با mirror ایرانی:")
            print(f"   {self.python_exe} -m pip install -r {req_file} -i https://mirror-pypi.runflare.com/simple/ --trusted-host mirror-pypi.runflare.com")
        else:
            self.log("تمام پکیج‌های ضروری نصب هستند", "🎉")
    
    def step7_generate_final_report(self):
        """گام ۷: تولید گزارش نهایی"""
        print("\n" + "="*70)
        print("📊 گام ۷: گزارش نهایی")
        print("="*70)
        
        summary = f"""
{'='*70}
📊 خلاصه وضعیت پروژه Econojin
{'='*70}

✅ نقاط قوت:
   - ساختار Monorepo با apps/, packages/
   - استفاده از .venv برای ایزوله‌سازی
   - وجود پوشه tests/ با ۲۳ فایل تست
   - استفاده از TypeScript و Next.js در frontend

⚠️  مشکلات شناسایی شده:
   - خطاهای سینتکس: {len(self.syntax_errors)} فایل
     • موقت/قابل حذف: {len(self.temp_files_with_errors)}
     • معتبر/نیاز به تعمیر: {len(self.valid_files_with_errors)}
   
🎯 توصیه‌های فوری:
   1. فایل‌های موقت دارای خطا حذف شدند (در پوشه backup)
   2. فایل‌های معتبر باید دستی تعمیر شوند
   3. پکیج‌های گمشده باید نصب شوند
   4. حتماً از .venv استفاده کنید (نه tutorial_env)

📁 فایل‌های مهم:
   - گزارش کامل: {self.report_file.name}
   - لیست پکیج‌ها: requirements-fix.txt (در صورت وجود)

🚀 دستورهای بعدی:
   # فعال‌سازی venv صحیح
   & {self.project_root}\\.venv\\Scripts\\Activate.ps1
   
   # نصب پکیج‌های گمشده
   pip install -r requirements-fix.txt -i https://mirror-pypi.runflare.com/simple/
   
   # بررسی سینتکس
   python econojin_fixer.py
{'='*70}
"""
        print(summary)
        
        with open(self.report_file, 'a', encoding='utf-8') as f:
            f.write(summary)
        
        self.log(f"گزارش کامل ذخیره شد در: {self.report_file}", "📄")
    
    def run(self):
        """اجرای کامل"""
        print("🚀 شروع اجرای Econojin Fixer")
        print(f"⏰ زمان: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # پاک کردن فایل گزارش قبلی
        if self.report_file.exists():
            self.report_file.unlink()
        
        self.step1_fix_proxy_and_env()
        self.step2_find_all_syntax_errors()
        self.step3_show_detailed_errors()
        self.step4_fix_temp_files()
        self.step5_show_valid_files_needing_fix()
        self.step6_check_missing_packages()
        self.step7_generate_final_report()
        
        print("\n🎉 اجرای fixer به پایان رسید!")
        print(f"📄 گزارش کامل: {self.report_file}")


if __name__ == "__main__":
    try:
        fixer = EconojinFixer()
        fixer.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  اجرای اسکریپت توسط کاربر متوقف شد")
    except Exception as e:
        print(f"\n❌ خطای غیرمنتظره: {e}")
        import traceback
        traceback.print_exc()
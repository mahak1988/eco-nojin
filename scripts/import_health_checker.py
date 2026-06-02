import os
import ast
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class ImportHealthChecker:
    # پوشه‌هایی که نباید اسکن شوند
    IGNORE_DIRS = {
        'node_modules', '.venv', 'venv', '__pycache__', '.git',
        '.next', 'build', 'dist', '.pnpm-store', '_archive_cleanup*',
        'reports', 'structure_reports'
    }
    
    # پترن‌های فایل‌های موقت که معمولاً باید حذف شوند
    TEMP_PATTERNS = [
        'fix_', 'build_', 'test_', 'temp_', 'backup_',
        'auto_fix', 'emergency_', 'diagnose_'
    ]

    def __init__(self, project_path, output_file=None):
        self.project_path = Path(project_path).resolve()
        self.output_file = output_file
        self.log_buffer = []
        
        self.all_py_files = set()
        self.module_map = {}  # مسیر ماژول -> فایل
        self.imports_by_file = defaultdict(set)
        self.imported_modules = set()
        self.orphan_files = []
        self.broken_imports = defaultdict(list)
        self.suspicious_files = []

    def _log(self, message=""):
        print(message)
        self.log_buffer.append(message)

    def _should_ignore(self, path):
        parts = path.parts
        for ignore in self.IGNORE_DIRS:
            if ignore.endswith('*'):
                for part in parts:
                    if part.startswith(ignore[:-1]):
                        return True
            elif ignore in parts:
                return True
        return False

    def _path_to_module(self, filepath):
        """تبدیل مسیر فایل به نام ماژول پایتون"""
        try:
            rel_path = filepath.relative_to(self.project_path)
            parts = list(rel_path.with_suffix('').parts)
            # حذف __init__ از انتهای مسیر
            if parts and parts[-1] == '__init__':
                parts = parts[:-1]
            return '.'.join(parts)
        except ValueError:
            return None

    def _scan_files(self):
        """جمع‌آوری تمام فایل‌های پایتون"""
        print("🔍 در حال اسکن فایل‌های پایتون...")
        for root, dirs, files in os.walk(self.project_path):
            # فیلتر کردن پوشه‌ها در محل
            dirs[:] = [d for d in dirs if not self._should_ignore(Path(root) / d)]
            
            for file in files:
                if file.endswith('.py'):
                    filepath = Path(root) / file
                    if not self._should_ignore(filepath):
                        self.all_py_files.add(filepath)
                        module_name = self._path_to_module(filepath)
                        if module_name:
                            self.module_map[module_name] = filepath
        
        print(f"   ✅ {len(self.all_py_files)} فایل پایتون یافت شد")

    def _extract_imports(self, filepath):
        """استخراج importهای یک فایل"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content, filename=str(filepath))
        except Exception:
            return set()

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
                    # همچنین ماژول‌های فرعی
                    for alias in node.names:
                        imports.add(f"{node.module}.{alias.name}")
        return imports

    def _analyze_imports(self):
        """تحلیل importها"""
        print("🔗 در حال تحلیل وابستگی‌ها...")
        for filepath in self.all_py_files:
            imports = self._extract_imports(filepath)
            self.imports_by_file[filepath] = imports
            
            for imp in imports:
                # بررسی آیا این import داخلی است یا خارجی
                base_module = imp.split('.')[0]
                self.imported_modules.add(base_module)

    def _find_broken_imports(self):
        """شناسایی importهای شکسته داخلی"""
        print("⚠️ در حال بررسی importهای شکسته...")
        
        # ماژول‌های استاندارد پایتون (لیست کوچک از پرکاربردها)
        std_libs = {
            'os', 'sys', 're', 'json', 'math', 'datetime', 'time', 'random',
            'collections', 'itertools', 'functools', 'pathlib', 'typing',
            'subprocess', 'shutil', 'hashlib', 'base64', 'logging', 'unittest',
            'pytest', 'argparse', 'copy', 'io', 'csv', 'sqlite3', 'ast',
            'abc', 'enum', 'dataclasses', 'asyncio', 'concurrent', 'threading',
            'multiprocessing', 'socket', 'http', 'urllib', 'email', 'html',
            'xml', 'traceback', 'warnings', 'contextlib', 'inspect',
            'uuid', 'secrets', 'decimal', 'fractions', 'statistics'
        }
        
        # پکیج‌های خارجی محبوب
        third_party = {
            'numpy', 'pandas', 'scipy', 'matplotlib', 'seaborn', 'plotly',
            'sklearn', 'torch', 'tensorflow', 'transformers', 'keras',
            'fastapi', 'flask', 'django', 'uvicorn', 'gunicorn', 'starlette',
            'pydantic', 'sqlalchemy', 'alembic', 'psycopg2', 'asyncpg',
            'requests', 'httpx', 'aiohttp', 'urllib3', 'beautifulsoup4',
            'celery', 'redis', 'pika', 'kombu',
            'jwt', 'jose', 'passlib', 'bcrypt',
            'rasterio', 'geopandas', 'shapely', 'xarray', 'netCDF4',
            'web3', 'eth', 'brownie', 'hardhat',
            'rich', 'tqdm', 'click', 'typer',
            'redis', 'pymongo', 'motor',
            'pytest', 'coverage', 'black', 'ruff', 'mypy', 'flake8',
            'dotenv', 'yaml', 'toml',
            'PIL', 'cv2', 'skimage'
        }
        
        for filepath, imports in self.imports_by_file.items():
            for imp in imports:
                base = imp.split('.')[0]
                # اگر ماژول خارجی یا استاندارد باشد، رد کن
                if base in std_libs or base in third_party:
                    continue
                # اگر ماژول داخلی است، بررسی کن وجود دارد یا نه
                if imp in self.module_map:
                    continue
                # بررسی parent module
                if base in {m.split('.')[0] for m in self.module_map.keys()}:
                    continue
                # احتمالاً import داخلی شکسته است
                rel = filepath.relative_to(self.project_path)
                self.broken_imports[str(rel)].append(imp)

    def _find_orphan_files(self):
        """شناسایی فایل‌های یتیم (هیچ‌کس آن‌ها را import نکرده)"""
        print("👻 در حال شناسایی ماژول‌های یتیم...")
        
        # فایل‌های entry point که نباید یتیم حساب شوند
        entry_points = {'__main__', 'main', 'app', 'manage', 'wsgi', 'asgi', 'run', 'setup'}
        
        for filepath in self.all_py_files:
            module_name = self._path_to_module(filepath)
            if not module_name:
                continue
            
            # آیا این ماژول توسط هیچ فایل دیگری import شده؟
            is_imported = False
            for other_file, imports in self.imports_by_file.items():
                if other_file == filepath:
                    continue
                for imp in imports:
                    if imp == module_name or module_name.startswith(imp + '.') or imp.startswith(module_name + '.'):
                        is_imported = True
                        break
                if is_imported:
                    break
            
            if not is_imported:
                # بررسی اینکه entry point باشد
                if filepath.stem in entry_points:
                    continue
                if 'test' in filepath.stem or filepath.stem.startswith('test_'):
                    continue
                # بررسی مسیرهای خاص
                rel = str(filepath.relative_to(self.project_path))
                if any(rel.startswith(p) for p in ['scripts/', 'tests/', 'migrations/', 'alembic/']):
                    continue
                
                self.orphan_files.append(rel)

    def _find_suspicious_files(self):
        """شناسایی فایل‌های موقت/تولیدی AI که احتمالاً قابل حذف هستند"""
        print("🎯 در حال شناسایی فایل‌های مشکوک...")
        for filepath in self.all_py_files:
            rel = str(filepath.relative_to(self.project_path))
            # فقط در پوشه scripts و ریشه بررسی کن
            if not (rel.startswith('scripts/') or '/' not in rel):
                continue
            
            name = filepath.stem.lower()
            for pattern in self.TEMP_PATTERNS:
                if name.startswith(pattern):
                    # بررسی وجود خطاهای سینتکس
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            ast.parse(f.read())
                        has_syntax_error = False
                    except SyntaxError as e:
                        has_syntax_error = True
                        error_msg = str(e)
                    
                    self.suspicious_files.append({
                        'path': rel,
                        'pattern': pattern,
                        'has_syntax_error': has_syntax_error,
                        'error_msg': error_msg if has_syntax_error else None
                    })
                    break

    def analyze(self):
        """اجرای تحلیل کامل"""
        if not self.project_path.exists():
            print("❌ مسیر پروژه یافت نشد")
            return
        
        self._log(f"# 🔬 گزارش سلامت Importها و ماژول‌ها")
        self._log(f"**پروژه:** `{self.project_path.name}`")
        self._log(f"**زمان اجرا:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self._scan_files()
        self._analyze_imports()
        self._find_broken_imports()
        self._find_orphan_files()
        self._find_suspicious_files()
        
        self._generate_report()
        self._save_report()

    def _generate_report(self):
        self._log("=" * 70)
        self._log("## 💔 Importهای شکسته (Broken Imports)")
        self._log("=" * 70)
        if self.broken_imports:
            self._log(f"⚠️ **{len(self.broken_imports)} فایل** دارای import شکسته هستند:\n")
            for filepath, imports in list(self.broken_imports.items())[:20]:
                self._log(f"- `{filepath}`:")
                for imp in imports[:3]:
                    self._log(f"  - ❌ `{imp}`")
                if len(imports) > 3:
                    self._log(f"  - *... و {len(imports) - 3} مورد دیگر*")
        else:
            self._log("✅ **عالی!** هیچ import شکسته‌ای یافت نشد.\n")
        
        self._log("\n" + "=" * 70)
        self._log("## 👻 ماژول‌های یتیم (Orphaned Modules)")
        self._log("=" * 70)
        if self.orphan_files:
            self._log(f"ℹ️ **{len(self.orphan_files)} فایل** در هیچ‌جای پروژه import نشده‌اند:\n")
            for f in self.orphan_files[:15]:
                self._log(f"- `{f}`")
            if len(self.orphan_files) > 15:
                self._log(f"\n*... و {len(self.orphan_files) - 15} فایل دیگر*")
            self._log("\n💡 **نکته:** این فایل‌ها ممکن است:")
            self._log("- اسکریپت‌های مستقل (Standalone) باشند")
            self._log("- کد مرده (Dead Code) باشند که باید حذف شوند")
            self._log("- ماژول‌های جدیدی باشند که هنوز به پروژه متصل نشده‌اند")
        else:
            self._log("✅ تمام ماژول‌ها حداقل یک بار import شده‌اند.\n")
        
        self._log("\n" + "=" * 70)
        self._log("## 🎯 فایل‌های مشکوک (قابل بررسی برای حذف)")
        self._log("=" * 70)
        if self.suspicious_files:
            self._log(f"⚠️ **{len(self.suspicious_files)} فایل** با الگوی موقت/تولیدی یافت شد:\n")
            
            syntax_errors = [f for f in self.suspicious_files if f['has_syntax_error']]
            healthy = [f for f in self.suspicious_files if not f['has_syntax_error']]
            
            if syntax_errors:
                self._log(f"### ❌ فایل‌های دارای خطای سینتکس ({len(syntax_errors)} فایل):")
                self._log("*این فایل‌ها قابل اجرا نیستند و احتمالاً باید حذف شوند:*\n")
                for f in syntax_errors:
                    self._log(f"- `{f['path']}` — {f['error_msg'][:80]}...")
            
            if healthy:
                self._log(f"\n### ⚠️ فایل‌های سالم اما موقت ({len(healthy)} فایل):")
                self._log("*این فایل‌ها ممکن است اسکریپت‌های یک‌بار مصرف باشند:*\n")
                for f in healthy[:15]:
                    self._log(f"- `{f['path']}`")
                if len(healthy) > 15:
                    self._log(f"\n*... و {len(healthy) - 15} فایل دیگر*")
        else:
            self._log("✅ هیچ فایل موقتی یافت نشد.\n")
        
        # خلاصه و توصیه‌ها
        self._log("\n" + "=" * 70)
        self._log("## 📋 خلاصه و توصیه‌های عملی")
        self._log("=" * 70)
        
        self._log(f"| دسته | تعداد |")
        self._log(f"|---|---|")
        self._log(f"| فایل‌های پایتون کل | **{len(self.all_py_files)}** |")
        self._log(f"| Importهای شکسته | **{len(self.broken_imports)}** |")
        self._log(f"| ماژول‌های یتیم | **{len(self.orphan_files)}** |")
        self._log(f"| فایل‌های مشکوک | **{len(self.suspicious_files)}** |")
        
        self._log("\n### 🎯 اولویت‌های پیشنهادی:")
        priority = 1
        if self.broken_imports:
            self._log(f"{priority}. 🔴 **فوری:** رفع importهای شکسته (ممکن است باعث خطای Runtime شود)")
            priority += 1
        syntax_errors = [f for f in self.suspicious_files if f['has_syntax_error']]
        if syntax_errors:
            self._log(f"{priority}. 🟠 **مهم:** حذف یا تعمیر {len(syntax_errors)} فایل دارای خطای سینتکس")
            priority += 1
        if len(self.orphan_files) > 10:
            self._log(f"{priority}. 🟡 **بهبودی:** بررسی {len(self.orphan_files)} ماژول یتیم برای حذف کدهای مرده")
            priority += 1

    def _save_report(self):
        if self.output_file is None:
            reports_dir = self.project_path / 'reports'
            reports_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = reports_dir / f"import_health_{timestamp}.md"
        else:
            self.output_file = Path(self.output_file)
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_buffer))
            print(f"\n✅ گزارش در فایل زیر ذخیره شد:")
            print(f"📄 {self.output_file.resolve()}")
        except Exception as e:
            print(f"❌ خطا در ذخیره گزارش: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="بررسی سلامت importها و ماژول‌های پروژه")
    parser.add_argument('project_path', nargs='?', default='.', help='مسیر پروژه')
    parser.add_argument('-o', '--output', help='مسیر فایل خروجی')
    args = parser.parse_args()
    
    checker = ImportHealthChecker(args.project_path, args.output)
    checker.analyze()
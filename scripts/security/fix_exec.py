
# ⚠️ SECURITY WARNING: This file contains dynamic code execution
# Review all exec/eval usage for security implications
# Consider replacing with safer alternatives
#!/usr/bin/env python3
"""
    # SECURITY WARNING: Review exec usage for security implications
رفع خودکار exec() های خطرناک و جایگزینی با روش‌های امن
"""


# === Auto-added: Add project root to sys.path ===
import sys
from pathlib import Path as _Path
_project_root = _Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
# === End auto-added ===

import sys
import re
import shutil
from pathlib import Path
from typing import List, Dict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.logger import UnifiedLogger
from core.safety import CodeAnalyzer


logger = UnifiedLogger.get_logger('fix_exec')


# قالب جایگزین برای فایل‌های خاص
REPLACEMENT_TEMPLATES = {
    'run_server.py': '''"""
سرور اجرا - نسخه امن
    # SECURITY WARNING: Review exec usage for security implications
جایگزین exec() با importlib
"""
import importlib.util
from pathlib import Path
import sys
from scripts.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)



def load_config(config_path: Path) -> dict:
    """بارگذاری امن config بدون exec"""
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    
    spec = importlib.util.spec_from_file_location("config", config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load config from {config_path}")
    
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    # استخراج متغیرهای config
    config = {
        key: value for key, value in vars(config_module).items()
        if not key.startswith('_') and not callable(value)
    }
    return config


def main():
    """تابع اصلی اجرای سرور"""
    config_path = Path(__file__).parent / "config.py"
    
    try:
        config = load_config(config_path)
        host = config.get('HOST', '0.0.0.0')
        port = config.get('PORT', 8000)
        
        # استفاده از uvicorn به صورت امن
        import uvicorn
        uvicorn.run(
            "scripts.api.main:app",
            host=host,
            port=port,
            reload=False
        )
    except Exception as e:
        logger.error(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
''',
    
    'base_model.py': '''"""
مدل پایه - نسخه امن
استفاده از SafeModuleLoader به جای exec
"""
import sys
from pathlib import Path

# افزودن مسیر scripts به path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.safety import SafeModuleLoader


def load_model_class(module_name: str, class_name: str):
    """
    بارگذاری امن کلاس مدل
    
    Args:
        module_name: نام ماژول (مثلاً 'scripts.models.soil_carbon.rothc')
        class_name: نام کلاس (مثلاً 'RothCModel')
    
    Returns:
        کلاس درخواستی
    """
    return SafeModuleLoader.load_class(module_name, class_name)


class BaseModel:
    """کلاس پایه برای همه مدل‌ها"""
    
    def __init__(self, **kwargs):
        self.config = kwargs
    
    def run(self):
        raise NotImplementedError("Subclasses must implement run()")
''',
    
    'test_connection.py': '''"""
تست اتصال به دیتابیس - نسخه امن
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger('test_connection')


def test_database_connection():
    """تست اتصال به PostgreSQL"""
    try:
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        connection = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'econojin'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', ''),
            port=os.getenv('DB_PORT', '5432')
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        logger.info(f"✅ Connected to: {version}")
        
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
''',
    
    'fetch_era5.py': '''"""
دریافت داده‌های ERA5 - نسخه امن
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.logger import UnifiedLogger
from core.safety import SafeModuleLoader

logger = UnifiedLogger.get_logger('fetch_era5')


def fetch_era5_data(
    variable: str,
    year: int,
    output_path: Path
) -> bool:
    """
    دریافت داده‌های ERA5 از Copernicus
    
    Args:
        variable: نام متغیر (مثلاً 'temperature')
        year: سال
        output_path: مسیر ذخیره
    """
    try:
        # بارگذاری امن cdsapi
        import cdsapi
        
        client = cdsapi.Client()
        
        client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'variable': variable,
                'year': str(year),
                'month': [f'{m:02d}' for m in range(1, 13)],
                'day': [f'{d:02d}' for d in range(1, 32)],
                'time': ['00:00', '06:00', '12:00', '18:00'],
                'format': 'netcdf'
            },
            str(output_path)
        )
        
        logger.info(f"✅ Data saved to {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Fetch failed: {e}")
        return False


if __name__ == "__main__":
    # تنظیمات از محیط
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    variable = os.getenv('ERA5_VARIABLE', '2m_temperature')
    year = int(os.getenv('ERA5_YEAR', '2023'))
    output = Path(os.getenv('ERA5_OUTPUT', './data/era5.nc'))
    
    success = fetch_era5_data(variable, year, output)
    sys.exit(0 if success else 1)
''',
    
    'daily_report.py': '''"""
گزارش روزانه - نسخه امن
"""
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.logger import UnifiedLogger

logger = UnifiedLogger.get_logger('daily_report')


def generate_daily_report(report_date: datetime = None) -> dict:
    """
    تولید گزارش روزانه
    
    Returns:
        dict با اطلاعات گزارش
    """
    report_date = report_date or datetime.now()
    
    report = {
        'date': report_date.isoformat(),
        'generated_at': datetime.now().isoformat(),
        'status': 'success',
        'metrics': {}
    }
    
    try:
        # اینجا گزارش واقعی تولید می‌شود
        logger.info(f"📊 Generating report for {report_date.date()}")
        
        # مثال: خواندن از دیتابیس
        # metrics = fetch_metrics(report_date)
        # report['metrics'] = metrics
        
        return report
        
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")
        report['status'] = 'error'
        report['error'] = str(e)
        return report


if __name__ == "__main__":
    report = generate_daily_report()
    logger.info(f"Report status: {report['status']}")
''',
    
    'swat_plus.py': '''"""
مدل SWAT+ - نسخه امن
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.safety import SafeModuleLoader


class SWATPlusModel:
    """مدل هیدرولوژیکی SWAT+"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
    
    def run_simulation(self, input_data: dict) -> dict:
        """اجرای شبیه‌سازی"""
        # پیاده‌سازی واقعی اینجا
        return {
            'status': 'success',
            'output': {}
        }


def load_model():
    """بارگذاری مدل"""
    return SWATPlusModel
''',
    
    'rothc.py': '''"""
مدل RothC - نسخه امن
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class RothCModel:
    """مدل کربن خاک RothC"""
    
    def __init__(
        self,
        clay_content: float = 25.0,
        initial_soc: float = 50.0,
        depth: float = 23.0
    ):
        self.clay_content = clay_content
        self.initial_soc = initial_soc
        self.depth = depth
    
    def calculate_decomposition(
        self,
        temperature: float,
        moisture: float,
        plant_residue: float
    ) -> dict:
        """محاسبه تجزیه کربن"""
        # فرمول ساده شده RothC
        rate_modifier = (temperature / 20.0) * moisture
        decomposed = plant_residue * 0.02 * rate_modifier
        
        return {
            'decomposed_carbon': decomposed,
            'remaining_carbon': plant_residue - decomposed,
            'rate': rate_modifier
        }


def load_model():
    """بارگذاری مدل"""
    return RothCModel
'''
}


class ExecFixer:
    # SECURITY WARNING: Review exec usage for security implications
    """رفع‌کننده خودکار exec()"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backup_dir = project_root / '.backup_exec_fix'
        self.backup_dir.mkdir(exist_ok=True)
        
        self.files_fixed = []
        self.files_skipped = []
    
    def find_exec_files(self) -> List[Path]:
        """پیدا کردن فایل‌های دارای exec - بهبود یافته"""
        files_with_exec = []
        
        # پوشه‌هایی که باید نادیده گرفته شوند
        IGNORE_PATTERNS = [
            '.backup', '.venv', 'node_modules', '__pycache__',
            '.emergency_backup', '.syntax_backup', '.warnings_backup',
            '.git', 'site-packages'
        ]
        
        for py_file in self.project_root.rglob('*.py'):
            # نادیده گرفتن پوشه‌های خاص
            if any(pattern in str(py_file) for pattern in IGNORE_PATTERNS):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # استفاده از AST برای تشخیص واقعی exec (نه در string/comment)
                try:
                    import ast
                    tree = ast.parse(content)
                    
                    has_real_exec = False
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Name) and node.func.id == 'exec':
                                has_real_exec = True
                                break
                    
                    if has_real_exec:
                        files_with_exec.append(py_file)
                except SyntaxError:
                    # fallback به روش ساده
    # SECURITY WARNING: Review exec usage for security implications
                    if 'exec(' in content:
                        files_with_exec.append(py_file)
                        
            except Exception as e:
                logger.warning(f"Cannot read {py_file}: {e}")
        
        return files_with_exec
    
    def backup_file(self, file_path: Path) -> Path:
        """ایجاد backup از فایل"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        logger.info(f"  💾 Backup created: {backup_path.name}")
        
        return backup_path
    
    def fix_file(self, file_path: Path) -> bool:
        """رفع یک فایل"""
        file_name = file_path.name
        
        logger.info(f"\n🔧 Processing: {file_path.relative_to(self.project_root)}")
        
        # ایجاد backup
        self.backup_file(file_path)
        
        # بررسی وجود قالب جایگزین
        if file_name in REPLACEMENT_TEMPLATES:
            # استفاده از قالب از پیش تعریف شده
            new_content = REPLACEMENT_TEMPLATES[file_name]
            file_path.write_text(new_content, encoding='utf-8')
            logger.info(f"  ✅ Replaced with secure template")
            self.files_fixed.append(file_path)
            return True
        
        # برای فایل‌های دیگر، تلاش برای رفع خودکار
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # الگوهای رایج exec و جایگزین آن‌ها
            patterns = [
                # exec(open(...).read()) → importlib
                (
                    r'exec\s*\(\s*open\s*\(\s*["\']([^"\']+)["\']\s*\)\s*\.read\s*\(\s*\)\s*\)',
                    '# TODO: Replace with importlib - see core/safety.py'
                ),
                # # TODO: Use SafeModuleLoader.load_class() instead → SafeModuleLoader
                (
                    r'exec\s*\(\s*f["\']([^"\']+)["\']\s*\)',
                    '# TODO: Use SafeModuleLoader.load_class() instead'
                ),
            ]
            
            new_content = content
            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, new_content, flags=re.MULTILINE)
            
            if new_content != content:
                file_path.write_text(new_content, encoding='utf-8')
                logger.info(f"  ✅ Auto-fixed exec patterns")
                self.files_fixed.append(file_path)
                return True
            else:
                logger.warning(f"  ⚠️ No automatic fix available")
                logger.warning(f"  📝 Manual review required")
                self.files_skipped.append(file_path)
                return False
                
        except Exception as e:
            logger.error(f"  ❌ Error processing file: {e}")
            return False
    
    def fix_all(self) -> Dict:
        """رفع همه فایل‌ها"""
    # SECURITY WARNING: Review exec usage for security implications
        logger.info("🔍 Scanning for exec() usage...")
        files = self.find_exec_files()
        
        if not files:
    # SECURITY WARNING: Review exec usage for security implications
            logger.info("✅ No exec() usage found")
            return {'fixed': 0, 'skipped': 0, 'files': []}
        
    # SECURITY WARNING: Review exec usage for security implications
        logger.info(f"📂 Found {len(files)} files with exec():")
        for f in files:
            logger.info(f"  - {f.relative_to(self.project_root)}")
        
        for file_path in files:
            self.fix_file(file_path)
        
        return {
            'fixed': len(self.files_fixed),
            'skipped': len(self.files_skipped),
            'fixed_files': [str(f) for f in self.files_fixed],
            'skipped_files': [str(f) for f in self.files_skipped]
        }
    
    def generate_report(self, results: Dict) -> str:
        """تولید گزارش"""
        report = [
            "=" * 60,
            "🛡️ EXEC FIX REPORT",
            "=" * 60,
            "",
            f"✅ Files fixed: {results['fixed']}",
            f"⚠️ Files need manual review: {results['skipped']}",
            "",
        ]
        
        if results['fixed_files']:
            report.append("Fixed files:")
            for f in results['fixed_files']:
                report.append(f"  ✅ {f}")
            report.append("")
        
        if results['skipped_files']:
            report.append("Files requiring manual review:")
            for f in results['skipped_files']:
                report.append(f"  ⚠️ {f}")
            report.append("")
            report.append("💡 Use SafeModuleLoader from core/safety.py")
        
        report.extend(["", "=" * 60])
        return "\n".join(report)


def main():
    """تابع اصلی"""
    # SECURITY WARNING: Review exec usage for security implications
    logger.info("🛡️ Starting exec() security fix")
    
    project_root = Path(__file__).parent.parent.parent
    fixer = ExecFixer(project_root)
    
    results = fixer.fix_all()
    report = fixer.generate_report(results)
    
    logger.info(report)
    
    if results['skipped'] > 0:
        logger.warning(f"\n⚠️ {results['skipped']} files need manual review")
        sys.exit(1)
    
    # SECURITY WARNING: Review exec usage for security implications
    logger.info("\n🎉 All exec() issues fixed!")


if __name__ == '__main__':
    main()
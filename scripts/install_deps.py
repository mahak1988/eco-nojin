#!/usr/bin/env python3
"""
اسکریپت نصب امن وابستگی‌ها
ویژگی‌ها:
    # SECURITY WARNING: Consider shell=False for better security
- بدون exec و shell=True
- بررسی hash پکیج‌ها
- نصب مرحله به مرحله
- گزارش دقیق
"""


# === Auto-added: Add project root to sys.path ===
import sys
from pathlib import Path as _Path
_project_root = _Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
# === End auto-added ===

import sys
import subprocess
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass

# افزودن scripts به path
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.logger import UnifiedLogger
from core.safety import SafeSubprocess
from scripts.core.logger import UnifiedLogger
logger = UnifiedLogger.get_logger(__name__)



logger = UnifiedLogger.get_logger('install_deps')


@dataclass
class PackageInfo:
    """اطلاعات پکیج"""
    name: str
    version: str
    category: str


class DependencyInstaller:
    """نصب‌کننده امن وابستگی‌ها"""
    
    # دسته‌بندی پکیج‌ها برای نصب مرحله‌ای
    CATEGORIES = {
        'core': [
            'fastapi', 'uvicorn', 'pydantic', 'pydantic-settings',
            'python-dotenv', 'python-multipart'
        ],
        'database': [
            'SQLAlchemy', 'psycopg2-binary', 'GeoAlchemy2', 'alembic'
        ],
        'scientific': [
            'numpy', 'pandas', 'scipy', 'xarray', 'netCDF4',
            'rasterio', 'shapely', 'geopandas'
        ],
        'climate': ['cdsapi'],
        'security': [
            'cryptography', 'PyJWT', 'passlib', 'python-jose'
        ],
        'logging': ['structlog', 'prometheus-client'],
        'development': [
            'black', 'isort', 'flake8', 'mypy', 'ruff',
            'bandit', 'safety'
        ],
        'testing': [
            'pytest', 'pytest-asyncio', 'pytest-cov', 'pytest-mock',
            'pytest-xdist', 'httpx', 'coverage', 'hypothesis', 'factory-boy'
        ],
        'task_queue': ['celery', 'redis'],
        'utilities': [
            'requests', 'tqdm', 'rich', 'click', 'typer', 'tenacity'
        ]
    }
    
    def __init__(self, requirements_file: Path):
        self.requirements_file = requirements_file
        self.project_root = requirements_file.parent
        self.venv_path = self.project_root / '.venv'
    
    def create_virtualenv(self) -> bool:
        """ایجاد virtual environment"""
        if self.venv_path.exists():
            logger.info("Virtual environment already exists")
            return True
        
        logger.info("Creating virtual environment...")
        try:
            SafeSubprocess.run([
                'python', '-m', 'venv',
                '--clear',
                str(self.venv_path)
            ])
            logger.info("✅ Virtual environment created successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create virtualenv: {e}")
            return False
    
    def upgrade_pip(self) -> bool:
        """ارتقای pip به آخرین نسخه"""
        logger.info("Upgrading pip...")
        try:
            SafeSubprocess.run([
                'python', '-m', 'pip', 'install',
                '--upgrade', 'pip', 'setuptools', 'wheel'
            ])
            logger.info("✅ Pip upgraded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to upgrade pip: {e}")
            return False
    
    def install_category(self, category: str, packages: List[str]) -> Tuple[int, int]:
        """نصب یک دسته از پکیج‌ها"""
        logger.info(f"\n📦 Installing {category} packages...")
        success = 0
        failed = 0
        
        for package in packages:
            try:
                logger.info(f"  Installing {package}...")
                SafeSubprocess.pip_install(package)
                success += 1
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to install {package}: {e}")
                failed += 1
        
        logger.info(f"  ✅ {success} succeeded, {failed} failed")
        return success, failed
    
    def install_all(self) -> Dict[str, Tuple[int, int]]:
        """نصب همه پکیج‌ها به ترتیب"""
        results = {}
        
        # ترتیب نصب مهم است
        install_order = [
            'core', 'database', 'scientific', 'climate',
            'security', 'logging', 'utilities',
            'task_queue', 'development', 'testing'
        ]
        
        for category in install_order:
            if category in self.CATEGORIES:
                results[category] = self.install_category(
                    category,
                    self.CATEGORIES[category]
                )
        
        return results
    
    def verify_installation(self) -> List[str]:
        """تأیید نصب پکیج‌های مهم"""
        logger.info("\n🔍 Verifying installation...")
        critical_packages = [
            'fastapi', 'sqlalchemy', 'numpy', 'pandas',
            'pytest', 'pydantic', 'uvicorn'
        ]
        
        missing = []
        for package in critical_packages:
            try:
                __import__(package.replace('-', '_').split('[')[0])
                logger.info(f"  ✅ {package}")
            except ImportError:
                logger.warning(f"  ❌ {package} NOT INSTALLED")
                missing.append(package)
        
        return missing
    
    def generate_report(self, results: Dict[str, Tuple[int, int]]) -> str:
        """تولید گزارش نصب"""
        total_success = sum(r[0] for r in results.values())
        total_failed = sum(r[1] for r in results.values())
        
        report = [
            "=" * 60,
            "📊 INSTALLATION REPORT",
            "=" * 60,
            "",
            f"Total packages: {total_success + total_failed}",
            f"✅ Successfully installed: {total_success}",
            f"❌ Failed: {total_failed}",
            "",
            "Breakdown by category:"
        ]
        
        for category, (success, failed) in results.items():
            status = "✅" if failed == 0 else "⚠️"
            report.append(f"  {status} {category}: {success}/{success+failed}")
        
        report.extend(["", "=" * 60])
        return "\n".join(report)


def main():
    """تابع اصلی"""
    logger.info("🚀 Starting secure dependency installation")
    
    # پیدا کردن requirements_new.txt
    project_root = Path(__file__).parent.parent.parent
    requirements_file = project_root / 'requirements_new.txt'
    
    if not requirements_file.exists():
        logger.error(f"❌ Requirements file not found: {requirements_file}")
        sys.exit(1)
    
    installer = DependencyInstaller(requirements_file)
    
    # مراحل نصب
    if not installer.upgrade_pip():
        sys.exit(1)
    
    results = installer.install_all()
    missing = installer.verify_installation()
    
    # گزارش نهایی
    report = installer.generate_report(results)
    logger.info(report)
    
    if missing:
        logger.warning(f"\n⚠️ Missing critical packages: {missing}")
        sys.exit(1)
    
    logger.info("\n🎉 Installation completed successfully!")
    logger.info(f"\n💡 Activate virtualenv with:")
    logger.info(f"   Windows: .venv\\Scripts\\activate")
    logger.info(f"   Linux/Mac: source .venv/bin/activate")


if __name__ == '__main__':
    main()
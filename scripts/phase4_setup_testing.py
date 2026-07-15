#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 4: Backend Testing Setup
===========================================
راه‌اندازی زیرساخت تست بک‌اند و ایجاد تست‌های اولیه

نحوه اجرا:
    python scripts/testing/phase4_setup_testing.py

نویسنده: Eco Nojin Team
نسخه: 4.0.0
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "4.0.0"
PROJECT_NAME = "Eco Nojin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase4_testing_setup.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
# Test Templates
# ============================================================

TEST_TEMPLATES = {
    "shared_core/test_database_session.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for shared_core.database.session
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apps.shared_core.database.session import get_db, init_db, close_db, AsyncSessionLocal


class TestDatabaseSession:
    """Tests for database session management"""
    
    @pytest.mark.asyncio
    async def test_get_db_yields_session(self):
        """Test that get_db yields a database session"""
        mock_session = AsyncMock()
        
        with patch("apps.shared_core.database.session.AsyncSessionLocal") as mock_factory:
            mock_factory.return_value.__aenter__.return_value = mock_session
            mock_factory.return_value.__aexit__.return_value = None
            
            async for db in get_db():
                assert db is not None
                break
    
    @pytest.mark.asyncio
    async def test_init_db_creates_tables(self):
        """Test that init_db creates database tables"""
        with patch("apps.shared_core.database.session.Base") as mock_base:
            mock_base.metadata.create_all = AsyncMock()
            
            await init_db()
            
            mock_base.metadata.create_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_db_disposes_engine(self):
        """Test that close_db disposes the engine"""
        with patch("apps.shared_core.database.session.engine") as mock_engine:
            mock_engine.dispose = AsyncMock()
            
            await close_db()
            
            mock_engine.dispose.assert_called_once()
''',
    
    "users/test_users_service.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for users service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apps.users.service import UserService
from apps.users.schemas import UserCreate, UserUpdate


class TestUserService:
    """Tests for UserService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock user repository"""
        repo = AsyncMock()
        repo.get_by_email = AsyncMock()
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo
    
    @pytest.fixture
    def service(self, mock_repository):
        """UserService instance with mock repository"""
        return UserService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, service, mock_repository):
        """Test successful user creation"""
        user_data = UserCreate(
            email="test@example.com",
            password="securepassword123",
            full_name="Test User"
        )
        
        mock_repository.get_by_email.return_value = None
        mock_repository.create.return_value = MagicMock(id=1, email="test@example.com")
        
        result = await service.create_user(user_data)
        
        assert result is not None
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, service, mock_repository):
        """Test user creation with duplicate email"""
        user_data = UserCreate(
            email="existing@example.com",
            password="password123",
            full_name="Test User"
        )
        
        mock_repository.get_by_email.return_value = MagicMock(id=1)
        
        with pytest.raises(ValueError, match="already exists"):
            await service.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, service, mock_repository):
        """Test getting user by ID"""
        mock_user = MagicMock(id=1, email="test@example.com")
        mock_repository.get_by_id.return_value = mock_user
        
        result = await service.get_user_by_id(1)
        
        assert result is not None
        assert result.id == 1
        mock_repository.get_by_id.assert_called_once_with(1)
''',
    
    "conftest.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest configuration and shared fixtures
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_session():
    """Mock database session"""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    session.refresh = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Mock user object"""
    user = MagicMock()
    user.id = 1
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.hashed_password = "hashed_password_here"
    user.is_active = True
    return user


@pytest.fixture
def sample_user_data():
    """Sample user creation data"""
    return {
        "email": "test@example.com",
        "password": "securepassword123",
        "full_name": "Test User"
    }
'''
}

# ============================================================
# Phase 4 Setup Script
# ============================================================

class Phase4Setup:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.apps_dir = project_root / "apps"
    
    def execute(self):
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint(f"🧪 {PROJECT_NAME} - Phase 4: Backend Testing Setup v{VERSION}", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        try:
            # گام ۱: نصب dependencies تست
            self._install_test_dependencies()
            
            # گام ۲: ایجاد فایل‌های تست
            self._create_test_files()
            
            # گام ۳: ایجاد pytest.ini
            self._create_pytest_config()
            
            # گام ۴: اجرای تست‌ها
            self._run_tests()
            
            # گام ۵: تولید گزارش
            self._generate_report()
            
        except Exception as e:
            logger.error(f"❌ خطا: {e}")
            import traceback
            traceback.print_exc()
    
    def _install_test_dependencies(self):
        cprint("\n📦 گام ۱: نصب dependencies تست...", Colors.BLUE)
        
        test_deps = [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
            "httpx>=0.24.0",
        ]
        
        try:
            for dep in test_deps:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep],
                    capture_output=True,
                    check=True
                )
                cprint(f"   ✅ {dep}", Colors.GREEN)
        except subprocess.CalledProcessError as e:
            cprint(f"   ❌ خطا در نصب: {e}", Colors.RED)
    
    def _create_test_files(self):
        cprint("\n📝 گام ۲: ایجاد فایل‌های تست...", Colors.BLUE)
        
        for file_rel, content in TEST_TEMPLATES.items():
            if file_rel == "conftest.py":
                file_path = self.apps_dir / file_rel
            else:
                module_name = file_rel.split("/")[0]
                file_path = self.apps_dir / module_name / "tests" / file_rel.split("/", 1)[1]
            
            if file_path.exists():
                cprint(f"   ⏩ {file_rel} از قبل وجود دارد", Colors.DIM)
                continue
            
            try:
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content, encoding="utf-8")
                cprint(f"   ✅ ایجاد شد: {file_rel}", Colors.GREEN)
            except Exception as e:
                cprint(f"   ❌ خطا در ایجاد {file_rel}: {e}", Colors.RED)
    
    def _create_pytest_config(self):
        cprint("\n⚙️  گام ۳: ایجاد pytest.ini...", Colors.BLUE)
        
        pytest_ini = self.project_root / "pytest.ini"
        
        if pytest_ini.exists():
            cprint("   ⏩ pytest.ini از قبل وجود دارد", Colors.DIM)
            return
        
        content = """[pytest]
testpaths = apps
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts = -v --tb=short
"""
        
        try:
            pytest_ini.write_text(content, encoding="utf-8")
            cprint("   ✅ pytest.ini ایجاد شد", Colors.GREEN)
        except Exception as e:
            cprint(f"   ❌ خطا: {e}", Colors.RED)
    
    def _run_tests(self):
        cprint("\n🧪 گام ۴: اجرای تست‌ها...", Colors.BLUE)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "apps/", "-v", "--tb=short"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            cprint(result.stdout, Colors.END)
            
            if result.returncode == 0:
                cprint("   ✅ تمام تست‌ها موفق بودند", Colors.GREEN)
            else:
                cprint(f"   ⚠️  برخی تست‌ها ناموفق بودند", Colors.YELLOW)
        
        except Exception as e:
            cprint(f"   ❌ خطا در اجرای تست‌ها: {e}", Colors.RED)
    
    def _generate_report(self):
        cprint("\n📊 گام ۵: تولید گزارش...", Colors.BLUE)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📈 خلاصه فاز ۴", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        cprint("\n✅ اقدامات انجام‌شده:")
        cprint("   • نصب dependencies تست")
        cprint("   • ایجاد ۳ فایل تست اولیه")
        cprint("   • ایجاد pytest.ini")
        cprint("   • اجرای تست‌ها")
        
        cprint("\n📌 گام‌های بعدی:")
        cprint("   1. افزودن تست‌های بیشتر برای هر ماژول")
        cprint("   2. اجرای: pytest --cov=apps --cov-report=html")
        cprint("   3. بررسی پوشش تست در htmlcov/index.html")
        cprint("   4. Commit: git add . && git commit -m 'phase-4: testing setup'")

# ============================================================
# Main
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

def main():
    project_root = find_project_root()
    
    cprint(f"\n🌱 {PROJECT_NAME} Phase 4 v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه: {project_root}", Colors.DIM)
    
    setup = Phase4Setup(project_root)
    setup.execute()

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
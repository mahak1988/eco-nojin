#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏗️ Refactor Mega Builder - نسخه نهایی و بهینه‌سازی شده
تقسیم build_phase4_mega.py به ماژول‌های کوچک‌تر با رفع مشکلات پورت‌پذیری و امنیت
"""
import shutil
import sys
from pathlib import Path
from datetime import datetime

# تعیین هوشمند ریشه پروژه بر اساس محل قرارگیری این اسکریپت
ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = ROOT.parent if ROOT.name == "scripts" else ROOT

MEGA_FILE = PROJECT_ROOT / "scripts" / "build_phase4_mega.py"
LEGACY_DIR = PROJECT_ROOT / "scripts" / "legacy" / "build_phase4"
MODULES_DIR = PROJECT_ROOT / "scripts" / "builders"


def write_file(path: Path, content: str):
    """نوشتن فایل با ایجاد خودکار دایرکتوری‌های والد"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ Created: {path.relative_to(PROJECT_ROOT)}")


def archive_original():
    print("\n[1/6] Archiving original file...")
    LEGACY_DIR.mkdir(parents=True, exist_ok=True)
    
    if MEGA_FILE.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = LEGACY_DIR / f"build_phase4_mega_{timestamp}.py"
        shutil.copy2(MEGA_FILE, archive_path)
        print(f"✅ Archived: {archive_path.relative_to(PROJECT_ROOT)}")
        MEGA_FILE.unlink()
        print(f"✅ Removed original: {MEGA_FILE.relative_to(PROJECT_ROOT)}")
    else:
        print(f"⚠️ File not found: {MEGA_FILE.relative_to(PROJECT_ROOT)} (Skipping archive)")


def create_base_builder():
    print("\n[2/6] Creating base builder...")
    # رفع ریسک Hardcoded Paths: تعیین داینامیک PROJECT_ROOT
    content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Builder Module
Provides common functionality for all builders.
"""
import logging
import shutil
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# تعیین داینامیک ریشه پروژه بر اساس مسیر این فایل
# مسیر: scripts/builders/base_builder.py -> ریشه: parent.parent.parent
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"

class BaseBuilder:
    """کلاس پایه برای تمام سازنده‌ها با قابلیت پشتیبان‌گیری خودکار"""
    def __init__(self, name: str):
        self.name = name
        self.backup_dir = PROJECT_ROOT / f".{name}_backup"
        self.backup_dir.mkdir(exist_ok=True)
        self.files_created = []
    
    def backup(self, path: Path):
        """ایجاد پشتیبان امن قبل از بازنویسی فایل"""
        if not path.exists():
            return
        try:
            rel = path.relative_to(PROJECT_ROOT)
            dest = self.backup_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = dest.parent / f"{dest.stem}_{ts}{dest.suffix}"
            shutil.copy2(path, backup)
            logger.debug(f"  📦 Backed up: {rel}")
        except Exception as e:
            logger.error(f"  ⚠️ Backup failed for {path}: {e}")
    
    def write(self, path: Path, content: str):
        """نوشتن محتوا با مدیریت خودکار پشتیبان و دایرکتوری‌ها"""
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self.backup(path)
        path.write_text(content, encoding="utf-8")
        self.files_created.append(path.relative_to(PROJECT_ROOT))
        logger.info(f"  ✓ {path.relative_to(PROJECT_ROOT)}")
    
    def get_stats(self) -> dict:
        return {
            "name": self.name,
            "files_created": len(self.files_created),
            "files": [str(f) for f in self.files_created]
        }
'''
    write_file(MODULES_DIR / "base_builder.py", content)


def create_i18n_builder():
    print("\n[3/6] Creating i18n builder...")
    content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
i18n Builder Module
Generates internationalization files for the frontend.
"""
import json
import logging
from .base_builder import BaseBuilder, FRONTEND_DIR

logger = logging.getLogger(__name__)

class I18nBuilder(BaseBuilder):
    SUPPORTED_LOCALES = ["fa", "en", "ar", "tr", "zh"]
    
    def __init__(self):
        super().__init__("i18n")
    
    def build(self):
        logger.info("\\n" + "="*70)
        logger.info("🌐 Building i18n System")
        logger.info("="*70)
        
        for locale in self.SUPPORTED_LOCALES:
            self._create_locale_file(locale)
        self._create_i18n_index()
        return self.get_stats()
    
    def _create_locale_file(self, locale: str):
        translations = self._get_translations(locale)
        path = FRONTEND_DIR / "lib" / "i18n" / f"{locale}.json"
        self.write(path, json.dumps(translations, ensure_ascii=False, indent=2))
    
    def _get_translations(self, locale: str) -> dict:
        translations = {
            "fa": {"common": {"appName": "اکونوژین", "home": "خانه", "login": "ورود"}},
            "en": {"common": {"appName": "Econojin", "home": "Home", "login": "Login"}},
            "ar": {"common": {"appName": "إكونوجين", "home": "الرئيسية", "login": "دخول"}},
            "tr": {"common": {"appName": "Econojin", "home": "Ana Sayfa", "login": "Giriş"}},
            "zh": {"common": {"appName": "Econojin", "home": "首页", "login": "登录"}}
        }
        return translations.get(locale, translations["en"])
    
    def _create_i18n_index(self):
        """ایجاد فایل index.ts کامل برای تمام زبان‌های پشتیبانی شده"""
        content = ""
        for locale in self.SUPPORTED_LOCALES:
            content += f"import {locale} from './{locale}.json';\\n"
        content += "\\n"
        content += "export const translations = {\\n"
        for locale in self.SUPPORTED_LOCALES:
            content += f"  {locale},\\n"
        content += "};\\n\\n"
        content += f"export const locales = {self.SUPPORTED_LOCALES} as const;\\n"
        content += "export type Locale = typeof locales[number];\\n"
        
        path = FRONTEND_DIR / "lib" / "i18n" / "index.ts"
        self.write(path, content)
'''
    write_file(MODULES_DIR / "i18n_builder.py", content)


def create_contracts_builder():
    print("\n[4/6] Creating contracts builder...")
    content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contracts Builder Module
Generates Solidity smart contracts and secure Hardhat configuration.
"""
import logging
from .base_builder import BaseBuilder, CONTRACTS_DIR

logger = logging.getLogger(__name__)

class ContractsBuilder(BaseBuilder):
    def __init__(self):
        super().__init__("contracts")
    
    def build(self):
        logger.info("\\n" + "="*70)
        logger.info("📜 Building Smart Contracts")
        logger.info("="*70)
        
        self._create_seed_token()
        self._create_gaia_certificate()
        self._create_hardhat_config()
        return self.get_stats()
    
    def _create_seed_token(self):
        content = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract SeedToken is ERC20, Ownable {
    constructor() ERC20("Seed Token", "SEED") Ownable(msg.sender) {
        _mint(msg.sender, 1000000 * 10 ** decimals());
    }
    
    function mint(address to, uint256 amount) public onlyOwner {
        _mint(to, amount);
    }
}
"""
        path = CONTRACTS_DIR / "contracts" / "SeedToken.sol"
        self.write(path, content)
    
    def _create_gaia_certificate(self):
        content = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract GaiaCertificate is ERC721 {
    uint256 private _nextTokenId;
    
    constructor() ERC721("Gaia Certificate", "GAIA") {}
    
    function mint(address to) public returns (uint256) {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
        return tokenId;
    }
}
"""
        path = CONTRACTS_DIR / "contracts" / "GaiaCertificate.sol"
        self.write(path, content)
    
    def _create_hardhat_config(self):
        # تقویت امنیت: ارائه الگوی امن برای استفاده از متغیرهای محیطی
        content = """require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: "0.8.20",
  networks: {
    localhost: { 
      url: "http://127.0.0.1:8545" 
    },
    // ⚠️ SECURITY NOTE: 
    // هرگز کلیدهای خصوصی یا RPC URL ها را در این فایل hardcode نکنید.
    // همیشه از متغیرهای محیطی در فایل .env استفاده کنید.
    // مثال:
    // sepolia: {
    //   url: process.env.SEPOLIA_RPC_URL || "",
    //   accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : []
    // }
  }
};
"""
        path = CONTRACTS_DIR / "hardhat.config.js"
        self.write(path, content)
'''
    write_file(MODULES_DIR / "contracts_builder.py", content)


def create_orchestrator():
    print("\n[5/6] Creating orchestrator...")
    content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Builder Orchestrator
Coordinates the execution of all builder modules with error handling.
"""
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# حل مشکل import برای اجرای مستقیم اسکریپت
sys.path.insert(0, str(Path(__file__).parent))

from builders.i18n_builder import I18nBuilder
from builders.contracts_builder import ContractsBuilder

def run_builders():
    logger.info("="*70)
    logger.info("🚀 Econojin Builder Orchestrator")
    logger.info("="*70)
    
    builders = [
        ("i18n", I18nBuilder),
        ("contracts", ContractsBuilder),
    ]
    
    results = {}
    for name, builder_class in builders:
        try:
            logger.info(f"\\n▶️  Running {name} builder...")
            builder = builder_class()
            stats = builder.build()
            results[name] = stats
            logger.info(f"✅ {name}: {stats['files_created']} files created")
        except Exception as e:
            logger.error(f"❌ {name} failed: {e}", exc_info=True)
            results[name] = {"error": str(e)}
    
    return results

def main():
    try:
        results = run_builders()
        failed = [n for n, r in results.items() if isinstance(r, dict) and "error" in r]
        
        if failed:
            logger.error(f"\\n❌ Build failed for: {', '.join(failed)}")
            return 1
        else:
            logger.info("\\n" + "="*70)
            logger.info("✅ All builders completed successfully!")
            logger.info("="*70)
            return 0
    except Exception as e:
        logger.error(f"❌ Fatal error in orchestrator: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    write_file(MODULES_DIR.parent / "build_econojin.py", content)


def create_init_file():
    print("\n[6/6] Creating __init__.py...")
    content = '''"""
Econojin Builders Package
Modular builders for generating project components.
"""
from .base_builder import BaseBuilder
from .i18n_builder import I18nBuilder
from .contracts_builder import ContractsBuilder

__all__ = ["BaseBuilder", "I18nBuilder", "ContractsBuilder"]
'''
    write_file(MODULES_DIR / "__init__.py", content)


def main():
    print("🏗️ Refactoring Mega Builder")
    print("=" * 60)
    print(f"Source: {MEGA_FILE.relative_to(PROJECT_ROOT) if MEGA_FILE.exists() else 'Not Found'}")
    print(f"Target: {MODULES_DIR.relative_to(PROJECT_ROOT)}")
    print("=" * 60)
    
    if MEGA_FILE.exists():
        print("\\n⚠️  This script will:")
        print("   1. Archive build_phase4_mega.py to scripts/legacy/")
        print("   2. Create modular builders in scripts/builders/")
        print("   3. Create orchestrator: scripts/build_econojin.py")
        
        confirm = input("\\n   Continue? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("\\n❌ Cancelled by user.")
            return 1
    else:
        print(f"\\n⚠️  Source file not found: {MEGA_FILE.relative_to(PROJECT_ROOT)}")
        print("   Proceeding with creation of new modules only...")
    
    archive_original()
    create_base_builder()
    create_i18n_builder()
    create_contracts_builder()
    create_init_file()
    create_orchestrator()
    
    print("\\n" + "=" * 60)
    print("✅ Refactoring completed!")
    print("\\n📁 New structure:")
    print("   scripts/builders/")
    print("   ├── base_builder.py")
    print("   ├── i18n_builder.py")
    print("   ├── contracts_builder.py")
    print("   └── __init__.py")
    print("   scripts/build_econojin.py")
    print("\\n🚀 To run:")
    print("   python scripts/build_econojin.py")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
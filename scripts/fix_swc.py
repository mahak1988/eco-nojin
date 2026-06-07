import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
دانلود و نصب SWC binary مخصوص Windows برای Next.js 15.0.5
r"""

import os
import subprocess
import sys
from pathlib import Path
from urllib.request import urlretrieve

PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DOWNLOAD_DIR = FRONTEND_DIR / ".offline_packages"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# URL مستقیم SWC binary برای Windows x64
SWC_PACKAGE = "@next/swc-win32-x64-msvc"
SWC_VERSION = "15.0.5"
SWC_URL = f"https://registry.npmmirror.com/@next/swc-win32-x64-msvc/-/swc-win32-x64-msvc-{SWC_VERSION}.tgz"
SWC_FILE = DOWNLOAD_DIR / f"next-swc-win32-x64-msvc-{SWC_VERSION}.tgz"


def download_swc():
    """دانلود SWC binary"""
    print("=" * 70)
    logger.info("🔧 FIX SWC BINARY - Next.js 15.0.5")
    print("=" * 70)

    if SWC_FILE.exists():
        logger.info(f"\n  ⏭️  Already downloaded: {SWC_FILE.name}")
    else:
        logger.info(f"\n  📥 Downloading {SWC_PACKAGE}@{SWC_VERSION}...")
        logger.info(f"     URL: {SWC_URL}")

        try:
            urlretrieve(SWC_URL, SWC_FILE)
            size_mb = SWC_FILE.stat().st_size / (1024 * 1024)
            logger.info(f"  ✅ Downloaded: {size_mb:.1f} MB")
        except Exception as e:
            logger.info(f"  ❌ Download failed: {e}")

            # تلاش با mirror جایگزین
            alt_url = f"https://registry.npmjs.org/@next/swc-win32-x64-msvc/-/swc-win32-x64-msvc-{SWC_VERSION}.tgz"
            logger.info(f"\n  🔄 Trying alternative mirror...")
            logger.info(f"     URL: {alt_url}")

            try:
                urlretrieve(alt_url, SWC_FILE)
                size_mb = SWC_FILE.stat().st_size / (1024 * 1024)
                logger.info(f"  ✅ Downloaded: {size_mb:.1f} MB")
            except Exception as e2:
                logger.info(f"  ❌ Alternative also failed: {e2}")
                return False

    return True


def install_swc():
    """نصب SWC binary"""
    logger.info(f"\n  📦 Installing {SWC_PACKAGE}...")

    # نصب با npm
    cmd = ["npm", "install", "--no-save", str(SWC_FILE)]

    try:
        result = subprocess.run(
            cmd,
            cwd=FRONTEND_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            shell=(os.name == "nt"),
        )

        if result.returncode == 0:
            logger.info("  ✅ SWC binary installed successfully!")
            return True
        else:
            logger.info(f"  ❌ Installation failed:")
            logger.info(str(result.stderr[:500]))
            return False
    except Exception as e:
        logger.info(f"  ❌ Error: {e}")
        return False


def verify_installation():
    """تأیید نصب"""
    print("\n" + "=" * 70)
    logger.info("🔍 Verifying Installation")
    print("=" * 70)

    swc_dir = FRONTEND_DIR / "node_modules" / "@next" / "swc-win32-x64-msvc"

    if swc_dir.exists():
        logger.info(f"  ✅ SWC directory exists: {swc_dir}")

        # بررسی فایل .node
        node_files = list(swc_dir.glob("*.node"))
        if node_files:
            logger.info(f"  ✅ Binary file found: {node_files[0].name}")
            return True
        else:
            # بررسی در subdirectory
            for root, dirs, files in os.walk(swc_dir):
                for f in files:
                    if f.endswith(".node"):
                        logger.info(f"  ✅ Binary file found: {f}")
                        return True

            logger.info("  ❌ No .node file found")
            return False
    else:
        logger.info(f"  ❌ SWC directory not found")
        return False


def generate_next_steps():
    """تولید راهنمای گام‌های بعدی"""
    print("\n" + "=" * 70)
    logger.info("🚀 NEXT STEPS")
    print("=" * 70)
    print(
        r"""
1) اجرای مجدد dev server:
   cd D:\\econojin.com\\frontend
   npm run dev

2) باز کردن مرورگر:
   http://localhost:3000

3) اگر باز هم مشکل داشت:
   
   راه‌حل جایگزین (استفاده از Babel به جای SWC):
   
   a) ایجاد فایل .babelrc در frontend:
      {
        "presets": ["next/babel"]
      }
   
   b) ایجاد فایل next.config.js:
      module.exports = {
        swcMinify: false
      }
   
   c) نصب Babel:
      npm install --save-dev @babel/core babel-loader
   
   d) اجرای مجدد:
      npm run dev
r"""
    )
    print("=" * 70)


def main():
    if not FRONTEND_DIR.exists():
        logger.info(f"❌ Frontend directory not found: {FRONTEND_DIR}")
        return 1

    # دانلود
    if not download_swc():
        logger.info("\n❌ Download failed. Please try manual download.")
        return 1

    # نصب
    if install_swc():
        # تأیید
        if verify_installation():
            generate_next_steps()
            return 0

    logger.info("\n❌ Installation failed. Try alternative solution.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

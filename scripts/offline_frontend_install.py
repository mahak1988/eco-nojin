# scripts/resume_frontend_download.py
"""
اسکریپت resume دانلود با requests و مدیریت بهتر خطا
فقط پکیج‌های دانلود نشده را دانلود می‌کند
r"""

import json
import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    logger.info("❌ requests نصب نیست. ابتدا اجرا کنید:")
    logger.info("   pip install requests")
    sys.exit(1)

PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DOWNLOAD_DIR = FRONTEND_DIR / ".offline_packages"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

# همه پکیج‌های مورد نیاز
ALL_PACKAGES = {
    "next": "15.0.5",
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "lucide-react": "0.460.0",
    "@radix-ui/react-slot": "1.1.0",
    "clsx": "2.1.1",
    "tailwind-merge": "2.5.4",
    "class-variance-authority": "0.7.1",
    "tailwindcss": "3.4.15",
    "tailwindcss-animate": "1.0.7",
    "autoprefixer": "10.4.20",
    "postcss": "8.4.49",
    "axios": "1.7.9",
    "typescript": "5.6.3",
    "@types/node": "20.17.10",
    "@types/react": "18.3.12",
    "@types/react-dom": "18.3.1",
}

# Mirror‌های جایگزین (به ترتیب اولویت)
MIRRORS = [
    "https://registry.npmmirror.com",
    "https://registry.npmjs.org",
    "https://registry.yarnpkg.com",
]


def create_robust_session():
    """ایجاد session با retry قوی"""
    session = requests.Session()

    retry_strategy = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10,
    )
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) npm/10.0.0",
            "Accept": "*/*",
        }
    )

    return session


def get_tarball_url(package: str, version: str, mirror: str) -> str:
    """دریافت URL tarball از mirror مشخص"""
    if package.startswith("@"):
        org, name = package.split("/")
        return f"{mirror}/{org}/{name}/-/{name}-{version}.tgz"
    else:
        return f"{mirror}/{package}/-/{package}-{version}.tgz"


def download_package(package: str, version: str) -> bool:
    """دانلود یک پکیج با fallback بین mirror‌ها"""
    safe_name = package.replace("@", "").replace("/", "-")
    filename = f"{safe_name}-{version}.tgz"
    dest = DOWNLOAD_DIR / filename

    # اگر قبلاً دانلود شده
    if dest.exists() and dest.stat().st_size > 1000:
        logger.info(f"  ⏭️  {package}@{version} (cached)")
        return True

    session = create_robust_session()

    for i, mirror in enumerate(MIRRORS, 1):
        url = get_tarball_url(package, version, mirror)
        logger.info(f"  📥 {package}@{version} (mirror {i}/{len(MIRRORS)})")

        try:
            response = session.get(url, timeout=120, stream=True)
            response.raise_for_status()

            # دانلود با progress
            total = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(dest, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

            size_kb = downloaded / 1024
            logger.info(f"      ✓ Downloaded {size_kb:.1f} KB")
            return True

        except Exception as e:
            logger.info(f"      ✗ Failed: {type(e).__name__}")
            if dest.exists():
                dest.unlink()
            continue

    logger.info(f"  ❌ All mirrors failed for {package}")
    return False


def install_downloaded():
    """نصب پکیج‌های دانلود شده"""
    import subprocess

    tgz_files = list(DOWNLOAD_DIR.glob("*.tgz"))
    if not tgz_files:
        logger.info("❌ No .tgz files found")
        return False

    logger.info(f"\n📦 Installing {len(tgz_files)} packages...")

    cmd = ["npm", "install", "--no-save", "--legacy-peer-deps"] + [str(f) for f in tgz_files]

    result = subprocess.run(
        cmd,
        cwd=FRONTEND_DIR,
        capture_output=True,
        text=True,
        shell=(os.name == "nt"),
    )

    if result.returncode == 0:
        logger.info("✅ Installation successful!")
        return True
    else:
        logger.info(f"❌ Installation failed:\n{result.stderr[:500]}")
        return False


def main():
    logger.info("=" * 70)
    logger.info("🚀 RESUME FRONTEND DOWNLOAD")
    logger.info("=" * 70)

    # بررسی پکیج‌های دانلود شده
    existing = list(DOWNLOAD_DIR.glob("*.tgz"))
    logger.info(f"\n📊 Already downloaded: {len(existing)}/{len(ALL_PACKAGES)}")

    # دانلود پکیج‌های باقی‌مانده
    logger.info("\n📥 Downloading remaining packages...")
    success_count = 0
    failed = []

    for package, version in ALL_PACKAGES.items():
        if download_package(package, version):
            success_count += 1
        else:
            failed.append(package)

    logger.info(f"\n✅ Downloaded: {success_count}/{len(ALL_PACKAGES)}")

    if failed:
        logger.info(f"❌ Failed: {', '.join(failed)}")

    # نصب
    if success_count > 0:
        logger.info("\n" + "=" * 70)
        install_downloaded()

    logger.info("\n🚀 Next step:")
    logger.info("   cd D:\\econojin.com\\frontend")
    logger.info("   npm run dev")


if __name__ == "__main__":
    main()

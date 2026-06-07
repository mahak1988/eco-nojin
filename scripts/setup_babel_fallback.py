import os
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path


def download_swc_binary():
    """دانلود و نصب SWC binary برای Next.js 15.0.5"""

    # مسیرها
    frontend_dir = Path(r"D:\econojin.com\frontend")
    download_dir = frontend_dir / ".offline_packages"
    download_dir.mkdir(exist_ok=True)

    # اطلاعات پکیج
    package_name = "@next/swc-win32-x64-msvc"
    version = "15.0.5"
    filename = f"swc-win32-x64-msvc-{version}.tgz"
    download_path = download_dir / filename

    # Mirror‌های مختلف
    mirrors = [
        f"https://registry.npmmirror.com/@next/swc-win32-x64-msvc/-/{filename}",
        f"https://registry.npmjs.org/@next/swc-win32-x64-msvc/-/{filename}",
        f"https://cdn.npmmirror.com/packages/@next/swc-win32-x64-msvc/{version}/{filename}",
    ]

    # دانلود
    if not download_path.exists():
        print(f"📥 Downloading SWC binary ({version})...")

        for i, url in enumerate(mirrors, 1):
            print(f"  Attempt {i}/{len(mirrors)}: {url}")
            try:
                urllib.request.urlretrieve(url, download_path)
                print(f"  ✅ Downloaded: {download_path.stat().st_size / 1024 / 1024:.1f} MB")
                break
            except Exception as e:
                print(f"  ❌ Failed: {e}")
                if download_path.exists():
                    download_path.unlink()
        else:
            print("❌ All mirrors failed")
            print("\n💡 Manual download options:")
            print(f"  1. Download from browser: {mirrors[0]}")
            print(f"  2. Copy to: {download_path}")
            return False

    # استخراج
    print(f"\n📦 Extracting {filename}...")
    extract_dir = download_dir / "swc-extracted"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir()

    with tarfile.open(download_path, "r:gz") as tar:
        tar.extractall(extract_dir)

    # پیدا کردن فایل .node
    node_files = list(extract_dir.rglob("*.node"))
    if not node_files:
        print("❌ No .node file found in archive")
        return False

    # کپی به node_modules
    target_dir = frontend_dir / "node_modules" / "@next" / "swc-win32-x64-msvc"
    target_dir.mkdir(parents=True, exist_ok=True)

    # کپی همه فایل‌ها
    for item in extract_dir.glob("package/*"):
        if item.is_file():
            shutil.copy2(item, target_dir / item.name)
        else:
            dest = target_dir / item.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(item, dest)

    print(f"✅ SWC binary installed to: {target_dir}")

    # پاکسازی
    shutil.rmtree(extract_dir)

    return True


if __name__ == "__main__":
    success = download_swc_binary()
    sys.exit(0 if success else 1)

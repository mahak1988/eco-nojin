# auto_downloader_ir.py - نسخه مخصوص ایران
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


class IranianPyPIDownloader:
    # استفاده از mirror ایرانی برای دسترسی پایدار
    PYPI_MIRRORS = [
        "https://mirror-pypi.runflare.com/simple",
        "https://pypi.org/simple",
    ]

    PYPI_API = "https://pypi.org/pypi"  # API اصلی

    def __init__(self, download_dir="offline_packages"):
        self.download_dir = Path(download_dir)
        self._ensure_directory()

        # پاک کردن proxy از محیط
        for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
            if var in os.environ:
                del os.environ[var]

        # تنظیم proxy handler برای دور زدن proxy سیستم
        proxy_handler = urllib.request.ProxyHandler({})
        self.opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(self.opener)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        }

    def _ensure_directory(self):
        """ایجاد پوشه با مدیریت مشکلات"""
        try:
            if self.download_dir.exists() and not self.download_dir.is_dir():
                print(f"⚠️ حذف فایل مزاحم: {self.download_dir}")
                self.download_dir.unlink()

            self.download_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ پوشه آماده: {self.download_dir.resolve()}")
        except Exception as e:
            print(f"❌ خطا: {e}")
            self.download_dir = Path("offline_packages_alt")
            self.download_dir.mkdir(exist_ok=True)

    def _make_request(self, url, timeout=30):
        """درخواست HTTP با دور زدن proxy"""
        req = urllib.request.Request(url, headers=self.headers)
        try:
            return self.opener.open(req, timeout=timeout)
        except urllib.error.URLError as e:
            # اگر proxy فعال است، تلاش بدون proxy
            if "proxy" in str(e).lower() or "10061" in str(e):
                print(f"  ⚠️ مشکل proxy، تلاش مجدد...")
                # بازگشت خطا برای مدیریت توسط caller
                raise
            raise

    def get_pypi_info(self, package_name, version=None):
        """دریافت اطلاعات از PyPI API"""
        if version:
            url = f"{self.PYPI_API}/{package_name}/{version}/json"
        else:
            url = f"{self.PYPI_API}/{package_name}/json"

        print(f"🔍 دریافت اطلاعات {package_name}...")

        try:
            with self._make_request(url, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"  ⚠️ API اصلی در دسترس نیست: {e}")
            print(f"  💡 از روش جایگزین (دانلود مستقیم) استفاده می‌شود")
            return None

    def find_best_wheel(self, package_info, python_version="cp313"):
        """یافتن بهترین wheel"""
        if not package_info:
            return None

        urls = package_info.get("urls", [])

        priority_order = [
            lambda u: f"{python_version}-win_amd64" in u["filename"]
            and u["packagetype"] == "bdist_wheel",
            lambda u: "cp312-win_amd64" in u["filename"] and u["packagetype"] == "bdist_wheel",
            lambda u: "cp311-win_amd64" in u["filename"] and u["packagetype"] == "bdist_wheel",
            lambda u: "py3-none-any" in u["filename"] and u["packagetype"] == "bdist_wheel",
            lambda u: u["packagetype"] == "bdist_wheel",
        ]

        for priority_fn in priority_order:
            for url_info in urls:
                if priority_fn(url_info):
                    return url_info

        return urls[0] if urls else None

    def download_with_retry(self, url, filename, max_retries=3):
        """دانلود با retry"""
        filepath = self.download_dir / filename

        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  ✅ موجود: {filename} ({size_mb:.2f} MB)")
            return filepath

        print(f"  📥 دانلود: {filename}")

        for attempt in range(max_retries):
            try:
                with self._make_request(url, timeout=60) as response:
                    total_size = int(response.headers.get("content-length", 0))
                    downloaded = 0
                    chunk_size = 8192

                    with open(filepath, "wb") as f:
                        while True:
                            chunk = response.read(chunk_size)
                            if not chunk:
                                break
                            f.write(chunk)
                            downloaded += len(chunk)

                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                mb_done = downloaded / (1024 * 1024)
                                mb_total = total_size / (1024 * 1024)
                                print(
                                    f"\r     {percent:5.1f}% | {mb_done:.1f}/{mb_total:.1f} MB",
                                    end="",
                                    flush=True,
                                )

                    print(f"\n  ✅ کامل شد")
                    return filepath

            except Exception as e:
                print(f"\n  ⚠️ تلاش {attempt + 1}/{max_retries} ناموفق")
                if filepath.exists():
                    filepath.unlink()
                if attempt < max_retries - 1:
                    time.sleep(2)

        return None

    def install_with_pip_using_mirror(self, package_names):
        """نصب با استفاده از mirror ایرانی"""
        print(f"\n🔧 نصب با mirror ایرانی...")

        # ابتدا از mirror استفاده می‌کنیم
        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--trusted-host",
            "mirror-pypi.runflare.com",
            "--index-url",
            "https://mirror-pypi.runflare.com/simple",
            "--timeout",
            "120",
        ] + package_names

        print(f"💻 اجرا: pip install از mirror ایرانی\n")
        print("=" * 60)

        result = subprocess.run(cmd)
        print("=" * 60)

        if result.returncode == 0:
            return True

        # اگر mirror کار نکرد، از فایل‌های محلی استفاده کن
        print("\n🔄 mirror کار نکرد، تلاش از پوشه محلی...")
        return self.install_from_local(package_names)

    def install_from_local(self, package_names):
        """نصب از فایل‌های دانلود شده"""
        wheel_files = list(self.download_dir.glob("*.whl"))
        if not wheel_files:
            print("❌ هیچ فایل wheel یافت نشد")
            return False

        cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-index",
            f"--find-links={self.download_dir.resolve()}",
        ] + package_names

        result = subprocess.run(cmd)
        return result.returncode == 0

    def verify_installation(self):
        """بررسی نصب"""
        print("\n🔍 بررسی نصب:")
        packages = [
            "contourpy",
            "cycler",
            "fonttools",
            "kiwisolver",
            "PIL",
            "matplotlib",
            "seaborn",
            "aquacrop",
        ]

        success = []
        failed = []

        for pkg in packages:
            try:
                __import__(pkg)
                success.append(pkg)
                print(f"  ✅ {pkg}")
            except ImportError:
                failed.append(pkg)
                print(f"  ❌ {pkg}")

        return len(failed) == 0

    def run(self):
        print("=" * 70)
        print("🇮🇷 دانلود و نصب خودکار (با mirror ایرانی)")
        print("=" * 70)
        print(f"📂 پوشه: {self.download_dir.resolve()}")
        print(f"🐍 Python: {sys.executable}")
        print(f"🌐 Proxy: غیرفعال شد")

        # بررسی محیط
        if "tutorial_env" in sys.executable:
            print(f"\n⚠️  توجه: از tutorial_env استفاده می‌کنید!")
            print(f"   پیشنهاد: از .venv استفاده کنید:")
            print(f"   & d:\\econojin.com\\.venv\\Scripts\\Activate.ps1")

        print()

        # استراتژی هوشمند: ابتدا pip با mirror را امتحان کن
        print("🎯 استراتژی: ابتدا pip با mirror، سپس دانلود دستی")
        print("-" * 70)

        packages = [
            "contourpy",
            "cycler",
            "fonttools",
            "kiwisolver",
            "pillow",
            "matplotlib",
            "seaborn",
            "aquacrop==3.0.12",
        ]

        # تلاش اول: pip با mirror ایرانی
        if self.install_with_pip_using_mirror(packages):
            print("\n✅ نصب با mirror ایرانی موفق بود!")
            if self.verify_installation():
                print("\n🎉 تمام پکیج‌ها آماده هستند!")
                self._final_test()
                return True

        print("\n⚠️ نصب با mirror موفق نبود، دانلود دستی...")

        # تلاش دوم: دانلود از API
        packages_to_download = [
            ("contourpy", None),
            ("cycler", None),
            ("fonttools", None),
            ("kiwisolver", None),
            ("pillow", None),
            ("matplotlib", None),
            ("seaborn", None),
            ("aquacrop", "3.0.12"),
        ]

        downloaded = []
        for pkg_name, version in packages_to_download:
            print(f"\n📦 {pkg_name}")
            info = self.get_pypi_info(pkg_name, version)
            if info:
                file_info = self.find_best_wheel(info)
                if file_info:
                    path = self.download_with_retry(file_info["url"], file_info["filename"])
                    if path:
                        downloaded.append(pkg_name)

        if downloaded:
            print(f"\n🔧 نصب فایل‌های دانلود شده...")
            self.install_from_local(downloaded)
            self.verify_installation()

        self._final_test()

    def _final_test(self):
        """تست نهایی AquaCrop"""
        try:
            from aquacrop import AquaCropOS

            print("\n🎉 AquaCropOS آماده استفاده است!")
        except ImportError as e:
            print(f"\n⚠️ AquaCropOS: {e}")
            print("\n💡 اگر مشکل ادامه داشت:")
            print("   1. از fallback داخلی استفاده می‌شود")
            print("   2. یا aquacrop را از FAO دانلود کنید:")
            print("      https://github.com/KUL-RSDA/AquaCrop/releases")


if __name__ == "__main__":
    downloader = IranianPyPIDownloader()
    downloader.run()

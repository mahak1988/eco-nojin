# auto_downloader_v2.py
import urllib.request
import urllib.error
import subprocess
import sys
import os
import time
import json
from pathlib import Path

class PyPIDownloader:
    def __init__(self, download_dir='offline_packages'):
        self.download_dir = Path(download_dir)
        self._ensure_directory()
        
        # تنظیم User-Agent برای جلوگیری از بلاک شدن
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-AutoDownloader/2.0',
            'Accept': 'application/json'
        }
    
    def _ensure_directory(self):
        """ایجاد پوشه با مدیریت مشکلات احتمالی"""
        try:
            # اگر فایل با این نام وجود دارد، حذف شود
            if self.download_dir.exists() and not self.download_dir.is_dir():
                print(f"⚠️ یک فایل با نام {self.download_dir} یافت شد، در حال حذف...")
                self.download_dir.unlink()
            
            # ایجاد پوشه
            self.download_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ پوشه آماده است: {self.download_dir.resolve()}")
            
        except Exception as e:
            print(f"❌ خطا در ایجاد پوشه: {e}")
            # تلاش با نام جایگزین
            self.download_dir = Path('offline_packages_alt')
            self.download_dir.mkdir(exist_ok=True)
            print(f"✅ پوشه جایگزین ایجاد شد: {self.download_dir.resolve()}")
    
    def get_pypi_info(self, package_name, version=None):
        """دریافت اطلاعات پکیج از PyPI API با urllib"""
        if version:
            url = f"https://pypi.org/pypi/{package_name}/{version}/json"
        else:
            url = f"https://pypi.org/pypi/{package_name}/json"
        
        print(f"🔍 دریافت اطلاعات {package_name}...")
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"❌ خطای HTTP برای {package_name}: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"❌ خطای شبکه: {e.reason}")
            return None
        except Exception as e:
            print(f"❌ خطای غیرمنتظره: {e}")
            return None
    
    def find_best_wheel(self, package_info, python_version='cp313'):
        """یافتن بهترین فایل wheel"""
        if not package_info:
            return None
        
        urls = package_info.get('urls', [])
        
        # اولویت‌ها
        priority_order = [
            lambda u: f'{python_version}-win_amd64' in u['filename'] and u['packagetype'] == 'bdist_wheel',
            lambda u: 'cp312-win_amd64' in u['filename'] and u['packagetype'] == 'bdist_wheel',
            lambda u: 'cp311-win_amd64' in u['filename'] and u['packagetype'] == 'bdist_wheel',
            lambda u: 'py3-none-any' in u['filename'] and u['packagetype'] == 'bdist_wheel',
            lambda u: u['packagetype'] == 'bdist_wheel',
            lambda u: u['packagetype'] == 'sdist',
        ]
        
        for priority_fn in priority_order:
            for url_info in urls:
                if priority_fn(url_info):
                    return url_info
        
        return urls[0] if urls else None
    
    def download_with_retry(self, url, filename, max_retries=5):
        """دانلود با retry و نمایش پیشرفت"""
        filepath = self.download_dir / filename
        
        if filepath.exists():
            size_mb = filepath.stat().st_size / (1024 * 1024)
            print(f"  ✅ فایل از قبل موجود است: {filename} ({size_mb:.2f} MB)")
            return filepath
        
        print(f"  📥 دانلود: {filename}")
        
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=60) as response:
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0
                    chunk_size = 8192
                    
                    with open(filepath, 'wb') as f:
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
                                print(f"\r     {percent:5.1f}% | {mb_done:.1f}/{mb_total:.1f} MB", end='', flush=True)
                    
                    print(f"\n  ✅ دانلود کامل شد")
                    return filepath
                    
            except Exception as e:
                print(f"\n  ⚠️ تلاش {attempt + 1}/{max_retries} ناموفق: {str(e)[:60]}")
                if filepath.exists():
                    filepath.unlink()
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3
                    print(f"  ⏳ {wait_time} ثانیه صبر...")
                    time.sleep(wait_time)
        
        print(f"  ❌ دانلود ناموفق: {filename}")
        return None
    
    def download_package(self, package_name, version=None):
        """دانلود یک پکیج"""
        info = self.get_pypi_info(package_name, version)
        if not info:
            return None
        
        best_file = self.find_best_wheel(info)
        if not best_file:
            print(f"❌ فایل مناسبی برای {package_name} یافت نشد")
            return None
        
        filename = best_file['filename']
        url = best_file['url']
        
        return self.download_with_retry(url, filename)
    
    def install_packages(self, package_names):
        """نصب پکیج‌ها از پوشه محلی"""
        print(f"\n🔧 نصب پکیج‌ها...")
        
        cmd = [
            sys.executable, '-m', 'pip', 'install',
            '--no-index',
            f'--find-links={self.download_dir.resolve()}',
        ] + package_names
        
        print(f"💻 اجرا: {' '.join(cmd[:6])} ...\n")
        print("=" * 60)
        
        result = subprocess.run(cmd)
        
        print("=" * 60)
        return result.returncode == 0
    
    def verify_installation(self):
        """بررسی نصب"""
        print("\n🔍 بررسی نصب:")
        packages = ['contourpy', 'cycler', 'fonttools', 'kiwisolver', 
                   'PIL', 'matplotlib', 'seaborn', 'aquacrop']
        
        for pkg in packages:
            try:
                __import__(pkg)
                print(f"  ✅ {pkg}")
            except ImportError:
                print(f"  ❌ {pkg}")
    
    def run(self):
        print("=" * 70)
        print("🎯 دانلود و نصب خودکار (بدون نیاز به requests)")
        print("=" * 70)
        print(f"📂 پوشه دانلود: {self.download_dir.resolve()}")
        print(f"🐍 Python: {sys.executable}\n")
        
        # پکیج‌ها به ترتیب نصب
        packages = [
            ('contourpy', None),
            ('cycler', None),
            ('fonttools', None),
            ('kiwisolver', None),
            ('pillow', None),
            ('matplotlib', None),
            ('seaborn', None),
            ('aquacrop', '3.0.12'),
        ]
        
        downloaded_files = []
        failed_packages = []
        
        for pkg_name, version in packages:
            print(f"\n{'='*60}")
            print(f"📦 پردازش: {pkg_name} {f'(نسخه {version})' if version else ''}")
            print(f"{'='*60}")
            
            # بررسی نصب بودن
            pkg_import = 'PIL' if pkg_name == 'pillow' else pkg_name
            try:
                __import__(pkg_import)
                print(f"  ✅ از قبل نصب شده است، رد شد")
                continue
            except ImportError:
                pass
            
            filepath = self.download_package(pkg_name, version)
            if filepath:
                downloaded_files.append((pkg_name, filepath))
            else:
                failed_packages.append(pkg_name)
        
        # گزارش
        print("\n" + "=" * 70)
        print("📊 گزارش دانلود")
        print("=" * 70)
        print(f"  ✅ دانلود موفق: {len(downloaded_files)}")
        print(f"  ❌ دانلود ناموفق: {len(failed_packages)}")
        
        if failed_packages:
            print(f"\n⚠️ پکیج‌های ناموفق: {', '.join(failed_packages)}")
        
        # نصب
        if downloaded_files:
            pkg_names = [name for name, _ in downloaded_files]
            success = self.install_packages(pkg_names)
            
            if success:
                self.verify_installation()
                
                # تست نهایی
                try:
                    from aquacrop import AquaCropOS
                    print("\n🎉 AquaCropOS آماده استفاده است!")
                except ImportError as e:
                    print(f"\n⚠️ AquaCropOS: {e}")
            else:
                print("\n❌ نصب ناموفق. نصب دستی:")
                for name, filepath in downloaded_files:
                    print(f"   pip install {filepath}")
        
        return len(failed_packages) == 0


if __name__ == "__main__":
    downloader = PyPIDownloader()
    downloader.run()
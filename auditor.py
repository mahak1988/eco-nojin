import os
import json
import re
import time
from pathlib import Path
from collections import defaultdict
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("⚠️ لطفاً کتابخانه‌های زیر را نصب کنید: pip install requests beautifulsoup4")

class EcoNojinAuditor:
    def __init__(self, local_dir, live_url=None):
        self.local_dir = Path(local_dir)
        self.live_url = live_url
        self.report_lines = []
        
        self.expected_stack = {
            "Frontend (GIS & UI)": ["react", "vue", "leaflet", "mapbox-gl", "react-leaflet", "openlayers", "tailwindcss", "next"],
            "Backend (Data & API)": ["fastapi", "django", "celery", "redis", "geopandas", "rasterio", "shapely", "fiona", "xarray"],
            "Database & DevOps": ["postgis", "postgresql", "docker", "kubernetes", "nginx", "traefik", "minio"]
        }

    def log(self, message, level="INFO"):
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌", "HEADER": "🔹"}.get(level, "")
        line = f"{icon} {message}"
        self.report_lines.append(line)
        print(line)

    def analyze_local_architecture(self):
        self.log("🔹 شروع تحلیل معماری محلی و استک فناوری...", "HEADER")
        if not self.local_dir.exists():
            self.log(f"مسیر {self.local_dir} یافت نشد!", "ERROR")
            return

        found_tech = defaultdict(list)
        loc_stats = defaultdict(int)
        code_extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.html', '.css', '.sql', '.sh'}
        
        for root, dirs, files in os.walk(self.local_dir):
            dirs[:] = [d for d in dirs if d not in {'node_modules', '.git', '__pycache__', '.venv', 'venv', 'env'}]
            
            for file in files:
                file_path = Path(root) / file
                
                if file_path.suffix in code_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = len(f.readlines())
                            loc_stats[file_path.suffix] += lines
                    except Exception:
                        pass

                if file == 'package.json':
                    self._parse_package_json(file_path, found_tech)
                elif file in ['requirements.txt', 'Pipfile', 'pyproject.toml']:
                    self._parse_python_deps(file_path, found_tech)
                elif file in ['docker-compose.yml', 'docker-compose.yaml', 'Dockerfile']:
                    self._parse_docker(file_path, found_tech)

        self.log("📦 بررسی تطابق با معماری اکو نوژین:")
        for category, techs in self.expected_stack.items():
            found = [t for t in techs if t in found_tech[category]]
            missing = [t for t in techs if t not in found_tech[category]]
            if found:
                self.log(f"[{category}] موارد یافت شده: {', '.join(found)}", "SUCCESS")
            if missing:
                self.log(f"[{category}] موارد پیشنهادیِ یافت‌نشده: {', '.join(missing)}", "WARNING")

        self.log("📊 آمار خطوط کد (LOC):")
        total_loc = 0
        for ext, count in sorted(loc_stats.items(), key=lambda x: x[1], reverse=True):
            self.log(f"  - {ext}: {count:,} خط")
            total_loc += count
        self.log(f"  🔸 مجموع کل: {total_loc:,} خط", "INFO")

    def _parse_package_json(self, path, found_tech):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                deps = list(data.get('dependencies', {}).keys()) + list(data.get('devDependencies', {}).keys())
                for dep in deps:
                    for cat, techs in self.expected_stack.items():
                        if cat.startswith("Frontend"):
                            if any(t in dep.lower() for t in techs):
                                found_tech[cat].append(dep)
        except Exception:
            pass

    def _parse_python_deps(self, path, found_tech):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                for cat, techs in self.expected_stack.items():
                    if cat.startswith("Backend") or cat.startswith("Database"):
                        for tech in techs:
                            if tech in content:
                                found_tech[cat].append(tech)
        except Exception:
            pass

    def _parse_docker(self, path, found_tech):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                for tech in self.expected_stack["Database & DevOps"]:
                    if tech in content:
                        found_tech["Database & DevOps"].append(tech)
        except Exception:
            pass

    def security_scan(self):
        self.log("🔹 شروع اسکن امنیتی محلی...", "HEADER")
        risks = 0
        
        env_files = list(self.local_dir.rglob('.env*'))
        if env_files:
            self.log(f"تعداد {len(env_files)} فایل .env یافت شد. (مطمئن شوید در .gitignore باشند)", "WARNING")
            risks += 1
            
        sensitive_patterns = [
            r'(?i)(password|passwd|pwd)\s*=\s*["\'][^"\']+["\']',
            r'(?i)(api_key|apikey|secret_key)\s*=\s*["\'][^"\']+["\']'
        ]
        
        for ext in ['.py', '.js', '.ts', '.jsx', '.tsx']:
            for file_path in self.local_dir.rglob(f'*{ext}'):
                if 'node_modules' in str(file_path) or 'venv' in str(file_path):
                    continue
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        for pattern in sensitive_patterns:
                            if re.search(pattern, content):
                                self.log(f"هشدار امنیتی: احتمال وجود کلید هاردکد شده در {file_path.name}", "ERROR")
                                risks += 1
                                break
                except Exception:
                    pass
                    
        if risks == 0:
            self.log("هیچ ریسک امنیتی آشکاری در سطح فایل‌ها یافت نشد.", "SUCCESS")

    def live_site_audit(self):
        if not self.live_url:
            return
            
        self.log(f"🔹 شروع ممیزی سایت زنده: {self.live_url}", "HEADER")
        try:
            start_time = time.time()
            headers = {'User-Agent': 'EcoNojinAuditor/1.0'}
            response = requests.get(self.live_url, headers=headers, timeout=10, allow_redirects=True)
            ttfb = (time.time() - start_time) * 1000
            
            self.log(f"وضعیت HTTP: {response.status_code} | زمان پاسخ (TTFB): {ttfb:.2f} ms", "SUCCESS" if response.status_code == 200 else "ERROR")
            
            security_headers = {
                'Strict-Transport-Security': 'HSTS (اجبار HTTPS)',
                'Content-Security-Policy': 'CSP (جلوگیری از XSS)',
                'X-Content-Type-Options': 'جلوگیری از MIME Sniffing',
                'X-Frame-Options': 'جلوگیری از Clickjacking'
            }
            
            self.log("🛡️ بررسی هدرهای امنیتی سرور:")
            for header, desc in security_headers.items():
                if header in response.headers:
                    self.log(f"  {desc}: موجود است ✅", "SUCCESS")
                else:
                    self.log(f"  {desc}: یافت نشد! ⚠️", "WARNING")

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "بدون عنوان"
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            
            self.log("🔍 بررسی سئو (SEO):")
            self.log(f"  عنوان صفحه: {title}")
            if meta_desc and meta_desc.get('content'):
                self.log(f"  توضیحات متا: {meta_desc['content'][:80]}...", "SUCCESS")
            else:
                self.log("  توضیحات متا (Meta Description) یافت نشد!", "WARNING")

        except requests.exceptions.RequestException as e:
            self.log(f"خطا در اتصال به سایت زنده: {e}", "ERROR")

    def generate_report(self):
        self.log("🔹 تولید گزارش نهایی...", "HEADER")
        report_path = self.local_dir / "EcoNojin_Audit_Report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# 🌍 گزارش ممیزی فنی و معماری پلتفرم اکو نوژین\n")
            f.write(f"**تاریخ اجرا:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**مسیر محلی:** `{self.local_dir}`\n\n---\n\n")
            for line in self.report_lines:
                f.write(line.replace("✅", "- ✅").replace("⚠️", "- ⚠️").replace("❌", "- ❌") + "\n")
        
        self.log(f"✅ گزارش با موفقیت ذخیره شد:\n{report_path}", "SUCCESS")

if __name__ == "__main__":
    LOCAL_PATH = r"D:\econojin.com"
    LIVE_URL = None  # اگر سایت آنلاین است، آدرس را اینجا قرار دهید (مثلاً "https://econojin.com")
    
    print("🚀 شروع ممیزی جامع پلتفرم اکو نوژین...\n")
    auditor = EcoNojinAuditor(LOCAL_PATH, LIVE_URL)
    auditor.analyze_local_architecture()
    print("\n" + "="*60 + "\n")
    auditor.security_scan()
    print("\n" + "="*60 + "\n")
    auditor.live_site_audit()
    print("\n" + "="*60 + "\n")
    auditor.generate_report()
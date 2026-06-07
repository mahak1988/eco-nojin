import ast
import os
from collections import defaultdict
from pathlib import Path


class MissingImportsChecker:
    def __init__(self, project_path, missing_packages):
        self.root = Path(project_path).resolve()
        self.missing_packages = missing_packages
        self.imports_found = defaultdict(list)  # package -> list of files

    def scan_imports(self):
        """جستجوی importهای پکیج‌های گمشده در کل پروژه"""
        print("🔍 در حال جستجوی importهای پکیج‌های گمشده...\n")

        for py_file in self.root.rglob("*.py"):
            # نادیده گرفتن پوشه‌های مخفی و node_modules
            if any(
                part.startswith(".") or part in {"node_modules", "venv", "__pycache__"}
                for part in py_file.parts
            ):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            base_module = alias.name.split(".")[0]
                            if base_module in self.missing_packages:
                                rel_path = py_file.relative_to(self.root)
                                self.imports_found[base_module].append(
                                    {
                                        "file": str(rel_path),
                                        "line": node.lineno,
                                        "import": f"import {alias.name}",
                                    }
                                )

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            base_module = node.module.split(".")[0]
                            if base_module in self.missing_packages:
                                rel_path = py_file.relative_to(self.root)
                                names = ", ".join(alias.name for alias in node.names)
                                self.imports_found[base_module].append(
                                    {
                                        "file": str(rel_path),
                                        "line": node.lineno,
                                        "import": f"from {node.module} import {names}",
                                    }
                                )

            except Exception:
                continue

    def generate_report(self):
        """تولید گزارش با راه‌حل‌های پیشنهادی"""
        print("=" * 70)
        print("📋 گزارش Importهای گمشده و راه‌حل‌ها")
        print("=" * 70)

        # راه‌حل‌های پیشنهادی برای هر پکیج
        solutions = {
            "rothc": {
                "explanation": "مدل RothC یک پکیج PyPI نیست. این مدل معمولاً به‌صورت محلی پیاده‌سازی می‌شود.",
                "solutions": [
                    "✅ بررسی کنید آیا فایل backend/models/carbon/rothc_model.py پیاده‌سازی محلی دارد یا خیر",
                    "✅ اگر دارد، import را از پکیج خارجی به import محلی تغییر دهید",
                    "✅ اگر ندارد، می‌توانید از کتابخانه‌های مشابه مانند `soilcarbon` استفاده کنید",
                ],
            },
            "aquacrop": {
                "explanation": "AquaCrop معمولاً از منابع رسمی FAO نصب می‌شود.",
                "solutions": [
                    "✅ نصب از GitHub: pip install git+https://github.com/KUL-RSDA/AquaCrop.git",
                    "✅ یا استفاده از aquacrop-wrapper: pip install aquacrop-wrapper",
                    "✅ یا بررسی کنید آیا backend/models/crop/aquacrop_integration.py پیاده‌سازی محلی دارد",
                ],
            },
            "structlog": {
                "explanation": "پکیج استاندارد لاگینگ ساختاریافته",
                "solutions": ["✅ pip install structlog"],
            },
            "geoalchemy2": {
                "explanation": "افزونه SQLAlchemy برای داده‌های جغرافیایی",
                "solutions": ["✅ pip install GeoAlchemy2"],
            },
            "rioxarray": {
                "explanation": "افزونه xarray برای داده‌های raster",
                "solutions": ["✅ pip install rioxarray"],
            },
            "cdsapi": {
                "explanation": "API برای دانلود داده‌های Copernicus Climate Data Store",
                "solutions": [
                    "✅ pip install cdsapi",
                    "⚠️ نیاز به ثبت‌نام در https://cds.climate.copernicus.eu/ و دریافت API key",
                ],
            },
            "prometheus_client": {
                "explanation": "کتابخانه Prometheus برای monitoring",
                "solutions": ["✅ pip install prometheus-client"],
            },
        }

        for package in self.missing_packages:
            print(f"\n{'='*70}")
            print(f"📦 پکیج: {package}")
            print(f"{'='*70}")

            if package in solutions:
                print(f"\n💡 {solutions[package]['explanation']}\n")

            if package in self.imports_found:
                files = self.imports_found[package]
                print(f"⚠️  این پکیج در {len(files)} فایل import شده است:\n")

                for imp_info in files[:10]:  # نمایش ۱۰ فایل اول
                    print(f"  📄 {imp_info['file']} (خط {imp_info['line']})")
                    print(f"     → {imp_info['import']}")

                if len(files) > 10:
                    print(f"\n  ... و {len(files) - 10} فایل دیگر")

                print(f"\n🎯 راه‌حل‌های پیشنهادی:")
                for i, solution in enumerate(solutions.get(package, {}).get("solutions", []), 1):
                    print(f"   {solution}")
            else:
                print("✅ این پکیج در هیچ فایلی import نشده است!")
                print("   → می‌توانید آن را از requirements-missing.txt حذف کنید")

    def generate_fixed_requirements(self):
        """تولید فایل requirements اصلاح‌شده"""
        print(f"\n{'='*70}")
        print("📝 تولید فایل requirements-missing-fixed.txt")
        print(f"{'='*70}\n")

        fixed_packages = []

        for package in self.missing_packages:
            if package in self.imports_found:
                # پکیج واقعاً استفاده می‌شود
                if package == "rothc":
                    # rothc را نادیده بگیر - احتمالاً محلی است
                    print(f"  ❌ {package}: حذف شد (پیاده‌سازی محلی)")
                elif package == "aquacrop":
                    # نسخه صحیح aquacrop
                    fixed_packages.append("git+https://github.com/KUL-RSDA/AquaCrop.git")
                    print(f"  ✓ {package}: اضافه شد (از GitHub)")
                elif package == "prometheus_client":
                    fixed_packages.append("prometheus-client")
                    print(f"  ✓ {package}: اضافه شد (با نام صحیح)")
                else:
                    fixed_packages.append(package)
                    print(f"  ✓ {package}: اضافه شد")
            else:
                print(f"  ❌ {package}: حذف شد (استفاده نشده)")

        # ذخیره فایل جدید
        output_file = self.root / "requirements-missing-fixed.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# پکیج‌های مورد نیاز (اصلاح‌شده)\n")
            f.write("# برای نصب: pip install -r requirements-missing-fixed.txt\n\n")
            for pkg in fixed_packages:
                f.write(f"{pkg}\n")

        print(f"\n✅ فایل {output_file.name} ایجاد شد")
        print(f"📦 {len(fixed_packages)} پکیج برای نصب باقی ماند")

    def run(self):
        self.scan_imports()
        self.generate_report()
        self.generate_fixed_requirements()


if __name__ == "__main__":
    # پکیج‌های گمشده از گزارش قبلی
    missing = {
        "rothc",
        "aquacrop",
        "structlog",
        "geoalchemy2",
        "rioxarray",
        "cdsapi",
        "prometheus_client",
    }

    checker = MissingImportsChecker(".", missing)
    checker.run()

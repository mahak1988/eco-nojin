#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Econojin Structure Checker
بررسی کامل ساختار پروژه و گزارش موارد مفقوده
"""
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


# رنگ‌ها برای خروجی کنسول (ویندوز/لینوکس)
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


@dataclass
class CheckItem:
    """یک آیتم برای بررسی (پوشه یا فایل)"""

    path: str
    item_type: str  # 'dir' or 'file'
    description: str
    critical: bool = True  # آیا وجود این مورد حیاتی است؟
    created: bool = False


@dataclass
class CheckReport:
    """گزارش نهایی بررسی"""

    total: int = 0
    exists: int = 0
    missing: int = 0
    critical_missing: List[CheckItem] = field(default_factory=list)
    optional_missing: List[CheckItem] = field(default_factory=list)

    @property
    def completion_percent(self) -> float:
        if self.total == 0:
            return 0
        return (self.exists / self.total) * 100


class StructureChecker:
    """بررسی‌کننده ساختار پروژه Econojin"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.items: List[CheckItem] = []
        self._define_expected_structure()

    def _define_expected_structure(self):
        """تعریف ساختار مورد انتظار پروژه"""

        # === پوشه‌های اصلی ===
        main_dirs = [
            ("backend", "پوشه اصلی بک‌اند"),
            ("backend/api", "ماژول اصلی FastAPI"),
            ("backend/api/core", "تنظیمات و پیکربندی هسته"),
            ("backend/api/modules", "ماژول‌های کاربردی"),
            ("backend/api/agents", "ایجنت‌های هوش مصنوعی"),
            ("backend/tests", "تست‌های بک‌اند"),
            ("frontend", "پوشه اصلی فرانت‌اند"),
            ("frontend/src", "کدهای منبع فرانت‌اند"),
            ("frontend/src/app", "صفحات Next.js"),
            ("frontend/src/components", "کامپوننت‌های React"),
            ("frontend/public", "فایل‌های استاتیک"),
            ("docs", "مستندات پروژه"),
            ("infrastructure", "فایل‌های زیرساخت"),
            ("infrastructure/docker", "پیکربندی Docker"),
            ("scripts", "اسکریپت‌های کمکی"),
        ]

        # === ماژول‌های بک‌اند (۱۵ بخش) ===
        backend_modules = [
            ("backend/api/modules/weather", "ماژول هواشناسی"),
            ("backend/api/modules/accounting", "ماژول حسابداری"),
            ("backend/api/modules/calendar", "ماژول تقویم و جلسات"),
            ("backend/api/modules/store", "ماژول فروشگاه"),
            ("backend/api/modules/library", "ماژول کتابخانه"),
            ("backend/api/modules/desktop", "ماژول میزکار وب"),
            ("backend/api/modules/education", "ماژول آموزش و وبینار"),
            ("backend/api/modules/gis", "ماژول GIS و نقشه"),
            ("backend/api/modules/psychology", "ماژول روانشناسی"),
            ("backend/api/modules/telegram_bots", "ماژول ربات‌های تلگرام"),
            ("backend/api/modules/ecomining", "ماژول EcoCoin و ماینینگ"),
            ("backend/api/modules/community", "ماژول جامعه و خیریه"),
            ("backend/api/modules/games", "ماژول بازی و متاورس"),
            ("backend/api/modules/infrastructure", "ماژول زیرساخت"),
        ]

        # === صفحات فرانت‌اند ===
        frontend_pages = [
            ("frontend/src/app/dashboard", "داشبورد اصلی"),
            ("frontend/src/app/weather", "صفحه هواشناسی"),
            ("frontend/src/app/accounting", "صفحه حسابداری"),
            ("frontend/src/app/education", "صفحه آموزش"),
            ("frontend/src/app/gis", "صفحه GIS"),
            ("frontend/src/app/ecomining", "صفحه EcoCoin"),
            ("frontend/src/app/psychology", "صفحه روانشناسی"),
        ]

        # === فایل‌های حیاتی ===
        critical_files = [
            ("backend/api/main.py", "فایل اصلی FastAPI"),
            ("backend/requirements.txt", "وابستگی‌های پایتون"),
            ("frontend/package.json", "وابستگی‌های Node.js"),
            ("frontend/next.config.js", "پیکربندی Next.js"),
            ("README.md", "مستندات اصلی پروژه"),
            (".env.example", "الگوی متغیرهای محیطی"),
            ("backend/api/core/config.py", "تنظیمات پیکربندی"),
            ("backend/api/core/database.py", "پیکربندی دیتابیس"),
        ]

        # === فایل‌های اختیاری (پیشرفته) ===
        optional_files = [
            ("infrastructure/docker/docker-compose.yml", "Docker Compose"),
            ("infrastructure/docker/Dockerfile.backend", "Dockerfile بک‌اند"),
            ("infrastructure/docker/Dockerfile.frontend", "Dockerfile فرانت‌اند"),
            ("docs/api/README.md", "مستندات API"),
            ("docs/user-guides/getting-started.md", "راهنمای شروع کاربر"),
            ("scripts/01_install_dependencies.sh", "اسکریپت نصب"),
            ("scripts/02_run_econojin.py", "اسکریپت اجرا"),
            ("backend/api/agents/orchestrator.py", "ارکستراتور ایجنت‌ها"),
        ]

        # افزودن به لیست بررسی
        for path, desc in main_dirs + backend_modules + frontend_pages:
            self.items.append(CheckItem(path, "dir", desc, critical=True))

        for path, desc in critical_files:
            self.items.append(CheckItem(path, "file", desc, critical=True))

        for path, desc in optional_files:
            self.items.append(CheckItem(path, "file", desc, critical=False))

    def check(self) -> CheckReport:
        """اجرای بررسی و تولید گزارش"""
        report = CheckReport()
        report.total = len(self.items)

        for item in self.items:
            full_path = self.project_root / item.path
            exists = full_path.exists()
            item.created = exists

            if exists:
                report.exists += 1
            else:
                report.missing += 1
                if item.critical:
                    report.critical_missing.append(item)
                else:
                    report.optional_missing.append(item)

        return report

    def print_report(self, report: CheckReport):
        """چاپ گزارش با رنگ و فرمت مناسب"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 گزارش بررسی ساختار Econojin{Colors.END}")
        print(f"{'='*60}")
        print(f"📁 مسیر پروژه: {Colors.BLUE}{self.project_root}{Colors.END}")
        print()

        # آمار کلی
        print(f"📊 آمار کلی:")
        print(f"   • کل موارد بررسی‌شده: {report.total}")
        print(f"   • ✅ موجود: {Colors.GREEN}{report.exists}{Colors.END}")
        print(f"   • ❌ مفقود: {Colors.RED}{report.missing}{Colors.END}")
        print(f"   • 📈 درصد تکمیل: {Colors.BOLD}{report.completion_percent:.1f}%{Colors.END}")
        print()

        # موارد حیاتی مفقوده
        if report.critical_missing:
            print(f"{Colors.RED}{Colors.BOLD}⚠️ موارد حیاتی مفقوده (باید ایجاد شوند):{Colors.END}")
            for item in report.critical_missing:
                icon = "📁" if item.item_type == "dir" else "📄"
                print(f"   {Colors.RED}{icon} {item.path}{Colors.END}")
                print(f"      ↳ {item.description}")
            print()

        # موارد اختیاری مفقوده
        if report.optional_missing:
            print(
                f"{Colors.YELLOW}{Colors.BOLD}ℹ️ موارد اختیاری مفقوده (تکمیل پیشنهادی):{Colors.END}"
            )
            for item in report.optional_missing:
                icon = "📁" if item.item_type == "dir" else "📄"
                print(f"   {Colors.YELLOW}{icon} {item.path}{Colors.END}")
                print(f"      ↳ {item.description}")
            print()

        # وضعیت نهایی
        if report.missing == 0:
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 تبریک! ساختار پروژه کامل است.{Colors.END}")
        elif not report.critical_missing:
            print(
                f"{Colors.YELLOW}{Colors.BOLD}✅ ساختار اصلی کامل است. موارد اختیاری را می‌توانید بعداً اضافه کنید.{Colors.END}"
            )
        else:
            print(
                f"{Colors.RED}{Colors.BOLD}❌ ساختار ناقص است. لطفاً موارد حیاتی را ایجاد کنید.{Colors.END}"
            )

        print(f"{'='*60}\n")

    def create_missing(self, report: CheckReport, create_optional: bool = False):
        """ایجاد خودکار موارد مفقوده"""
        if not report.missing:
            print("✅ هیچ مورد مفقوده‌ای برای ایجاد وجود ندارد.")
            return

        items_to_create = report.critical_missing.copy()
        if create_optional:
            items_to_create.extend(report.optional_missing)

        print(f"🔧 در حال ایجاد {len(items_to_create)} مورد مفقوده...")

        for item in items_to_create:
            full_path = self.project_root / item.path
            try:
                if item.item_type == "dir":
                    full_path.mkdir(parents=True, exist_ok=True)
                    # ایجاد فایل __init__.py برای پوشه‌های پایتون
                    if "backend" in item.path or "api" in item.path:
                        init_file = full_path / "__init__.py"
                        if not init_file.exists():
                            init_file.write_text("# Econojin Module\n", encoding="utf-8")
                else:
                    full_path.parent.mkdir(parents=True, exist_ok=True)
                    # ایجاد فایل خالی با محتوای اولیه
                    if item.path.endswith(".py"):
                        content = f"# {item.description}\n# Auto-generated by Structure Checker\n\n"
                    elif item.path.endswith(".json"):
                        content = '{\n  "note": "Auto-generated"\n}\n'
                    elif item.path.endswith(".yml") or item.path.endswith(".yaml"):
                        content = f"# {item.description}\n# Auto-generated\n\n"
                    else:
                        content = f"# {item.description}\n"
                    full_path.write_text(content, encoding="utf-8")

                print(f"   ✅ ایجاد شد: {item.path}")

            except Exception as e:
                print(f"   ❌ خطا در ایجاد {item.path}: {e}")

        print(f"\n{Colors.GREEN}✅ فرآیند ایجاد موارد مفقوده تکمیل شد.{Colors.END}")


def main():
    """تابع اصلی اجرا"""
    # تعیین مسیر پروژه
    if len(sys.argv) > 1:
        project_path = Path(sys.argv[1])
    else:
        # جستجوی خودکار: پوشه econojin-super-platform در مسیر فعلی یا والد
        current = Path.cwd()
        if (current / "econojin-super-platform").exists():
            project_path = current / "econojin-super-platform"
        elif current.name == "econojin-super-platform":
            project_path = current
        else:
            # جستجو در والد
            parent = current.parent
            if (parent / "econojin-super-platform").exists():
                project_path = parent / "econojin-super-platform"
            else:
                print(f"❌ پوشه پروژه یافت نشد.")
                print(f"💡 راهنمایی: اسکریپت را در پوشه پروژه اجرا کنید یا مسیر را مشخص کنید:")
                print(f"   python check_structure.py /path/to/econojin-super-platform")
                return 1

    # ایجاد بررسی‌کننده و اجرا
    checker = StructureChecker(project_path)
    report = checker.check()
    checker.print_report(report)

    # پیشنهاد ایجاد خودکار
    if report.missing > 0:
        print("آیا می‌خواهید موارد مفقوده به‌طور خودکار ایجاد شوند؟")
        print(f"   {Colors.GREEN}y{Colors.END} = فقط موارد حیاتی")
        print(f"   {Colors.YELLOW}Y{Colors.END} = همه موارد (حیاتی + اختیاری)")
        print(f"   {Colors.RED}n{Colors.END} = خیر، فقط گزارش")

        choice = input(f"\nانتخاب شما [y/Y/n]: ").strip().lower()

        if choice == "y":
            checker.create_missing(report, create_optional=False)
        elif choice == "Y":
            checker.create_missing(report, create_optional=True)
        else:
            print("ℹ️ ایجاد خودکار لغو شد.")

    # کد خروجی بر اساس وضعیت
    if report.critical_missing:
        return 2  # خطای حیاتی
    elif report.missing > 0:
        return 1  # هشدار
    else:
        return 0  # موفقیت


if __name__ == "__main__":
    sys.exit(main())

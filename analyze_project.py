#!/usr/bin/env python3
"""
Frontend Project Structure Analyzer
تحلیل‌گر ساختار پروژه‌های React/TypeScript

این اسکریپت پروژه شما را اسکن می‌کند و:
- ساختار پوشه‌ها و فایل‌ها را شناسایی می‌کند
- کامپوننت‌ها، هوک‌ها، سرویس‌ها و تایپ‌ها را پیدا می‌کند
- وابستگی‌ها و imports را تحلیل می‌کند
- مشکلات معماری را تشخیص می‌دهد
- پیشنهادات بازسازی ارائه می‌دهد
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import argparse


class FrontendAnalyzer:
    """تحلیل‌گر ساختار پروژه فرانت‌اند"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.src_path = self.project_path / "src"
        
        # آمار پروژه
        self.stats = {
            "total_files": 0,
            "total_lines": 0,
            "components": [],
            "hooks": [],
            "services": [],
            "types": [],
            "utils": [],
            "styles": [],
            "other_files": []
        }
        
        # وابستگی‌ها
        self.dependencies = defaultdict(set)
        self.imports = defaultdict(set)
        
        # مشکلات و پیشنهادات
        self.issues = []
        self.recommendations = []
        
        # الگوهای شناسایی
        self.component_patterns = [
            r'\.tsx?$',
            r'function\s+[A-Z][a-zA-Z]*\s*\(',
            r'const\s+[A-Z][a-zA-Z]*\s*=\s*\(',
            r'class\s+[A-Z][a-zA-Z]*\s+extends\s+React\.Component',
        ]
        
    def analyze(self) -> Dict:
        """تحلیل کامل پروژه"""
        print(f"🔍 در حال تحلیل پروژه: {self.project_path}")
        print("=" * 60)
        
        if not self.src_path.exists():
            print(f"❌ پوشه src یافت نشد: {self.src_path}")
            return None
        
        # اسکن تمام فایل‌ها
        self._scan_files()
        
        # تحلیل ساختار پوشه‌ها
        self._analyze_directory_structure()
        
        # تحلیل imports
        self._analyze_imports()
        
        # شناسایی مشکلات
        self._identify_issues()
        
        # تولید پیشنهادات
        self._generate_recommendations()
        
        # تولید گزارش
        report = self._generate_report()
        
        print("✅ تحلیل کامل شد!")
        return report
    
    def _scan_files(self):
        """اسکن تمام فایل‌های پروژه"""
        print("📂 در حال اسکن فایل‌ها...")
        
        for file_path in self.src_path.rglob("*"):
            if file_path.is_file():
                self.stats["total_files"] += 1
                
                # شمارش خطوط
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        self.stats["total_lines"] += lines
                except:
                    pass
                
                # دسته‌بندی فایل
                relative_path = file_path.relative_to(self.src_path)
                file_info = {
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix
                }
                
                # شناسایی نوع فایل
                if self._is_component(file_path):
                    file_info["type"] = "component"
                    self.stats["components"].append(file_info)
                elif self._is_hook(file_path):
                    file_info["type"] = "hook"
                    self.stats["hooks"].append(file_info)
                elif self._is_service(file_path):
                    file_info["type"] = "service"
                    self.stats["services"].append(file_info)
                elif self._is_type(file_path):
                    file_info["type"] = "type"
                    self.stats["types"].append(file_info)
                elif self._is_util(file_path):
                    file_info["type"] = "util"
                    self.stats["utils"].append(file_info)
                elif self._is_style(file_path):
                    file_info["type"] = "style"
                    self.stats["styles"].append(file_info)
                else:
                    file_info["type"] = "other"
                    self.stats["other_files"].append(file_info)
    
    def _is_component(self, file_path: Path) -> bool:
        """بررسی آیا فایل یک کامپوننت است"""
        if file_path.suffix not in ['.tsx', '.jsx']:
            return False
        
        # بررسی مسیر
        path_str = str(file_path).lower()
        if 'components' in path_str:
            return True
        
        # بررسی محتوا
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # بررسی الگوهای کامپوننت
            if re.search(r'function\s+[A-Z][a-zA-Z]*\s*\(', content):
                return True
            if re.search(r'const\s+[A-Z][a-zA-Z]*\s*=\s*\(', content):
                return True
            if re.search(r'class\s+[A-Z][a-zA-Z]*\s+extends\s+React\.Component', content):
                return True
            if 'export default' in content and ('<' in content or 'return' in content):
                return True
        except:
            pass
        
        return False
    
    def _is_hook(self, file_path: Path) -> bool:
        """بررسی آیا فایل یک hook است"""
        path_str = str(file_path).lower()
        return 'hooks' in path_str or file_path.name.startswith('use')
    
    def _is_service(self, file_path: Path) -> bool:
        """بررسی آیا فایل یک سرویس است"""
        path_str = str(file_path).lower()
        return 'services' in path_str or 'api' in path_str
    
    def _is_type(self, file_path: Path) -> bool:
        """بررسی آیا فایل یک تایپ است"""
        path_str = str(file_path).lower()
        return 'types' in path_str or file_path.name.endswith('.d.ts')
    
    def _is_util(self, file_path: Path) -> bool:
        """بررسی آیا فایل یک utility است"""
        path_str = str(file_path).lower()
        return 'utils' in path_str or 'helpers' in path_str
    
    def _is_style(self, file_path: Path) -> bool:
        """بررسی آیا فایل یک استایل است"""
        return file_path.suffix in ['.css', '.scss', '.sass', '.less', '.module.css']
    
    def _analyze_directory_structure(self):
        """تحلیل ساختار پوشه‌ها"""
        print("📊 در حال تحلیل ساختار پوشه‌ها...")
        
        directories = defaultdict(list)
        
        for file_path in self.src_path.rglob("*"):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.src_path)
                parent = str(relative_path.parent)
                directories[parent].append(file_path.name)
        
        self.stats["directories"] = dict(directories)
        self.stats["directory_count"] = len(directories)
    
    def _analyze_imports(self):
        """تحلیل imports و dependencies"""
        print("🔗 در حال تحلیل وابستگی‌ها...")
        
        for category in ["components", "hooks", "services", "types", "utils"]:
            for file_info in self.stats[category]:
                file_path = self.src_path / file_info["path"]
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # استخراج imports
                    import_pattern = r'import\s+(?:.*?\s+from\s+)?[\'"]([^\'"]+)[\'"]'
                    imports = re.findall(import_pattern, content)
                    
                    for imp in imports:
                        if imp.startswith('.'):
                            # relative import
                            self.imports[file_info["path"]].add(imp)
                        else:
                            # external package
                            self.dependencies[imp].add(file_info["path"])
                except:
                    pass
    
    def _identify_issues(self):
        """شناسایی مشکلات معماری"""
        print("🔍 در حال شناسایی مشکلات...")
        
        # بررسی God Component
        for comp in self.stats["components"]:
            file_path = self.src_path / comp["path"]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                
                if lines > 300:
                    self.issues.append({
                        "severity": "CRITICAL",
                        "type": "GOD_COMPONENT",
                        "file": comp["path"],
                        "message": f"کامپوننت بسیار بزرگ ({lines} خط). باید به کامپوننت‌های کوچکتر تقسیم شود."
                    })
            except:
                pass
        
        # بررسی عدم وجود پوشه‌های استاندارد
        required_dirs = ["components", "hooks", "services", "types"]
        for dir_name in required_dirs:
            if not (self.src_path / dir_name).exists():
                self.issues.append({
                    "severity": "HIGH",
                    "type": "MISSING_DIRECTORY",
                    "message": f"پوشه استاندارد '{dir_name}' یافت نشد."
                })
        
        # بررسی hardcoded URLs
        for category in ["components", "hooks", "services"]:
            for file_info in self.stats[category]:
                file_path = self.src_path / file_info["path"]
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if re.search(r'http://localhost:\d+', content):
                        self.issues.append({
                            "severity": "MEDIUM",
                            "type": "HARDCODED_URL",
                            "file": file_info["path"],
                            "message": "URL hardcoded یافت شد. باید از environment variables استفاده شود."
                        })
                except:
                    pass
        
        # بررسی useEffect برای data fetching
        for file_info in self.stats["components"]:
            file_path = self.src_path / file_info["path"]
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'useEffect' in content and 'fetch' in content:
                    self.issues.append({
                        "severity": "MEDIUM",
                        "type": "USEEFFECT_FETCHING",
                        "file": file_info["path"],
                        "message": "استفاده از useEffect برای data fetching. پیشنهاد: استفاده از React Query یا SWR."
                    })
            except:
                pass
    
    def _generate_recommendations(self):
        """تولید پیشنهادات بازسازی"""
        print("💡 در حال تولید پیشنهادات...")
        
        # پیشنهاد بر اساس تعداد کامپوننت‌ها
        if len(self.stats["components"]) == 0:
            self.recommendations.append({
                "priority": "CRITICAL",
                "category": "STRUCTURE",
                "message": "هیچ کامپوننتی یافت نشد. احتمالاً تمام کد در یک فایل بزرگ است. باید به کامپوننت‌های کوچکتر تقسیم شود."
            })
        
        # پیشنهاد بر اساس تعداد هوک‌ها
        if len(self.stats["hooks"]) == 0:
            self.recommendations.append({
                "priority": "HIGH",
                "category": "LOGIC",
                "message": "هیچ custom hook یافت نشد. business logic را به هوک‌های سفارشی منتقل کنید."
            })
        
        # پیشنهاد بر اساس تعداد سرویس‌ها
        if len(self.stats["services"]) == 0:
            self.recommendations.append({
                "priority": "HIGH",
                "category": "API",
                "message": "هیچ service layer یافت نشد. تمام درخواست‌های API را به یک لایه سرویس منتقل کنید."
            })
        
        # پیشنهاد بر اساس تعداد تایپ‌ها
        if len(self.stats["types"]) == 0:
            self.recommendations.append({
                "priority": "MEDIUM",
                "category": "TYPES",
                "message": "هیچ type definition یافت نشد. TypeScript interfaces و types را در فایل‌های جداگانه تعریف کنید."
            })
        
        # پیشنهاد بر اساس مشکلات شناسایی شده
        critical_issues = [i for i in self.issues if i["severity"] == "CRITICAL"]
        if critical_issues:
            self.recommendations.append({
                "priority": "CRITICAL",
                "category": "REFACTORING",
                "message": f"{len(critical_issues)} مشکل بحرانی شناسایی شد. بازسازی فوری مورد نیاز است."
            })
        
        # پیشنهاد استفاده از state management
        if len(self.stats["components"]) > 10:
            self.recommendations.append({
                "priority": "MEDIUM",
                "category": "STATE",
                "message": "تعداد کامپوننت‌ها زیاد است. استفاده از state management (Redux, Zustand, Jotai) پیشنهاد می‌شود."
            })
    
    def _generate_report(self) -> Dict:
        """تولید گزارش نهایی"""
        print("📝 در حال تولید گزارش...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_path),
            "summary": {
                "total_files": self.stats["total_files"],
                "total_lines": self.stats["total_lines"],
                "components_count": len(self.stats["components"]),
                "hooks_count": len(self.stats["hooks"]),
                "services_count": len(self.stats["services"]),
                "types_count": len(self.stats["types"]),
                "utils_count": len(self.stats["utils"]),
                "styles_count": len(self.stats["styles"]),
                "directory_count": self.stats.get("directory_count", 0)
            },
            "components": self.stats["components"],
            "hooks": self.stats["hooks"],
            "services": self.stats["services"],
            "types": self.stats["types"],
            "utils": self.stats["utils"],
            "styles": self.stats["styles"],
            "issues": self.issues,
            "recommendations": self.recommendations,
            "dependencies": {k: list(v) for k, v in self.dependencies.items()},
            "imports": {k: list(v) for k, v in self.imports.items()}
        }
        
        return report
    
    def save_report(self, report: Dict, output_dir: str = None):
        """ذخیره گزارش به فایل"""
        if output_dir is None:
            output_dir = self.project_path
        
        output_path = Path(output_dir)
        
        # ذخیره JSON
        json_file = output_path / "project-analysis-report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"✅ گزارش JSON ذخیره شد: {json_file}")
        
        # ذخیره Markdown
        md_file = output_path / "project-analysis-report.md"
        self._save_markdown_report(report, md_file)
        print(f"✅ گزارش Markdown ذخیره شد: {md_file}")
    
    def _save_markdown_report(self, report: Dict, file_path: Path):
        """ذخیره گزارش به فرمت Markdown"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 گزارش تحلیل ساختار پروژه فرانت‌اند\n\n")
            f.write(f"**تاریخ تحلیل:** {report['timestamp']}\n")
            f.write(f"**مسیر پروژه:** `{report['project_path']}`\n\n")
            
            f.write("## 📈 آمار کلی\n\n")
            f.write("| دسته | تعداد |\n")
            f.write("|------|-------|\n")
            f.write(f"| کل فایل‌ها | {report['summary']['total_files']} |\n")
            f.write(f"| کل خطوط کد | {report['summary']['total_lines']} |\n")
            f.write(f"| کامپوننت‌ها | {report['summary']['components_count']} |\n")
            f.write(f"| هوک‌ها | {report['summary']['hooks_count']} |\n")
            f.write(f"| سرویس‌ها | {report['summary']['services_count']} |\n")
            f.write(f"| تایپ‌ها | {report['summary']['types_count']} |\n")
            f.write(f"| utilities | {report['summary']['utils_count']} |\n")
            f.write(f"| استایل‌ها | {report['summary']['styles_count']} |\n")
            f.write(f"| پوشه‌ها | {report['summary']['directory_count']} |\n\n")
            
            # کامپوننت‌ها
            if report['components']:
                f.write("## 🧩 کامپوننت‌ها\n\n")
                for comp in report['components']:
                    f.write(f"- `{comp['path']}`\n")
                f.write("\n")
            
            # هوک‌ها
            if report['hooks']:
                f.write("## 🪝 هوک‌ها\n\n")
                for hook in report['hooks']:
                    f.write(f"- `{hook['path']}`\n")
                f.write("\n")
            
            # سرویس‌ها
            if report['services']:
                f.write("## 🔌 سرویس‌ها\n\n")
                for service in report['services']:
                    f.write(f"- `{service['path']}`\n")
                f.write("\n")
            
            # مشکلات
            if report['issues']:
                f.write("## ⚠️ مشکلات شناسایی شده\n\n")
                for issue in report['issues']:
                    severity_emoji = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MEDIUM": "🟡",
                        "LOW": "🟢"
                    }.get(issue['severity'], "⚪")
                    
                    f.write(f"### {severity_emoji} {issue['severity']}: {issue['type']}\n")
                    if 'file' in issue:
                        f.write(f"**فایل:** `{issue['file']}`\n")
                    f.write(f"**توضیحات:** {issue['message']}\n\n")
            
            # پیشنهادات
            if report['recommendations']:
                f.write("## 💡 پیشنهادات بازسازی\n\n")
                for rec in report['recommendations']:
                    priority_emoji = {
                        "CRITICAL": "🔴",
                        "HIGH": "🟠",
                        "MEDIUM": "🟡",
                        "LOW": "🟢"
                    }.get(rec['priority'], "⚪")
                    
                    f.write(f"### {priority_emoji} {rec['priority']}: {rec['category']}\n")
                    f.write(f"{rec['message']}\n\n")


def main():
    """تابع اصلی"""
    parser = argparse.ArgumentParser(
        description="تحلیل‌گر ساختار پروژه‌های React/TypeScript"
    )
    parser.add_argument(
        "project_path",
        nargs="?",
        default=".",
        help="مسیر پروژه (پیش‌فرض: دایرکتوری فعلی)"
    )
    parser.add_argument(
        "-o", "--output",
        help="مسیر خروجی برای گزارش‌ها (پیش‌فرض: ریشه پروژه)"
    )
    
    args = parser.parse_args()
    
    # ایجاد تحلیل‌گر
    analyzer = FrontendAnalyzer(args.project_path)
    
    # تحلیل پروژه
    report = analyzer.analyze()
    
    if report:
        # ذخیره گزارش
        analyzer.save_report(report, args.output)
        
        # چاپ خلاصه
        print("\n" + "=" * 60)
        print("📊 خلاصه نتایج:")
        print("=" * 60)
        print(f"✅ کل فایل‌ها: {report['summary']['total_files']}")
        print(f"✅ کل خطوط کد: {report['summary']['total_lines']}")
        print(f"✅ کامپوننت‌ها: {report['summary']['components_count']}")
        print(f"✅ هوک‌ها: {report['summary']['hooks_count']}")
        print(f"✅ سرویس‌ها: {report['summary']['services_count']}")
        print(f"✅ مشکلات: {len(report['issues'])}")
        print(f"✅ پیشنهادات: {len(report['recommendations'])}")
        print("=" * 60)
        print("\n📁 گزارش‌ها ذخیره شدند:")
        print("   - project-analysis-report.json")
        print("   - project-analysis-report.md")
        print("\n✨ تحلیل کامل شد!")


if __name__ == "__main__":
    main()
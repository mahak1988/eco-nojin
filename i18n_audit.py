#!/usr/bin/env python3
"""
i18n Audit and Sync Script
شناسایی و همگام‌سازی ترجمه‌های چندزبانه در پروژه Econojin
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
import argparse

class I18nAuditor:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.i18n_dirs = []
        self.languages: Set[str] = set()
        self.translations: Dict[str, Dict[str, str]] = {}
        self.all_keys: Set[str] = set()
        self.missing_keys: Dict[str, List[str]] = defaultdict(list)
        
    def find_i18n_files(self):
        """پیدا کردن تمام فایل‌های i18n در پروژه"""
        print("🔍 در حال جستجوی فایل‌های i18n...")
        
        # جستجو در مسیرهای احتمالی
        search_patterns = [
            "**/i18n/**/*.json",
            "**/i18n/**/*.ts",
            "**/locales/**/*.json",
            "**/locales/**/*.ts",
            "**/translations/**/*.json",
            "**/*i18n*.ts",
        ]
        
        for pattern in search_patterns:
            files = list(self.project_root.glob(pattern))
            for file in files:
                if file.is_file():
                    self.i18n_dirs.append(file)
                    print(f"  ✓ یافت شد: {file.relative_to(self.project_root)}")
        
        if not self.i18n_dirs:
            print("⚠️  هیچ فایل i18n یافت نشد!")
        else:
            print(f"\n📁 مجموعاً {len(self.i18n_dirs)} فایل i18n یافت شد")
    
    def extract_language_from_filename(self, filename: str) -> str:
        """استخراج کد زبان از نام فایل"""
        # الگوهای رایج: fa.json, en.ts, en-US.json, etc.
        patterns = [
            r'^([a-z]{2})(?:\.|-)',  # fa.json, fa-IR.json
            r'^([a-z]{2}_[A-Z]{2})',  # fa_IR.json
            r'([a-z]{2})\.json$',     # fa.json
            r'([a-z]{2})\.ts$',       # fa.ts
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                return match.group(1)
        
        return filename.split('.')[0]  # fallback
    
    def flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
        """تخت کردن دیکشنری تودرتو"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, str(v)))
        return dict(items)
    
    def parse_i18n_file(self, file_path: Path) -> Dict[str, str]:
        """تجزیه فایل i18n و استخراج کلید-مقدار"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # اگر JSON است
            if file_path.suffix == '.json':
                data = json.loads(content)
                return self.flatten_dict(data)
            
            # اگر TypeScript است (استخراج شیء export شده)
            elif file_path.suffix == '.ts':
                # استخراج محتوای بین {} یا const/export
                # این یک ساده‌سازی است - برای فایل‌های پیچیده‌تر نیاز به parser واقعی داریم
                json_match = re.search(r'export\s+(?:const|default)\s+\w+\s*=\s*({[\s\S]*?});', content)
                if json_match:
                    json_str = json_match.group(1)
                    # حذف کامنت‌ها
                    json_str = re.sub(r'//.*?$', '', json_str, flags=re.MULTILINE)
                    json_str = re.sub(r'/\*[\s\S]*?\*/', '', json_str)
                    
                    # تلاش برای parse کردن (ممکن است نیاز به اصلاح داشته باشد)
                    try:
                        data = json.loads(json_str)
                        return self.flatten_dict(data)
                    except json.JSONDecodeError:
                        print(f"  ⚠️  خطا در تجزیه JSON در {file_path}")
                        return {}
            
            return {}
            
        except Exception as e:
            print(f"  ❌ خطا در خواندن {file_path}: {e}")
            return {}
    
    def analyze_translations(self):
        """تحلیل کامل ترجمه‌ها"""
        print("\n📊 در حال تحلیل ترجمه‌ها...")
        
        for file_path in self.i18n_dirs:
            lang = self.extract_language_from_filename(file_path.name)
            self.languages.add(lang)
            
            translations = self.parse_i18n_file(file_path)
            self.translations[lang] = translations
            
            # جمع‌آوری تمام کلیدها
            self.all_keys.update(translations.keys())
            
            print(f"  ✓ {lang}: {len(translations)} کلید")
        
        print(f"\n🌍 زبان‌های شناسایی‌شده: {', '.join(sorted(self.languages))}")
        print(f"🔑 مجموع کلیدهای یکتا: {len(self.all_keys)}")
    
    def find_missing_keys(self):
        """شناسایی کلیدهای گمشده در هر زبان"""
        print("\n🔍 در حال شناسایی کلیدهای گمشده...")
        
        for lang in self.languages:
            lang_keys = set(self.translations[lang].keys())
            missing = self.all_keys - lang_keys
            
            if missing:
                self.missing_keys[lang] = sorted(list(missing))
                print(f"  ⚠️  {lang}: {len(missing)} کلید گمشده")
            else:
                print(f"  ✓ {lang}: کامل")
    
    def generate_report(self, output_dir: Path):
        """تولید گزارش جامع"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # گزارش JSON
        report_data = {
            "summary": {
                "total_languages": len(self.languages),
                "languages": sorted(list(self.languages)),
                "total_keys": len(self.all_keys),
                "total_missing": sum(len(keys) for keys in self.missing_keys.values())
            },
            "missing_keys": {lang: keys for lang, keys in self.missing_keys.items()},
            "language_coverage": {
                lang: {
                    "total_keys": len(self.translations[lang]),
                    "coverage_percent": round(len(self.translations[lang]) / len(self.all_keys) * 100, 2) if self.all_keys else 100,
                    "missing_count": len(self.missing_keys.get(lang, []))
                }
                for lang in self.languages
            }
        }
        
        json_report = output_dir / "i18n_audit.json"
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"\n📄 گزارش JSON ذخیره شد: {json_report}")
        
        # گزارش Markdown
        md_report = output_dir / "i18n_audit.md"
        with open(md_report, 'w', encoding='utf-8') as f:
            f.write("# گزارش وضعیت i18n پروژه Econojin\n\n")
            f.write("## خلاصه\n\n")
            f.write(f"- **تعداد زبان‌ها:** {len(self.languages)}\n")
            f.write(f"- **زبان‌های موجود:** {', '.join(sorted(self.languages))}\n")
            f.write(f"- **مجموع کلیدهای یکتا:** {len(self.all_keys)}\n")
            f.write(f"- **مجموع کلیدهای گمشده:** {report_data['summary']['total_missing']}\n\n")
            
            f.write("## پوشش هر زبان\n\n")
            f.write("| زبان | تعداد کلیدها | درصد پوشش | کلیدهای گمشده |\n")
            f.write("|------|-------------|-----------|---------------|\n")
            
            for lang in sorted(self.languages):
                coverage = report_data['language_coverage'][lang]
                f.write(f"| {lang} | {coverage['total_keys']} | {coverage['coverage_percent']}% | {coverage['missing_count']} |\n")
            
            f.write("\n## کلیدهای گمشده به تفکیک زبان\n\n")
            
            for lang in sorted(self.missing_keys.keys()):
                missing = self.missing_keys[lang]
                f.write(f"### {lang} ({len(missing)} کلید گمشده)\n\n")
                f.write("```\n")
                for key in missing[:20]:  # نمایش 20 مورد اول
                    f.write(f"{key}\n")
                if len(missing) > 20:
                    f.write(f"... و {len(missing) - 20} مورد دیگر\n")
                f.write("```\n\n")
        
        print(f"📄 گزارش Markdown ذخیره شد: {md_report}")
    
    def sync_missing_keys(self, output_dir: Path):
        """تکمیل کلیدهای گمشده در فایل‌های ترجمه"""
        print("\n🔧 در حال تکمیل کلیدهای گمشده...")
        
        synced_dir = output_dir / "synced_translations"
        synced_dir.mkdir(parents=True, exist_ok=True)
        
        for lang in self.languages:
            # کپی ترجمه‌های موجود
            lang_translations = self.translations[lang].copy()
            
            # افزودن کلیدهای گمشده با مقدار خالی
            missing = self.missing_keys.get(lang, [])
            for key in missing:
                lang_translations[key] = ""  # مقدار خالی برای ترجمه
            
            # تبدیل به ساختار درختی
            nested = self.unflatten_dict(lang_translations)
            
            # ذخیره به فایل
            output_file = synced_dir / f"{lang}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(nested, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ {lang}: {len(missing)} کلید اضافه شد")
        
        print(f"\n📁 فایل‌های همگام‌شده در: {synced_dir}")
    
    def unflatten_dict(self, flat_dict: Dict[str, str], sep: str = '.') -> Dict[str, Any]:
        """تبدیل دیکشنری تخت به درختی"""
        result = {}
        for key, value in flat_dict.items():
            parts = key.split(sep)
            current = result
            
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = value
        
        return result

def main():
    parser = argparse.ArgumentParser(description="I18n Audit and Sync Tool")
    parser.add_argument("--project-root", default=".", help="مسیر ریشه پروژه")
    parser.add_argument("--output", default="i18n_report", help="مسیر خروجی گزارش‌ها")
    parser.add_argument("--sync", action="store_true", help="تکمیل کلیدهای گمشده")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🌍 I18n Audit and Sync Tool")
    print("=" * 60)
    
    auditor = I18nAuditor(args.project_root)
    
    # مراحل اجرا
    auditor.find_i18n_files()
    auditor.analyze_translations()
    auditor.find_missing_keys()
    
    # تولید گزارش
    output_dir = Path(args.output)
    auditor.generate_report(output_dir)
    
    # همگام‌سازی در صورت درخواست
    if args.sync:
        auditor.sync_missing_keys(output_dir)
    
    print("\n" + "=" * 60)
    print("✅ تحلیل i18n کامل شد!")
    print("=" * 60)

if __name__ == "__main__":
    main()
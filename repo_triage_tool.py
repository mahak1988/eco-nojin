#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repo Triage & Quarantine Tool v1.0
توضیحات: شناسایی، دسته‌بندی و انتقال ایمن فایل‌های زائد به پوشه قرنطینه.
هشدار: این ابزار در حالت پیش‌فرض Dry-Run است و هیچ فایلی را حذف یا منتقل نمی‌کند.
"""

import os
import re
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

# ==============================================================================
# 1. Configuration & Patterns (الگوهای تشخیص زوائد)
# ==============================================================================
IGNORE_DIRS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', '.idea', '.vscode', '_QUARANTINE'}

# الگوهای Regex برای شناسایی اسکریپت‌های یک‌بار مصرف (Junk Scripts)
JUNK_SCRIPT_PATTERNS = [
    r'^fix_.*\.py$', r'^create_.*\.py$', r'^patch_.*\.py$', r'^diagnose_.*\.py$',
    r'^smart_.*\.py$', r'^auto_.*\.py$', r'^add_.*\.py$', r'^upgrade_.*\.py$',
    r'^rewrite_.*\.py$', r'^merge_.*\.py$', r'^finalize_.*\.py$', r'^force_.*\.py$',
    r'^generate_.*\.py$', r'^verify_.*\.py$', r'^integrate_.*\.py$', r'^setup_.*\.py$',
    r'^run-.*\.ps1$', r'^start.*\.bat$', r'^start.*\.ps1$'
]

# الگوهای نام پوشه‌ها و فایل‌های بک‌آپ تکراری (Redundant Backups)
BACKUP_DIR_PATTERNS = [
    r'.*backup.*', r'.*archive.*', r'.*legacy.*', r'_cleanup_.*', r'_archived_.*'
]

# پسوندهای فایل‌های بک‌آپ محلی (Local Backup Extensions)
LOCAL_BACKUP_EXTS = {'.bak', '.backup', '.full.backup', '.original', '.broken', '.tmp', '.swp'}

# پسوندهای فایل‌های گزارش و لاگ موقت (Temp Reports)
TEMP_REPORT_EXTS = {'.log', '.txt'}
TEMP_REPORT_NAMES = {'analysis_report.json', 'analysis_report.md', 'surgeon_report.md', 'triage_report.md', 'EcoNojin_Analysis_Report.md', 'PROJECT_COMPARISON_REPORT.md'}

# فایل‌های حساس (Secrets)
SENSITIVE_FILES = {'.env', '.env.local', 'credentials.json', 'secrets.yaml'}
SENSITIVE_CONFIG_PATTERNS = [r'^config\.py$']

# ==============================================================================
# 2. Core Modules
# ==============================================================================

class TriageScanner:
    """اسکنر و دسته‌بندی‌کننده فایل‌ها بر اساس الگوها"""
    
    @staticmethod
    def scan(root_path: Path) -> Dict[str, List[Path]]:
        categories = {
            'junk_scripts': [],
            'redundant_backups': [],
            'local_backups': [],
            'temp_reports': [],
            'sensitive_files': []
        }
        
        compiled_junk_patterns = [re.compile(p, re.IGNORECASE) for p in JUNK_SCRIPT_PATTERNS]
        compiled_backup_dir_patterns = [re.compile(p, re.IGNORECASE) for p in BACKUP_DIR_PATTERNS]
        compiled_config_patterns = [re.compile(p, re.IGNORECASE) for p in SENSITIVE_CONFIG_PATTERNS]

        for dirpath, dirnames, filenames in os.walk(root_path):
            # Pruning: جلوگیری از ورود به دایرکتوری‌های سیستمی و قرنطینه
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]
            
            current_dir = Path(dirpath)
            dir_name = current_dir.name
            
            # بررسی پوشه‌های بک‌آپ (انتقال کل پوشه)
            if any(p.match(dir_name) for p in compiled_backup_dir_patterns) and current_dir != root_path:
                categories['redundant_backups'].append(current_dir)
                dirnames[:] = [] # جلوگیری از اسکن زیرمجموعه‌های این پوشه
                continue

            for filename in filenames:
                filepath = current_dir / filename
                ext = ''.join(filepath.suffixes).lower() # برای پسوندهای مرکب مثل .full.backup
                
                # 1. اسکریپت‌های زائد
                if any(p.match(filename) for p in compiled_junk_patterns):
                    categories['junk_scripts'].append(filepath)
                    continue
                
                # 2. فایل‌های بک‌آپ محلی
                if any(filename.endswith(e) for e in LOCAL_BACKUP_EXTS):
                    categories['local_backups'].append(filepath)
                    continue
                
                # 3. فایل‌های گزارش موقت (فقط در ریشه پروژه)
                if ext in TEMP_REPORT_EXTS or filename in TEMP_REPORT_NAMES:
                    if current_dir == root_path:
                        categories['temp_reports'].append(filepath)
                    continue
                
                # 4. فایل‌های حساس
                if filename in SENSITIVE_FILES or any(p.match(filename) for p in compiled_config_patterns):
                    categories['sensitive_files'].append(filepath)

        return categories


class QuarantineManager:
    """مدیریت انتقال ایمن فایل‌ها به قرنطینه"""
    
    @staticmethod
    def move_to_quarantine(root_path: Path, categories: Dict[str, List[Path]], execute: bool) -> Dict[str, int]:
        quarantine_base = root_path / '_QUARANTINE'
        stats = {'moved': 0, 'errors': 0}
        
        if execute:
            quarantine_base.mkdir(exist_ok=True)
            
        for category, items in categories.items():
            if category == 'sensitive_files':
                continue # فایل‌های حساس منتقل نمی‌شوند، فقط Sanitize می‌شوند
                
            for item_path in items:
                try:
                    # حفظ ساختار نسبی در قرنطینه
                    rel_path = item_path.relative_to(root_path)
                    dest_path = quarantine_base / category / rel_path
                    
                    if execute:
                        dest_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(item_path), str(dest_path))
                        stats['moved'] += 1
                    else:
                        stats['moved'] += 1 # در حالت Dry-run فقط می‌شماریم
                        
                except Exception as e:
                    print(f"❌ خطا در انتقال {item_path}: {e}")
                    stats['errors'] += 1
                    
        return stats


class SecretSanitizer:
    """خالی‌سازی ایمن فایل‌های حساس"""
    
    @staticmethod
    def sanitize(root_path: Path, sensitive_files: List[Path], execute: bool) -> int:
        sanitized_count = 0
        placeholder = "REDACTED_BY_TRIAGE_TOOL"
        
        for filepath in sensitive_files:
            if not filepath.exists():
                continue
                
            try:
                if execute:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        for line in lines:
                            # جایگزینی ساده مقادیر بعد از = یا :
                            if '=' in line and not line.strip().startswith('#'):
                                key = line.split('=', 1)[0]
                                f.write(f"{key}={placeholder}\n")
                            elif ':' in line and not line.strip().startswith('#'):
                                key = line.split(':', 1)[0]
                                f.write(f"{key}: {placeholder}\n")
                            else:
                                f.write(line)
                    sanitized_count += 1
                else:
                    sanitized_count += 1
            except Exception as e:
                print(f"⚠️ خطا در Sanitize فایل {filepath}: {e}")
                
        return sanitized_count


class TriageReport:
    """تولید گزارش نهایی"""
    
    @staticmethod
    def generate(root_path: Path, categories: Dict[str, List[Path]], stats: Dict, sanitized: int, executed: bool, out_path: Path):
        lines = []
        status = "✅ اجرا شده (Execute Mode)" if executed else "⚠️ آزمایشی (Dry-Run Mode)"
        
        lines.extend([
            f"# 🚑 گزارش تریاژ و قرنطینه پروژه",
            f"**تاریخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**وضعیت:** {status}",
            "", "---", "",
            "## 📊 خلاصه آماری",
            f"- **اسکریپت‌های یک‌بار مصرف شناسایی‌شده:** `{len(categories['junk_scripts'])}`",
            f"- **پوشه‌ها/فایل‌های بک‌آپ تکراری:** `{len(categories['redundant_backups'])}`",
            f"- **فایل‌های بک‌آپ محلی:** `{len(categories['local_backups'])}`",
            f"- **فایل‌های گزارش موقت:** `{len(categories['temp_reports'])}`",
            f"- **فایل‌های حساس (Sanitize شده):** `{sanitized}`",
            "",
            f"- **تعداد کل موارد منتقل‌شده به قرنطینه:** `{stats['moved']}`",
            f"- **تعداد خطاها:** `{stats['errors']}`",
            "", "---", ""
        ])
        
        if not executed:
            lines.extend([
                "## ⚠️ توجه: این یک گزارش آزمایشی (Dry-Run) است!",
                "هیچ فایلی منتقل یا ویرایش نشده است. برای اجرای عملیات، دستور را با فلگ `--execute` اجرا کنید.",
                "", "---", ""
            ])
        else:
            lines.extend([
                "## ✅ عملیات با موفقیت انجام شد",
                f"تمامی موارد زائد به پوشه `{root_path / '_QUARANTINE'}` منتقل شدند.",
                "شما می‌توانید این پوشه را بررسی کرده و در نهایت به صورت دستی حذف کنید.",
                "", "---", ""
            ])
            
        for category, items in categories.items():
            if not items:
                continue
                
            lines.append(f"### 📁 {category.replace('_', ' ').title()}")
            for item in items[:15]: # نمایش حداکثر 15 مورد برای جلوگیری از شلوغی
                try:
                    rel = item.relative_to(root_path)
                    lines.append(f"- `{rel}`")
                except ValueError:
                    lines.append(f"- `{item}`")
            if len(items) > 15:
                lines.append(f"- *... و {len(items) - 15} مورد دیگر*")
            lines.append("")
            
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))


# ==============================================================================
# 3. Main Orchestrator
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="ابزار تریاژ و قرنطینه فایل‌های زائد")
    parser.add_argument("path", type=str, nargs='?', default=".", help="مسیر پروژه")
    parser.add_argument("--execute", action="store_true", help="اجرای عملیات انتقال (پیش‌فرض: Dry-Run)")
    args = parser.parse_args()
    
    root_path = Path(args.path).resolve()
    if not root_path.is_dir():
        print(f"❌ خطا: مسیر '{root_path}' معتبر نیست.")
        return

    print(f"🔍 شروع تریاژ پروژه: {root_path}")
    print(f"⚙️ حالت اجرا: {'انتقال واقعی (Execute)' if args.execute else 'آزمایشی (Dry-Run)'}")
    
    print("⏳ [1/3] اسکن و دسته‌بندی فایل‌ها...")
    categories = TriageScanner.scan(root_path)
    
    print("⏳ [2/3] انتقال به قرنطینه...")
    stats = QuarantineManager.move_to_quarantine(root_path, categories, args.execute)
    
    print("⏳ [3/3] ایمن‌سازی فایل‌های حساس...")
    sanitized = SecretSanitizer.sanitize(root_path, categories['sensitive_files'], args.execute)
    
    report_path = root_path / "triage_report.md"
    TriageReport.generate(root_path, categories, stats, sanitized, args.execute, report_path)
    
    print("\n✅ تریاژ به پایان رسید!")
    print(f"📄 گزارش کامل: '{report_path}'")
    if not args.execute:
        print("👈 برای انتقال واقعی فایل‌ها به قرنطینه، دستور زیر را اجرا کنید:")
        print(f"   python {Path(__file__).name} --execute")

if __name__ == "__main__":
    main()
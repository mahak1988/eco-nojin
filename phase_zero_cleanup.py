import os
import re
import shutil
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

class PhaseZeroAuditor:
    def __init__(self, project_path: str, archive_path: str):
        self.project_path = Path(project_path).resolve()
        self.archive_path = Path(archive_path).resolve()
        self.backup_pattern = re.compile(r'^_backup_.*|^_QUARANTINE$')
        
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "git_status": "Unknown",
            "identified_backups": [],
            "total_wasted_space_mb": 0.0,
            "migration_status": "Pending",
            "critical_warnings": []
        }

    def step_1_git_safety_check(self) -> bool:
        """گام اول: اطمینان از پاک بودن مخزن Git و کامیت شدن تمام تغییرات زنده"""
        print("🛡️ [گام ۱] بررسی وضعیت ایمنی مخزن Git...")
        try:
            # بررسی وجود تغییرات کامیت نشده
            result = subprocess.run(
                ['git', 'status', '--porcelain'], 
                cwd=self.project_path, 
                capture_output=True, text=True, check=True
            )
            if result.stdout.strip():
                self.report["git_status"] = "DIRTY"
                self.report["critical_warnings"].append("⛔ مخزن Git دارای تغییرات کامیت نشده است. اجرای فاز صفر متوقف شد.")
                return False
            
            self.report["git_status"] = "CLEAN"
            print("✅ مخزن Git پاک است. تمام کدهای زنده ایمن هستند.")
            return True
        except subprocess.CalledProcessError:
            self.report["git_status"] = "NOT_A_GIT_REPO"
            self.report["critical_warnings"].append("⛔ مسیر پروژه یک مخزن Git معتبر نیست. ریسک انتقال بدون بک‌آپ بالاست.")
            return False

    def step_2_footprint_analysis(self) -> None:
        """گام دوم: شناسایی پوشه‌های هدف و محاسبه حجم منابع اشغال شده"""
        print("\n📊 [گام ۲] تحلیل ردپای منابع و شناسایی پوشه‌های بک‌آپ...")
        total_size = 0
        
        for item in self.project_path.iterdir():
            if item.is_dir() and self.backup_pattern.match(item.name):
                # محاسبه حجم پوشه
                dir_size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                total_size += dir_size
                
                self.report["identified_backups"].append({
                    "name": item.name,
                    "size_mb": round(dir_size / (1024 * 1024), 2),
                    "path": str(item)
                })
                
        self.report["total_wasted_space_mb"] = round(total_size / (1024 * 1024), 2)
        print(f"✅ تعداد {len(self.report['identified_backups'])} پوشه بک‌آپ شناسایی شد.")
        print(f"✅ حجم منابع اشغال شده (ردپای دیسک): {self.report['total_wasted_space_mb']} مگابایت")

    def step_3_safe_migration(self) -> None:
        """گام سوم: انتقال ایمن به آرشیو خارج از چرخه توسعه (بدون حذف فیزیکی)"""
        if self.report["git_status"] != "CLEAN":
            print("\n⛔ به دلیل عدم ایمنی مخزن Git، گام سوم (انتقال) اجرا نخواهد شد.")
            return

        if not self.report["identified_backups"]:
            print("\n✅ هیچ پوشه بک‌آپی برای انتقال یافت نشد. پروژه پاک است.")
            return

        print(f"\n📦 [گام ۳] شروع عملیات انتقال ایمن به آرشیو: {self.archive_path}")
        self.archive_path.mkdir(parents=True, exist_ok=True)
        
        migrated_count = 0
        for backup in self.report["identified_backups"]:
            src = Path(backup["path"])
            # افزودن timestamp به نام آرشیو برای جلوگیری از تداخل
            dest_name = f"{src.name}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            dest = self.archive_path / dest_name
            
            try:
                shutil.move(str(src), str(dest))
                migrated_count += 1
            except Exception as e:
                self.report["critical_warnings"].append(f"خطا در انتقال {src.name}: {e}")

        self.report["migration_status"] = f"SUCCESS ({migrated_count}/{len(self.report['identified_backups'])} migrated)"
        print(f"✅ عملیات انتقال با موفقیت به پایان رسید. ریشه پروژه اکنون آزاد است.")

    def execute_phase_zero(self) -> None:
        """اجرای ترتیبی و ایمن فاز صفر"""
        print("="*70)
        print("🚀 شروع عملیات فاز صفر: بحران‌زدایی زیرساخت (Phase Zero Execution)")
        print("="*70)
        
        if not self.step_1_git_safety_check():
            self._print_final_report()
            return
            
        self.step_2_footprint_analysis()
        
        # در محیط تولیدی، اینجا یک تاییدیه نهایی از کاربر گرفته می‌شود.
        # برای اتوماسیون کامل، در صورت پاک بودن Git، مستقیماً منتقل می‌کنیم.
        self.step_3_safe_migration()
        
        self._print_final_report()

    def _print_final_report(self) -> None:
        print("\n" + "="*70)
        print("📋 گزارش نهایی اجرای فاز صفر")
        print("="*70)
        for key, value in self.report.items():
            print(f"• {key}: {value}")
        print("="*70)
        
        # ذخیره گزارش
        report_file = self.project_path / "phase_zero_audit_report.json"
        import json
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)
        print(f"✅ گزارش ممیزی در فایل '{report_file.name}' ذخیره شد.\n")

if __name__ == "__main__":
    # مسیر پروژه فعلی
    PROJECT_ROOT = r"D:\econojin.com"
    # مسیر آرشیو امن (خارج از ریشه پروژه، اما در همان درایو برای سرعت انتقال)
    SECURE_ARCHIVE = r"D:\EcoJin_Legacy_Archive_2026"
    
    auditor = PhaseZeroAuditor(PROJECT_ROOT, SECURE_ARCHIVE)
    auditor.execute_phase_zero()
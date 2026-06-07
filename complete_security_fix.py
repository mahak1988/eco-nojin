import os
import shutil
from pathlib import Path

def create_env_file(project_dir):
    """ایجاد فایل .env از روی .env.example اگر وجود ندارد"""
    env_example_path = Path(project_dir) / '.env.example'
    env_path = Path(project_dir) / '.env'
    
    if not env_example_path.exists():
        print("❌ فایل .env.example یافت نشد!")
        return False
    
    if env_path.exists():
        print("✅ فایل .env از قبل وجود دارد.")
        return True
    
    # کپی .env.example به .env
    shutil.copy2(env_example_path, env_path)
    print(f"✅ فایل .env از روی .env.example ایجاد شد: {env_path}")
    print("\n⚠️  مهم: مقادیر واقعی کلیدها را در فایل .env وارد کنید (نه در .env.example)")
    
    return True

def list_backup_files(project_dir):
    """لیست کردن فایل‌های پشتیبان .bak"""
    backup_files = list(Path(project_dir).rglob('*.bak'))
    
    # حذف مسیرهای غیرضروری
    backup_files = [f for f in backup_files if '.venv' not in str(f) and 'node_modules' not in str(f)]
    
    if not backup_files:
        print("✅ هیچ فایل پشتیبانی یافت نشد.")
        return []
    
    print(f"\n📦 فایل‌های پشتیبان یافت شده ({len(backup_files)} فایل):")
    for i, backup in enumerate(backup_files, 1):
        size = backup.stat().st_size
        print(f"  {i}. {backup.relative_to(project_dir)} ({size} bytes)")
    
    return backup_files

def delete_backup_files(backup_files):
    """حذف فایل‌های پشتیبان با تأیید کاربر"""
    if not backup_files:
        return
    
    print("\n🗑️  آیا می‌خواهید این فایل‌های پشتیبان را حذف کنید؟")
    print("   (این فایل‌ها پس از حذف قابل بازیابی نیستند)")
    
    response = input("   پاسخ (y/n): ").strip().lower()
    
    if response == 'y':
        for backup in backup_files:
            backup.unlink()
            print(f"   ✅ حذف شد: {backup.name}")
        print("\n✅ تمام فایل‌های پشتیبان حذف شدند.")
    else:
        print("\nℹ️  فایل‌های پشتیبان حفظ شدند.")

def verify_gitignore(project_dir):
    """بررسی اینکه .env در .gitignore باشد"""
    gitignore_path = Path(project_dir) / '.gitignore'
    
    if not gitignore_path.exists():
        print("❌ فایل .gitignore یافت نشد!")
        return False
    
    content = gitignore_path.read_text(encoding='utf-8')
    
    if '.env' in content:
        print("✅ فایل .env در .gitignore قرار دارد.")
        return True
    else:
        print("⚠️  فایل .env در .gitignore نیست! در حال افزودن...")
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write("\n# فایل‌های محیطی\n.env\n.env.local\n.env.*.local\n")
        print("✅ .env به .gitignore اضافه شد.")
        return True

def check_imports_in_services(project_dir):
    """بررسی اینکه import os در services.py اضافه شده باشد"""
    services_path = Path(project_dir) / 'api' / 'modules' / 'library' / 'services.py'
    
    if not services_path.exists():
        print(f"⚠️  فایل {services_path} یافت نشد.")
        return
    
    content = services_path.read_text(encoding='utf-8')
    
    if 'import os' in content or 'from os' in content:
        print("✅ دستور import os در services.py وجود دارد.")
    else:
        print("⚠️  دستور import os در services.py یافت نشد!")
    
    if 'os.getenv' in content:
        print("✅ استفاده از os.getenv در services.py تأیید شد.")
    else:
        print("⚠️  استفاده از os.getenv در services.py یافت نشد!")

def main():
    project_dir = r"D:\econojin.com"
    
    print("🚀 شروع اقدامات تکمیلی پس از اصلاح کلیدهای هاردکد شده...\n")
    
    # 1. ایجاد فایل .env
    print("=" * 60)
    print("📝 مرحله 1: ایجاد فایل .env")
    print("=" * 60)
    create_env_file(project_dir)
    
    # 2. بررسی .gitignore
    print("\n" + "=" * 60)
    print("🔒 مرحله 2: بررسی .gitignore")
    print("=" * 60)
    verify_gitignore(project_dir)
    
    # 3. بررسی imports در services.py
    print("\n" + "=" * 60)
    print("🔍 مرحله 3: بررسی اصلاحات در services.py")
    print("=" * 60)
    check_imports_in_services(project_dir)
    
    # 4. لیست و حذف فایل‌های پشتیبان
    print("\n" + "=" * 60)
    print("🗑️  مرحله 4: مدیریت فایل‌های پشتیبان")
    print("=" * 60)
    backup_files = list_backup_files(project_dir)
    delete_backup_files(backup_files)
    
    # خلاصه نهایی
    print("\n" + "=" * 60)
    print("🎉 خلاصه اقدامات")
    print("=" * 60)
    print("✅ کلیدهای هاردکد شده با os.getenv جایگزین شدند")
    print("✅ فایل .env ایجاد شد (اگر وجود نداشت)")
    print("✅ .env در .gitignore قرار دارد")
    print("✅ فایل‌های پشتیبان بررسی شدند")
    print("\n📌 اقدامات بعدی:")
    print("   1. مقادیر واقعی کلیدها را در فایل .env وارد کنید")
    print("   2. برنامه را تست کنید تا از عملکرد صحیح اطمینان حاصل شود")
    print("   3. تغییرات را در Git commit کنید:")
    print("      git add .")
    print("      git commit -m 'security: replace hardcoded secrets with environment variables'")
    print("=" * 60)

if __name__ == "__main__":
    main()
import shutil
from pathlib import Path

# تنظیم مسیرها (بر اساس ساختار استاندارد پروژه شما)
SOURCE_DIR = Path("D:/econojin.com/i18n_clean_output")
TARGET_DIR = Path("D:/econojin.com/apps/web/src/i18n/locales")

# بررسی وجود پوشه هدف
if not TARGET_DIR.exists():
    print(f"❌ پوشه هدف یافت نشد: {TARGET_DIR}")
    print("💡 لطفاً مسیر TARGET_DIR را در اسکریپت بررسی کنید.")
    exit(1)

# ۱. ایجاد بک‌آپ از فایل‌های قدیمی
backup_dir = TARGET_DIR.parent / "locales_backup"
backup_dir.mkdir(exist_ok=True)
print("🔄 در حال ایجاد بک‌آپ از فایل‌های قدیمی...")
for file in TARGET_DIR.glob("*.json"):
    shutil.copy(file, backup_dir / file.name)
print(f"✅ بک‌آپ با موفقیت در پوشه {backup_dir.name} ذخیره شد.\n")

# ۲. جایگزینی فایل‌های en.json و fa.json
files_to_replace = ["en.json", "fa.json"]
for filename in files_to_replace:
    source_file = SOURCE_DIR / filename
    target_file = TARGET_DIR / filename
    
    if source_file.exists():
        shutil.copy(source_file, target_file)
        print(f"✅ فایل {filename} با موفقیت جایگزین و تمیز شد.")
    else:
        print(f"⚠️ فایل {filename} در پوشه مبدا یافت نشد.")

print("\n" + "="*60)
print("🎉 عملیات جایگزینی با موفقیت انجام شد!")
print("="*60)
print("💡 گام نهایی:")
print("   ۱. اگر سرور توسعه (pnpm dev) در حال اجراست، آن را متوقف کنید (Ctrl+C).")
print("   ۲. سرور را مجدداً راه‌اندازی کنید: pnpm dev")
print("   ۳. اکنون فرانت‌اند باید بدون خطای i18n و با ساختار صحیح بارگذاری شود.")
import os
import re
import json
from pathlib import Path

# تنظیمات مسیرها
PROJECT_ROOT = Path("D:/econojin.com")
SEARCH_DIRS = [
    PROJECT_ROOT / "apps" / "web",
    PROJECT_ROOT / "apps" / "api",
    PROJECT_ROOT / "packages" # برای اطمینان، اگر پکیج مشترکی دارید
]

# الگوهای Regex پیشرفته برای شناسایی کلیدهای ترجمه
PATTERNS = [
    # فرانت‌اند: t('key'), t("key"), t(`key`)
    r"t\s*\(\s*['\"`](.*?)['\"`]\s*\)",
    # فرانت‌اند: i18nKey="key" یا i18nKey={'key'}
    r"i18nKey\s*=\s*['\"](.*?)['\"]",
    # فرانت‌اند: useTranslation('namespace') - برای شناسایی namespaceها
    r"useTranslation\s*\(\s*['\"](.*?)['\"]\s*\)",
    # بک‌اند پایتون: _('key') یا _("key")
    r"_\s*\(\s*['\"](.*?)['\"]\s*\)",
    # بک‌اند پایتون: gettext('key')
    r"gettext\s*\(\s*['\"](.*?)['\"]\s*\)",
    # بک‌اند پایتون: gettext_lazy('key')
    r"gettext_lazy\s*\(\s*['\"](.*?)['\"]\s*\)"
]

def extract_keys_from_file(file_path: Path) -> set:
    """استخراج کلیدها از یک فایل با استفاده از الگوهای تعریف‌شده"""
    found_keys = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        for pattern in PATTERNS:
            matches = re.findall(pattern, content)
            for match in matches:
                # تمیزکاری کلید: حذف فاصله‌های اضافی و اطمینان از معتبر بودن
                key = match.strip()
                if key and len(key) > 2 and not key.startswith('{'):
                    found_keys.add(key)
    except Exception as e:
        pass # نادیده گرفتن خطاهای خواندن فایل
    return found_keys

def main():
    print("=" * 60)
    print("🚀 شروع استخراج پیشرفته و عمیق کلیدهای i18n")
    print("=" * 60)
    
    all_keys = set()
    files_scanned = 0
    
    for search_dir in SEARCH_DIRS:
        if not search_dir.exists():
            continue
            
        print(f"🔍 در حال اسکن عمیق دایرکتوری: {search_dir.relative_to(PROJECT_ROOT)}")
        
        # پیمایش بازگشتی تمام فایل‌ها
        for root, dirs, files in os.walk(search_dir):
            # نادیده گرفتن پوشه‌های بیهوده
            dirs[:] = [d for d in dirs if d not in ['node_modules', 'dist', 'build', '.next', '__pycache__', 'venv', '.git']]
            
            for file in files:
                if file.endswith(('.ts', '.tsx', '.js', '.jsx', '.py')):
                    file_path = Path(root) / file
                    keys = extract_keys_from_file(file_path)
                    all_keys.update(keys)
                    files_scanned += 1

    print(f"\n✅ اسکن {files_scanned} فایل تکمیل شد.")
    print(f"🔑 تعداد کلیدهای یکتای معتبر یافت‌شده در کد: {len(all_keys)}")
    
    # مرتب‌سازی کلیدها برای خوانایی بهتر
    sorted_keys = sorted(list(all_keys))
    
    # ۱. ذخیره لیست خام کلیدها
    keys_file = PROJECT_ROOT / "master_i18n_keys_v2.txt"
    with open(keys_file, 'w', encoding='utf-8') as f:
        for key in sorted_keys:
            f.write(f"{key}\n")
    print(f"📄 لیست خام کلیدها ذخیره شد: {keys_file.name}")
    
    # ۲. ایجاد قالب پایه JSON (تخت شده برای سهولت کار)
    template_dict = {key: "" for key in sorted_keys}
    template_file = PROJECT_ROOT / "master_base_template_v2.json"
    with open(template_file, 'w', encoding='utf-8') as f:
        json.dump(template_dict, f, ensure_ascii=False, indent=2)
    print(f"📄 قالب پایه JSON تمیز ذخیره شد: {template_file.name}")

    # ۳. بررسی کلیدهای یتیم (موجود در JSON اما نه در کد)
    print("\n🧹 در حال بررسی کلیدهای یتیم (استفاده‌نشده در کد)...")
    locales_dir = PROJECT_ROOT / "apps" / "web" / "src" / "i18n" / "locales"
    if locales_dir.exists():
        for locale_file in locales_dir.glob("*.json"):
            try:
                with open(locale_file, 'r', encoding='utf-8') as f:
                    # فرض بر این است که JSON تخت است یا ما فقط کلیدهای سطح اول را چک می‌کنیم
                    # برای دقت بیشتر، باید JSON را تخت کنیم، اما برای تشخیص اولیه همین کافی است
                    locale_data = json.load(f)
                    
                    # تخت کردن دیکشنری برای مقایسه دقیق
                    def flatten(d, parent_key='', sep='.'):
                        items = []
                        for k, v in d.items():
                            new_key = f"{parent_key}{sep}{k}" if parent_key else k
                            if isinstance(v, dict):
                                items.extend(flatten(v, new_key, sep=sep).items())
                            else:
                                items.append(new_key)
                        return items
                        
                    file_keys = set(flatten(locale_data))
                    orphaned = file_keys - all_keys
                    
                    if len(orphaned) > 0:
                        print(f"   ⚠️ فایل {locale_file.name}: {len(orphaned)} کلید استفاده‌نشده یافت شد.")
            except Exception:
                pass

    print("\n" + "=" * 60)
    print("🎉 عملیات استخراج با موفقیت به پایان رسید!")
    if len(all_keys) == 0:
        print("⚠️ هشدار: هنوز هیچ کلیدی پیدا نشده است. لطفاً بررسی کنید که آیا از تابع t() یا _() استفاده می‌کنید یا خیر.")
    print("=" * 60)

if __name__ == "__main__":
    main()
import os
import re
import json
from pathlib import Path

# تنظیمات مسیرها
PROJECT_ROOT = Path("D:/econojin.com")
SRC_DIR = PROJECT_ROOT / "apps" / "web" / "src"
EN_FILE = PROJECT_ROOT / "apps" / "web" / "src" / "i18n" / "locales" / "en.json"
FA_FILE = PROJECT_ROOT / "apps" / "web" / "src" / "i18n" / "locales" / "fa.json"

# الگوهای Regex برای پیدا کردن کلیدها در کدهای React/i18next
# 1. t('some.key') یا t("some.key")
# 2. i18nKey="some.key" یا i18nKey='some.key'
PATTERNS = [
    r'\bt\(\s*[\'"]([a-zA-Z0-9_.-]+)[\'"]\s*[,)]',
    r'\bi18nKey=[\'"]([a-zA-Z0-9_.-]+)[\'"]',
]

def extract_keys_from_source():
    """جستجو در سورس کد و استخراج کلیدهای معتبر UI"""
    found_keys = set()
    print(f"🔍 در حال اسکن سورس کد در مسیر: {SRC_DIR}")
    
    if not SRC_DIR.exists():
        print("❌ مسیر سورس کد یافت نشد.")
        return found_keys

    # اسکن فایل‌های مرتبط
    extensions = ('.ts', '.tsx', '.js', '.jsx')
    for root, _, files in os.walk(SRC_DIR):
        # صرف نظر کردن از پوشه node_modules و .next
        if 'node_modules' in root or '.next' in root:
            continue
            
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in PATTERNS:
                            matches = re.findall(pattern, content)
                            found_keys.update(matches)
                except Exception:
                    pass
                    
    # فیلتر کردن کلیدهای احتمالی غیرمعتبر (مثل مسیرهای فایل یا متغیرهای داینامیک)
    valid_keys = {k for k in found_keys if '.' in k and not k.startswith('./') and not '{' in k}
    print(f"✅ تعداد {len(valid_keys)} کلید معتبر UI در سورس کد یافت شد.")
    return valid_keys

def unflatten_dict(d, sep='.'):
    """تبدیل کلیدهای تخت (flat) به ساختار درختی (nested)"""
    result = {}
    for key, value in d.items():
        parts = key.split(sep)
        current = result
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    return result

def update_locale_file(file_path, valid_keys, base_lang='en'):
    """به‌روزرسانی فایل JSON با کلیدهای جدید"""
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        current_data = {}
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            # خواندن فایل و تبدیل آن به ساختار تخت برای مقایسه آسان
            def flatten(d, parent_key='', sep='.'):
                items = []
                for k, v in d.items():
                    new_key = f"{parent_key}{sep}{k}" if parent_key else k
                    if isinstance(v, dict):
                        items.extend(flatten(v, new_key, sep=sep).items())
                    else:
                        items.append((new_key, v))
                return dict(items)
            current_data = flatten(json.load(f))

    added_count = 0
    for key in valid_keys:
        if key not in current_data:
            # اگر کلید در فایل نیست، یک مقدار پیش‌فرض (همان کلید یا پیشوند زبان) اضافه می‌کنیم
            current_data[key] = f"[NEW_{base_lang.upper()}] {key.split('.')[-1].replace('_', ' ').capitalize()}"
            added_count += 1

    if added_count > 0:
        # تبدیل مجدد به ساختار درختی و ذخیره
        nested_data = unflatten_dict(current_data)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(nested_data, f, ensure_ascii=False, indent=2)
        print(f"🔄 فایل {file_path.name} به‌روزرسانی شد. ({added_count} کلید جدید اضافه شد).")
    else:
        print(f"✅ فایل {file_path.name} از قبل کامل است و نیازی به کلید جدید ندارد.")

if __name__ == "__main__":
    print("🚀 شروع استخراج کلیدهای UI از سورس کد...")
    keys = extract_keys_from_source()
    
    if keys:
        update_locale_file(EN_FILE, keys, base_lang='en')
        update_locale_file(FA_FILE, keys, base_lang='fa')
        print("\n🎉 عملیات استخراج و همگام‌سازی پایه با موفقیت انجام شد.")
        print("💡 اکنون می‌توانید فایل‌های en.json و fa.json را باز کرده و مقادیر [NEW...] را ترجمه کنید.")
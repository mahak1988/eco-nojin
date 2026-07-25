import os
import re
from pathlib import Path

PROJECT_ROOT = Path("D:/econojin.com")
# جستجو در کل پروژه برای یافتن الگوی صحیح
SEARCH_DIRS = ["apps/web/src", "packages", "src"] 

print("🔍 در حال جستجوی الگوهای ترجمه در کدبیس...")

# الگوهای عمومی برای پیدا کردن فراخوانی توابع با آرگومان رشته‌ای
patterns_to_test = [
    r"\b\w+\s*\(\s*['\"]([^'\"]{3,50})['\"]",  # تابع('کلید')
    r"i18nKey\s*=\s*['\"]([^'\"]+)['\"]",      # i18nKey="کلید"
    r"\b\w+\s*\(\s*`([^`]{3,50})`",            # تابع(`کلید`)
]

found_examples = {p: set() for p in patterns_to_test}

for search_dir in SEARCH_DIRS:
    dir_path = PROJECT_ROOT / search_dir
    if not dir_path.exists():
        continue
        
    for ext in ["*.tsx", "*.ts", "*.jsx", "*.js"]:
        for file_path in dir_path.rglob(ext):
            # نادیده گرفتن پوشه‌های بیهوده
            if any(ignore in str(file_path) for ignore in ["node_modules", ".next", "dist", "build"]):
                continue
                
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                for pattern in patterns_to_test:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        # فیلتر کردن کلیدهای معتبر (حاوی نقطه و حروف انگلیسی)
                        if "." in match and re.match(r"^[a-zA-Z0-9_.]+$", match):
                            found_examples[pattern].add(match)
            except Exception:
                pass

print("\n📊 نتایج اکتشاف:")
for pattern, examples in found_examples.items():
    valid_examples = list(examples)[:5] # نمایش حداکثر ۵ نمونه
    if valid_examples:
        print(f"\n✅ الگوی پیدا شده: {pattern}")
        print("   نمونه‌ها:", ", ".join(valid_examples))
    else:
        print(f"\n❌ هیچ نمونه‌ای برای الگوی: {pattern} یافت نشد.")

print("\n💡 راهنما:")
print("لطفاً خروجی بالا را بررسی کنید. اگر الگویی پیدا شد، نام تابع (مثلاً 't' یا 'translate') را به من بگویید")
print("تا اسکریپت استخراج نهایی را دقیقاً بر اساس کد شما تنظیم کنم.")
import os
import re
import json
from pathlib import Path

PROJECT_ROOT = Path("D:/econojin.com")
# الگوهای گسترده‌تر برای یافتن هر نوع فراخوانی ترجمه
PATTERNS = [
    r't\s*\(\s*["\']([^"\']{3,60})["\']\s*\)',       # t('key') یا t("key")
    r'i18nKey\s*=\s*["\']([^"\']{3,60})["\']',      # i18nKey="key"
    r'translate\s*\(\s*["\']([^"\']{3,60})["\']\s*\)', # translate('key')
    r'\{\s*t\s*\(\s*["\']([^"\']{3,60})["\']\s*\)\s*\}' # { t('key') }
]

found_keys = set()
files_scanned = 0

print("🔍 در حال اسکن عمیق‌تر برای یافتن الگوهای i18n...")
for ext in ["*.tsx", "*.ts", "*.jsx", "*.js"]:
    for file_path in PROJECT_ROOT.rglob(ext):
        if any(ignore in str(file_path) for ignore in ["node_modules", ".next", "dist", "build"]):
            continue
        files_scanned += 1
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            for pattern in PATTERNS:
                matches = re.findall(pattern, content)
                found_keys.update(matches)
        except Exception:
            pass

print(f"✅ اسکن {files_scanned} فایل تکمیل شد.")
print(f"🔑 تعداد کلیدهای i18n معتبر یافت‌شده: {len(found_keys)}")

if len(found_keys) > 0:
    print("\n💡 نمونه‌ای از کلیدهای یافت‌شده:")
    for key in list(found_keys)[:15]:
        print(f"   - {key}")
else:
    print("\n⚠️ هشدار: همچنان هیچ کلید i18n یافت نشد. این تأیید می‌کند که فرانت‌اند تقریباً به طور کامل از متن‌های سخت‌کد (Hardcoded) استفاده می‌کند.")
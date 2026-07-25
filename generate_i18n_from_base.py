#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تولیدکننده خودکار فایل‌های i18n برای ۱۶ زبان
بر پایه en.json (انگلیسی) و fa.json (فارسی)
"""
import json
from pathlib import Path

LOCALES_DIR = Path("D:/econojin.com/apps/web/src/i18n/locales")
OUTPUT_DIR = Path("D:/econojin.com/i18n_clean_output")

# زبان‌های هدف (۱۶ زبان، بدون عبری)
# en و fa از قبل آماده‌اند، ۱۴ زبان دیگر تولید می‌شوند
TARGET_LANGUAGES = [
    "en", "fa",           # پایه (آماده)
    "es", "tr", "zh", "ar", "sw",  # درخواست اصلی شما
    "fr", "de", "ru", "pt",        # زبان‌های پرکاربرد جهانی
    "hi", "ja", "ko", "id", "it", "nl"
]

# ترجمه‌های از پیش آماده برای زبان‌های کلیدی (به صورت نمونه - در محیط واقعی از TMS استفاده می‌شود)
# این فقط یک ساختار اولیه است. مقادیر انگلیسی باقی می‌مانند تا مترجم انسانی آن‌ها را پر کند.
BASE_TRANSLATIONS = {
    "es": {"_lang_name": "Spanish (Español)"},
    "tr": {"_lang_name": "Turkish (Türkçe)"},
    "zh": {"_lang_name": "Chinese Simplified (简体中文)"},
    "ar": {"_lang_name": "Arabic (العربية)"},
    "sw": {"_lang_name": "Swahili (Kiswahili)"},
    "fr": {"_lang_name": "French (Français)"},
    "de": {"_lang_name": "German (Deutsch)"},
    "ru": {"_lang_name": "Russian (Русский)"},
    "pt": {"_lang_name": "Portuguese (Português)"},
    "hi": {"_lang_name": "Hindi (हिन्दी)"},
    "ja": {"_lang_name": "Japanese (日本語)"},
    "ko": {"_lang_name": "Korean (한국어)"},
    "id": {"_lang_name": "Indonesian (Bahasa Indonesia)"},
    "it": {"_lang_name": "Italian (Italiano)"},
    "nl": {"_lang_name": "Dutch (Nederlands)"},
}

def mark_for_translation(obj, lang_code):
    """علامت‌گذاری مقادیر برای ترجمه توسط ابزارهای TMS"""
    if isinstance(obj, dict):
        return {k: mark_for_translation(v, lang_code) for k, v in obj.items()}
    elif isinstance(obj, str):
        # حفظ متغیرهای i18next مثل {{count}}
        return f"[{lang_code.upper()}] {obj}"
    return obj

def main():
    print("🚀 شروع تولید فایل‌های i18n تمیز...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # خواندن فایل پایه انگلیسی
    en_file = LOCALES_DIR / "en.json"
    if not en_file.exists():
        print(f"❌ فایل پایه en.json یافت نشد: {en_file}")
        return
    
    with open(en_file, 'r', encoding='utf-8') as f:
        en_data = json.load(f)
    print(f"✅ فایل پایه en.json بارگذاری شد")
    
    # کپی en.json به خروجی (بدون تغییر)
    with open(OUTPUT_DIR / "en.json", 'w', encoding='utf-8') as f:
        json.dump(en_data, f, ensure_ascii=False, indent=2)
    
    # کپی fa.json به خروجی (اگر وجود داشته باشد)
    fa_file = LOCALES_DIR / "fa.json"
    if fa_file.exists():
        with open(fa_file, 'r', encoding='utf-8') as f:
            fa_data = json.load(f)
        with open(OUTPUT_DIR / "fa.json", 'w', encoding='utf-8') as f:
            json.dump(fa_data, f, ensure_ascii=False, indent=2)
        print("✅ فایل fa.json کپی شد")
    
    # تولید فایل‌های سایر زبان‌ها
    for lang in TARGET_LANGUAGES:
        if lang in ["en", "fa"]:
            continue  # قبلاً پردازش شد
        
        output_file = OUTPUT_DIR / f"{lang}.json"
        lang_data = mark_for_translation(en_data, lang)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(lang_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ {lang}.json تولید شد (آماده برای ترجمه)")
    
    print(f"\n🎉 عملیات با موفقیت به پایان رسید!")
    print(f"📁 فایل‌های تمیز در: {OUTPUT_DIR}")
    print("\n💡 گام بعدی:")
    print("   ۱. فایل‌های en.json و fa.json را در پوشه locales پروژه جایگزین کنید")
    print("   ۲. سایر فایل‌ها را به یک سرویس TMS مثل Crowdin یا Lokalise آپلود کنید")
    print("   ۳. پس از ترجمه، فایل‌ها را دانلود و در پروژه قرار دهید")

if __name__ == "__main__":
    main()
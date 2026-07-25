#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخه هوشمند: پیدا کردن خودکار فایل پایه و افزودن سواحیلی
"""
import json
from pathlib import Path

PROJECT_ROOT = Path(".")

# زبان‌های هدف (سواحیلی 'sw' اضافه شد)
TARGET_LANGUAGES = [
    "fa", "en", "ar", "zh", "es", "fr", "de", "ru", 
    "tr", "sw"  # sw = Swahili (سواحیلی)
]

def find_base_file():
    """جستجوی پویا برای پیدا کردن فایل fa.json یا en.json در کل پروژه"""
    print("🔍 در حال جستجوی فایل پایه (fa.json یا en.json) در پروژه...")
    
    # اولویت با fa.json است، اگر نبود en.json
    for base_name in ["fa.json", "en.json"]:
        # جستجو در مسیرهای رایج i18n
        search_paths = [
            PROJECT_ROOT.rglob(f"**/i18n/**/{base_name}"),
            PROJECT_ROOT.rglob(f"**/locales/**/{base_name}"),
            PROJECT_ROOT.rglob(f"**/translations/**/{base_name}")
        ]
        
        for paths in search_paths:
            for file_path in paths:
                # اطمینان از اینکه فایل داخل node_modules یا build نباشد
                if "node_modules" not in str(file_path) and "dist" not in str(file_path):
                    print(f"✅ فایل پایه یافت شد: {file_path}")
                    return file_path
                    
    print("❌ فایل پایه (fa.json یا en.json) در پروژه یافت نشد.")
    print("💡 راهنما: لطفاً نام دقیق و مسیر فایل اصلی ترجمه خود را بررسی کنید.")
    return None

def clean_and_generate(base_file: Path):
    print(f"\n🚀 شروع پاک‌سازی و تولید فایل‌ها بر اساس: {base_file.name}")
    
    try:
        with open(base_file, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
    except Exception as e:
        print(f"❌ خطا در خواندن فایل پایه: {e}")
        return

    # استخراج کلیدهای تودرتو به صورت تخت برای مقایسه آسان
    def flatten_dict(d, parent_key='', sep='.'):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    flat_base = flatten_dict(base_data)
    valid_keys = set(flat_base.keys())
    
    print(f"📊 تعداد کلیدهای معتبر در فایل پایه: {len(valid_keys)}")

    # ایجاد پوشه خروجی
    output_dir = PROJECT_ROOT / "clean_i18n_output"
    output_dir.mkdir(exist_ok=True)

    # پردازش هر زبان
    for lang in TARGET_LANGUAGES:
        # پیدا کردن فایل موجود آن زبان (اگر وجود داشته باشد)
        lang_file_candidates = list(PROJECT_ROOT.rglob(f"**/{lang}.json"))
        lang_file = next((f for f in lang_file_candidates if "node_modules" not in str(f)), None)
        
        lang_data = {}
        missing_count = 0
        
        if lang_file:
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    lang_data = flatten_dict(json.load(f))
            except:
                pass

        # ساخت دیکشنری تمیز و تکمیل‌شده
        clean_flat = {}
        for key in valid_keys:
            if key in lang_data and lang_data[key]: # اگر ترجمه وجود دارد و خالی نیست
                clean_flat[key] = lang_data[key]
            else:
                # اگر ترجمه نیست، از فایل پایه کپی می‌شود (با یک پیشوند برای شناسایی آسان)
                clean_flat[key] = f"[{lang.upper()}] {flat_base[key]}"
                missing_count += 1

        # تبدیل مجدد به حالت تودرتو
        def unflatten_dict(d, sep='.'):
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

        final_data = unflatten_dict(clean_flat)
        
        # ذخیره فایل
        out_path = output_dir / f"{lang}.json"
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=2)
            
        print(f"  ✅ {lang}.json تولید شد. ({missing_count} کلید تکمیل‌شده از پایه)")

    print(f"\n🎉 عملیات با موفقیت به پایان رسید!")
    print(f"📁 فایل‌های تمیز و استاندارد در پوشهٔ `clean_i18n_output` ذخیره شدند.")

if __name__ == "__main__":
    base = find_base_file()
    if base:
        clean_and_generate(base)
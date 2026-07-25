import json
import os
from pathlib import Path

# مسیر دقیق دایرکتوری لوکال‌ها بر اساس خروجی شما
LOCALES_DIR = Path("D:/econojin.com/apps/web/src/i18n/locales")
BASE_LANG = "fa"

def flatten_dict(d, parent_key='', sep='.'):
    """تبدیل دیکشنری تودرتو به دیکشنری تخت برای مقایسه آسان کلیدها"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_dict(d, sep='.'):
    """بازگرداندن دیکشنری تخت به ساختار تودرتوی اصلی JSON"""
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

def main():
    if not LOCALES_DIR.exists():
        print(f"❌ دایرکتوری یافت نشد: {LOCALES_DIR}")
        return

    print(f"🔍 در حال بررسی دایرکتوری: {LOCALES_DIR}")
    
    # ۱. خواندن فایل پایه (fa.json)
    base_file = LOCALES_DIR / f"{BASE_LANG}.json"
    if not base_file.exists():
        print(f"❌ فایل پایه {base_file.name} یافت نشد!")
        return
        
    with open(base_file, 'r', encoding='utf-8') as f:
        base_data = json.load(f)
    
    base_flat = flatten_dict(base_data)
    base_keys = set(base_flat.keys())
    print(f"✅ فایل پایه '{BASE_LANG}.json' با {len(base_keys)} کلید یکتا بارگذاری شد.")

    # ۲. بررسی سایر فایل‌های زبان
    lang_files = [f for f in LOCALES_DIR.glob("*.json") if f.stem != BASE_LANG]
    
    # ایجاد پوشه خروجی برای فایل‌های اصلاح‌شده (بدون دستکاری فایل‌های اصلی)
    output_dir = LOCALES_DIR.parent / "locales_synced"
    output_dir.mkdir(exist_ok=True)
    
    report = []
    report.append("# 🌍 گزارش همگام‌سازی i18n پروژه Econojin\n")
    report.append(f"- **زبان پایه مرجع:** {BASE_LANG} ({len(base_keys)} کلید)\n")

    for lang_file in lang_files:
        lang_code = lang_file.stem
        print(f"\n🔄 در حال پردازش: {lang_code}.json")
        
        with open(lang_file, 'r', encoding='utf-8') as f:
            lang_data = json.load(f)
            
        lang_flat = flatten_dict(lang_data)
        lang_keys = set(lang_flat.keys())
        
        missing_keys = base_keys - lang_keys
        extra_keys = lang_keys - base_keys
        
        report.append(f"## زبان: `{lang_code}`")
        report.append(f"- کلیدهای موجود: {len(lang_keys)}")
        report.append(f"- ⚠️ کلیدهای گمشده (نسبت به fa): **{len(missing_keys)}**")
        report.append(f"- کلیدهای اضافی (منسوخ): {len(extra_keys)}\n")
        
        if missing_keys:
            print(f"  ⚠️ {len(missing_keys)} کلید گمشده پیدا شد. در حال تکمیل خودکار با مقدار فارسی...")
            # تکمیل کلیدهای گمشده با مقدار زبان پایه (fa) تا برنامه کرش نکند
            for key in missing_keys:
                lang_flat[key] = base_flat[key]
                
            # ذخیره فایل همگام‌شده
            synced_data = unflatten_dict(lang_flat)
            output_file = output_dir / f"{lang_code}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(synced_data, f, ensure_ascii=False, indent=2)
            print(f"  ✅ فایل همگام‌شده ذخیره شد: {output_file}")
        else:
            print(f"  ✅ این فایل کامل است و هیچ کلیدی کم ندارد.")

    # ۳. ذخیره گزارش نهایی
    report_file = LOCALES_DIR.parent / "i18n_sync_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))
        
    print(f"\n🎉 عملیات با موفقیت به پایان رسید!")
    print(f"📄 گزارش کامل در: {report_file}")
    print(f"📁 فایل‌های JSON اصلاح‌شده در: {output_dir}")
    print("\n💡 نکته: فایل‌های داخل پوشه locales_synced را بررسی و در صورت تأیید، جایگزین فایل‌های اصلی در پوشه locales کنید.")

if __name__ == "__main__":
    main()
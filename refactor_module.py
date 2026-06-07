import os
import re
import logging
from pathlib import Path

# تنظیمات لاگر برای خود اسکریپت
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def refactor_prints_in_directory(target_dir: str):
    """تبدیل print statement ها به logging در یک دایرکتوری خاص"""
    target_path = Path(target_dir)
    
    if not target_path.exists():
        logging.error(f"مسیر {target_dir} وجود ندارد.")
        return

    # الگوی regex برای پیدا کردن print(...)
    # توجه: این یک الگوی ساده است. برای پروژه‌های حساس، بازبینی دستی با Git Diff الزامی است.
    print_pattern = re.compile(r'^(\s*)print\s*\((.*)\)\s*$', re.MULTILINE)
    
    modified_files = 0

    for py_file in target_path.rglob("*.py"):
        # نادیده گرفتن محیط مجازی و پوشه‌های سیستمی
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'print(' in content:
                # جایگزینی هوشمند: اضافه کردن import logging اگر وجود ندارد
                if 'import logging' not in content:
                    content = 'import logging\n\n' + content
                
                # تبدیل print("msg") به logging.info("msg")
                # و print(e) به logging.error(f"Error: {e}", exc_info=True)
                def replace_print(match):
                    indent = match.group(1)
                    args = match.group(2).strip()
                    
                    # تشخیص ساده برای استثناها (مثلاً print(e))
                    if len(args) <= 3 and args.isalpha():
                        return f'{indent}logging.error(f"Exception in {os.path.basename(py_file.name)}: {{ {args} }}", exc_info=True)'
                    else:
                        return f'{indent}logging.info({args})'

                new_content = print_pattern.sub(replace_print, content)

                if new_content != content:
                    with open(py_file, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    modified_files += 1
                    logging.info(f"✅ اصلاح شد: {py_file.relative_to(target_path)}")

        except Exception as e:
            logging.error(f"خطا در پردازش {py_file}: {e}")

    logging.info(f"🎉 عملیات پایان یافت. {modified_files} فایل اصلاح شد.")

if __name__ == "__main__":
    # ⚠️ هشدار: قبل از اجرا، حتماً یک commit در Git داشته باشید تا بتوانید تغییرات را بازبینی کنید.
    folder_to_refactor = input("نام پوشه یا ماژول مورد نظر برای اصلاح را وارد کنید (مثال: apps/api یا .): ")
    refactor_prints_in_directory(folder_to_refactor)
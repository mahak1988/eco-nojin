import os
import re
import shutil
from pathlib import Path

def scan_and_fix_hardcoded_secrets(project_dir):
    """اسکن و اصلاح فایل‌های پایتون برای حذف کلیدهای هاردکد شده"""
    
    print("🔍 در حال جستجو برای فایل‌های حاوی کلید هاردکد شده...")
    
    # الگوهای جستجو برای کلیدهای هاردکد شده
    patterns = [
        (r'(?P<indent>\s*)(?P<var>password|passwd|pwd)\s*=\s*["\'](?P<value>[^"\']+)["\']', 'PASSWORD'),
        (r'(?P<indent>\s*)(?P<var>api_key|apikey|api_secret)\s*=\s*["\'](?P<value>[^"\']+)["\']', 'API_KEY'),
        (r'(?P<indent>\s*)(?P<var>secret_key|secret)\s*=\s*["\'](?P<value>[^"\']+)["\']', 'SECRET_KEY'),
        (r'(?P<indent>\s*)(?P<var>token|auth_token|access_token)\s*=\s*["\'](?P<value>[^"\']+)["\']', 'TOKEN'),
        (r'(?P<indent>\s*)(?P<var>database_url|db_url|postgres_url)\s*=\s*["\'](?P<value>[^"\']+)["\']', 'DATABASE_URL'),
    ]
    
    target_files = []
    
    # جستجو در تمام فایل‌های پایتون
    for py_file in Path(project_dir).rglob("*.py"):
        # حذف مسیرهای غیرضروری
        if any(x in str(py_file) for x in ['.venv', 'node_modules', '__pycache__', '.git']):
            continue
        
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            for pattern, _ in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    target_files.append(py_file)
                    break
        except Exception:
            continue
    
    if not target_files:
        print("✅ هیچ فایل پایتونی حاوی کلید هاردکد شده یافت نشد.")
        return
    
    print(f"\n⚠️  تعداد {len(target_files)} فایل حاوی کلید هاردکد شده یافت شد:")
    for f in target_files:
        print(f"  - {f.relative_to(project_dir)}")
    
    for target_file in target_files:
        print(f"\n{'='*60}")
        print(f"📄 در حال پردازش: {target_file.relative_to(project_dir)}")
        print('='*60)
        
        # ایجاد نسخه پشتیبان
        backup_file = target_file.with_suffix('.py.bak')
        if not backup_file.exists():
            shutil.copy2(target_file, backup_file)
            print(f"💾 نسخه پشتیبان ایجاد شد: {backup_file.name}")
        
        # خواندن محتوای فایل
        try:
            content = target_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"❌ خطا در خواندن فایل: {e}")
            continue
        
        found_keys = []
        new_content = content
        
        for pattern, env_name in patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                var_name = match.group('var')
                value = match.group('value')
                indent = match.group('indent')
                
                # اگر مقدار خیلی کوتاه است یا متغیر به نظر می‌رسد، رد کن
                if len(value) < 8 or value.startswith('$') or value.startswith('{') or value.startswith('os.'):
                    continue
                
                # نام متغیر محیطی را بساز
                env_var_name = env_name
                
                found_keys.append({
                    'line': match.group(0).strip(),
                    'var': var_name,
                    'value': value,
                    'env_name': env_var_name
                })
                
                # جایگزینی با os.getenv
                replacement = f'{indent}{var_name} = os.getenv("{env_var_name}")'
                new_content = new_content.replace(match.group(0), replacement)
        
        if not found_keys:
            print("✅ هیچ کلید هاردکد شده‌ای در این فایل یافت نشد.")
            if backup_file.exists():
                backup_file.unlink()
            continue
        
        print(f"\n🔑 تعداد {len(found_keys)} کلید هاردکد شده یافت شد:")
        for key in found_keys:
            masked_value = key['value'][:8] + '...' if len(key['value']) > 8 else key['value']
            print(f"  - {key['var']} = '{masked_value}' → os.getenv('{key['env_name']}')")
        
        # بررسی اینکه آیا os import شده است یا نه
        if 'import os' not in new_content and 'from os' not in new_content:
            new_content = "import os\n" + new_content
            print("📥 دستور 'import os' به ابتدای فایل اضافه شد.")
        
        # نوشتن فایل اصلاح‌شده
        try:
            target_file.write_text(new_content, encoding='utf-8')
            print(f"\n✅ فایل با موفقیت اصلاح شد.")
        except Exception as e:
            print(f"❌ خطا در نوشتن فایل: {e}")
            if backup_file.exists():
                shutil.copy2(backup_file, target_file)
                print("↩️  فایل پشتیبان بازگردانده شد.")
            continue
        
        # به‌روزرسانی فایل .env.example
        env_example_path = Path(project_dir) / ".env.example"
        env_lines = []
        if env_example_path.exists():
            env_lines = env_example_path.read_text(encoding='utf-8').splitlines()
        
        added_keys = []
        for key in found_keys:
            env_line = f"{key['env_name']}="
            if not any(line.startswith(env_line) for line in env_lines):
                env_lines.append(f"{key['env_name']}=your_{key['env_name'].lower()}_here")
                added_keys.append(key['env_name'])
        
        if added_keys:
            env_example_path.write_text('\n'.join(env_lines) + '\n', encoding='utf-8')
            print(f"\n📝 کلیدهای جدید به .env.example اضافه شدند: {', '.join(added_keys)}")
    
    print("\n" + "="*60)
    print("🎯 اقدامات بعدی:")
    print("1. فایل .env.example را بررسی کنید.")
    print("2. یک فایل .env ایجاد کنید و مقادیر واقعی کلیدها را در آن وارد کنید.")
    print("3. مطمئن شوید فایل .env در .gitignore قرار دارد.")
    print("4. فایل‌های اصلاح‌شده را تست کنید تا از عملکرد صحیح اطمینان حاصل شود.")
    print("5. در صورت عدم نیاز، فایل‌های پشتیبان (.py.bak) را حذف کنید.")
    print("="*60)

if __name__ == "__main__":
    project_dir = r"D:\econojin.com"
    scan_and_fix_hardcoded_secrets(project_dir)
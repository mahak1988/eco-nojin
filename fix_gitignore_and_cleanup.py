import os
import subprocess
from pathlib import Path

def run_command(cmd, cwd=None):
    """اجرای دستور در ترمینال و چاپ خروجی با فرمت زیبا"""
    print(f"\n▶️ در حال اجرا: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding='utf-8')
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

def update_gitignore(project_dir):
    """بروزرسانی هوشمند فایل .gitignore با قوانین استاندارد پروژه"""
    gitignore_path = Path(project_dir) / '.gitignore'
    
    # قوانین استانداردی که برای این پروژه (Python + Next.js + Docker) الزامی است
    rules_to_add = [
        "# ==========================================",
        "# محیط‌های مجازی پایتون (بسیار مهم)",
        "# ==========================================",
        ".venv/",
        ".venv.backup/",
        "venv/",
        "env/",
        "ENV/",
        "",
        "# ==========================================",
        "# فایل‌های محیطی و متغیرهای حساس",
        "# ==========================================",
        ".env",
        ".env.local",
        ".env.*.local",
        "*.env",
        "!.env.example",
        "!env.example",
        "",
        "# ==========================================",
        "# Node.js و Next.js",
        "# ==========================================",
        "node_modules/",
        ".next/",
        "out/",
        "build/",
        "dist/",
        "",
        "# ==========================================",
        "# فایل‌های موقت، کش و لاگ",
        "# ==========================================",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        ".pytest_cache/",
        "coverage/",
        "*.log",
        "npm-debug.log*",
        "",
        "# ==========================================",
        "# تنظیمات IDE و سیستم‌عامل",
        "# ==========================================",
        ".vscode/",
        ".idea/",
        ".DS_Store",
        "Thumbs.db",
    ]
    
    # خواندن محتوای فعلی
    existing_content = ""
    if gitignore_path.exists():
        existing_content = gitignore_path.read_text(encoding='utf-8')
    
    # فیلتر کردن قوانینی که از قبل وجود ندارند
    unique_new_rules = []
    for rule in rules_to_add:
        if rule.startswith("#") or rule == "":
            unique_new_rules.append(rule)
        elif rule not in existing_content:
            unique_new_rules.append(rule)
            
    # نوشتن قوانین جدید در انتهای فایل
    if unique_new_rules:
        print("📝 در حال افزودن قوانین جدید به .gitignore...")
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write("\n" + "\n".join(unique_new_rules) + "\n")
        print("✅ فایل .gitignore با موفقیت بروزرسانی شد.")
    else:
        print("ℹ️ فایل .gitignore از قبل شامل تمام قوانین ضروری است.")

def main():
    project_dir = r"D:\econojin.com"
    
    print("🚀 شروع اجرای خودکار اقدامات امنیتی و پاکسازی Git...\n")
    
    # 1. بروزرسانی .gitignore
    update_gitignore(project_dir)
    
    # 2. اضافه کردن به Git و کامیت
    run_command("git add .gitignore", cwd=project_dir)
    run_command('git commit -m "chore: update .gitignore to exclude virtual environments and build artifacts"', cwd=project_dir)
    
    # 3. پاکسازی هشدار loose objects با git gc (بهینه‌سازی مخزن)
    print("\n🧹 در حال پاکسازی اشیاء بی‌استفاده Git (رفع هشدار loose objects)...")
    run_command("git gc --prune=now", cwd=project_dir)
    
    print("\n🎉 تمام اقدامات با موفقیت انجام شد!")

if __name__ == "__main__":
    main()
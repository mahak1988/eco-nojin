import subprocess
import sys
import re

# تنظیمات
MAIN_BRANCH = "main"
TEST_BRANCH = "test-merge-all"
REMOTE = "origin"

# لیست الگوهایی که نباید ادغام شوند
EXCLUDE_PATTERNS = [
    r"^dependabot/",
    r"^revert-",
    r"qwen-code",
    r"HEAD"
]

def run_command(command):
    """اجرای دستور گیت و بازگرداندن خروجی"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True, 
            encoding='utf-8'
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در اجرای دستور: {command}")
        print(e.stderr)
        return None

def should_exclude(branch_name):
    """بررسی اینکه آیا شاخه باید نادیده گرفته شود یا خیر"""
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, branch_name):
            return True
    return False

def main():
    print("🚀 شروع فرآیند ادغام هوشمند شاخه‌ها...")

    # 1. دریافت آخرین تغییرات از سرور
    print("\n📡 در حال دریافت اطلاعات شاخه‌ها (git fetch)...")
    run_command("git fetch --all --prune")

    # 2. لیست کردن شاخه‌های ریموت
    print("\n📋 دریافت لیست شاخه‌های ریموت...")
    branches_output = run_command(f"git branch -r --format '%(refname:short)'")
    
    if not branches_output:
        print("خطا در دریافت لیست شاخه‌ها.")
        return

    all_remote_branches = branches_output.split('\n')
    
    # فیلتر کردن شاخه‌ها
    branches_to_merge = []
    for branch in all_remote_branches:
        clean_name = branch.replace(f"{REMOTE}/", "")
        
        if branch == f"{REMOTE}/{MAIN_BRANCH}" or branch == f"{REMOTE}/HEAD":
            continue
            
        if not should_exclude(branch):
            branches_to_merge.append(branch)
        else:
            print(f"⏭️ صرف‌نظر از شاخه: {branch}")

    if not branches_to_merge:
        print("هیچ شاخه‌ای برای ادغام یافت نشد.")
        return

    print(f"\n✅ تعداد {len(branches_to_merge)} شاخه برای ادغام شناسایی شد.")

    # 3. ایجاد یا ریست کردن شاخه تست
    print(f"\n🛠️ در حال آماده‌سازی شاخه تست '{TEST_BRANCH}' بر اساس '{MAIN_BRANCH}'...")
    
    # چک کردن اینکه آیا شاخه تست وجود دارد یا خیر
    current_branch = run_command("git rev-parse --abbrev-ref HEAD")
    
    # رفتن به شاخه اصلی برای اطمینان
    run_command(f"git checkout {MAIN_BRANCH}")
    run_command(f"git pull {REMOTE} {MAIN_BRANCH}")

    # ساخت شاخه تست جدید
    run_command(f"git checkout -B {TEST_BRANCH}")

    # 4. ادغام تک‌تک شاخه‌ها
    success_count = 0
    conflict_count = 0
    
    for branch in branches_to_merge:
        print(f"\n🔄 در حال ادغام {branch} ...")
        
        result = subprocess.run(
            f"git merge {branch} --no-edit", 
            shell=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode == 0:
            print(f"   ✅ با موفقیت ادغام شد: {branch}")
            success_count += 1
        else:
            print(f"   ⚠️ تداخل یا خطا در ادغام {branch}")
            print(f"      پیام: {result.stderr.strip()[:100]}...")
            subprocess.run("git merge --abort", shell=True)
            conflict_count += 1

    # 5. گزارش نهایی
    print("\n" + "="*40)
    print("🏁 پایان عملیات")
    print(f"✅ شاخه‌های موفق: {success_count}")
    print(f"⚠️ شاخه‌های دارای تداخل (لغو شده): {conflict_count}")
    print(f"💡 شما اکنون در شاخه '{TEST_BRANCH}' هستید.")
    print("🔍 لطفاً پروژه را بررسی کنید. اگر همه چیز درست بود، می‌توانید این شاخه را به main مرج کنید:")
    print(f"   git checkout {MAIN_BRANCH}")
    print(f"   git merge {TEST_BRANCH}")
    print("="*40)

if __name__ == "__main__":
    main()

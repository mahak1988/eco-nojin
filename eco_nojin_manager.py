"""
================================================================
  Econojin Repository Manager
  مخزن: https://github.com/mahak1988/eco-nojin.git
  اسکریپت مدیریت کامل مخزن GitHub برای PowerShell/VS Code
================================================================

نحوه استفاده در ترمینال PowerShell وی‌اس‌کد:
    python eco_nojin_manager.py              # منوی تعاملی
    python eco_nojin_manager.py clone        # کلون مستقیم
    python eco_nojin_manager.py info         # اطلاعات مخزن
    python eco_nojin_manager.py status       # وضعیت git
    python eco_nojin_manager.py branches     # لیست شاخه‌ها
    python eco_nojin_manager.py pull         # دریافت آخرین تغییرات
    python eco_nojin_manager.py open         # باز کردن در مرورگر

پیش‌نیازها:
    - نصب بودن Python 3.8+
    - نصب بودن Git (https://git-scm.com/downloads)
    - اتصال اینترنت

بررسی نصب پیش‌نیازها:
    python eco_nojin_manager.py check
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

# ================================================================
#   تنظیمات - در صورت نیاز ویرایش کنید
# ================================================================
REPO_URL = "https://github.com/mahak1988/eco-nojin.git"
REPO_NAME = "eco-nojin"
# مسیر پیش‌فرض کلون - می‌توانید تغییر دهید (None = مسیر فعلی)
CLONE_DIR = None  # مثال: r"C:\Projects\eco-nojin"


# ================================================================
#   توابع کمکی
# ================================================================
def run(cmd, cwd=None, capture=True):
    """اجرای دستور shell و بازگرداندن خروجی"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            shell=True,
            capture_output=capture,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)


def find_repo_path():
    """پیدا کردن مسیر مخزن کلون شده"""
    if CLONE_DIR:
        return Path(CLONE_DIR)
    # جستجو در مسیر فعلی و یک سطح بالاتر
    candidates = [
        Path.cwd() / REPO_NAME,
        Path.cwd(),
        Path.home() / REPO_NAME,
    ]
    for c in candidates:
        if (c / ".git").exists():
            return c
    return None


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_ok(msg):
    print(f"  [✓] {msg}")


def print_err(msg):
    print(f"  [✗] {msg}")


def print_info(msg):
    print(f"  [i] {msg}")


# ================================================================
#   عملیات اصلی
# ================================================================
def check_prerequisites():
    """بررسی نصب بودن Python و Git"""
    print_header("بررسی پیش‌نیازها")

    # Python
    code, out, _ = run("python --version")
    if code == 0:
        print_ok(f"Python: {out.strip()}")
    else:
        print_err("Python نصب نیست!")

    # Git
    code, out, _ = run("git --version")
    if code == 0:
        print_ok(f"Git: {out.strip()}")
    else:
        print_err("Git نصب نیست! از https://git-scm.com/downloads دانلود کنید.")

    # pip
    code, out, _ = run("pip --version")
    if code == 0:
        print_ok(f"pip: {out.strip()}")

    print("\nنکته: اگر git نصب نیست، در پاورشل با دستور زیر نصب کنید:")
    print('  winget install --id Git.Git -e --source winget')


def clone_repo():
    """کلون کردن مخزن"""
    print_header(f"کلون کردن {REPO_NAME}")

    target = Path(CLONE_DIR) if CLONE_DIR else (Path.cwd() / REPO_NAME)
    if target.exists():
        print_err(f"مسیر '{target}' از قبل وجود دارد.")
        ans = input("  حذف و دوباره کلون کنیم؟ (y/N): ").strip().lower()
        if ans == "y":
            import shutil
            shutil.rmtree(target, ignore_errors=True)
        else:
            print_info("عملیات لغو شد.")
            return

    print_info(f"کلون به: {target}")
    code, out, err = run(f'git clone "{REPO_URL}" "{target}"')
    if code == 0:
        print_ok("مخزن با موفقیت کلون شد!")
        print_info(f"مسیر: {target}")
        print("\nبرای ورود به پوشه:")
        print(f'  cd "{target}"')
    else:
        print_err("خطا در کلون کردن:")
        print(err or out)


def show_info():
    """نمایش اطلاعات مخزن"""
    repo = find_repo_path()
    if not repo:
        print_err("مخزن پیدا نشد. ابتدا کلون کنید: python eco_nojin_manager.py clone")
        return

    print_header("اطلاعات مخزن")
    print_info(f"مسیر محلی: {repo}")

    # Remote URL
    code, out, _ = run("git config --get remote.origin.url", cwd=str(repo))
    if code == 0:
        print_ok(f"Remote: {out.strip()}")

    # آخرین commit
    code, out, _ = run("git log -1 --format='%H%n%an <%ae>%n%ad%n%s'", cwd=str(repo))
    if code == 0:
        lines = out.strip().split("\n")
        if len(lines) >= 4:
            print(f"\n  آخرین Commit:")
            print(f"    SHA     : {lines[0][:12]}...")
            print(f"    نویسنده : {lines[1]}")
            print(f"    تاریخ   : {lines[2]}")
            print(f"    پیام    : {lines[3]}")

    # تعداد commit ها
    code, out, _ = run("git rev-list --count HEAD", cwd=str(repo))
    if code == 0:
        print_ok(f"تعداد کل Commitها: {out.strip()}")

    # حجم پوشه
    total_size = 0
    for dirpath, _, filenames in os.walk(repo):
        if ".git" in dirpath:
            continue
        for f in filenames:
            try:
                total_size += os.path.getsize(os.path.join(dirpath, f))
            except OSError:
                pass
    print_info(f"حجم (بدون .git): {total_size / (1024*1024):.2f} MB")

    # تعداد فایل‌ها
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(repo):
        # نادیده گرفتن پوشه .git
        if ".git" in dirpath:
            continue
        # نادیده گرفتن محتوای .git
        dirnames[:] = [d for d in dirnames if d != ".git"]
        file_count += len(filenames)
    print_info(f"تعداد فایل‌ها: {file_count}")


def show_status():
    """نمایش وضعیت git"""
    repo = find_repo_path()
    if not repo:
        print_err("مخزن پیدا نشد.")
        return

    print_header("وضعیت Git")
    code, out, _ = run("git status", cwd=str(repo))
    print(out)

    print("\n--- تغییرات خلاصه ---")
    code, out, _ = run("git status --short", cwd=str(repo))
    if out.strip():
        print(out)
    else:
        print_ok("هیچ تغییر محلی وجود ندارد (working tree clean)")


def list_branches():
    """لیست شاخه‌ها"""
    repo = find_repo_path()
    if not repo:
        print_err("مخزن پیدا نشد.")
        return

    print_header("شاخه‌های مخزن")

    # شاخه محلی
    code, out, _ = run("git branch", cwd=str(repo))
    print("\nشاخه‌های محلی:")
    print(out)

    # شاخه‌های ریموت
    code, out, _ = run("git branch -r", cwd=str(repo))
    print("شاخه‌های ریموت:")
    print(out)

    # شاخه فعلی
    code, out, _ = run("git rev-parse --abbrev-ref HEAD", cwd=str(repo))
    print_ok(f"شاخه فعلی: {out.strip()}")


def pull_latest():
    """دریافت آخرین تغییرات"""
    repo = find_repo_path()
    if not repo:
        print_err("مخزن پیدا نشد.")
        return

    print_header("دریافت آخرین تغییرات (git pull)")
    code, out, err = run("git pull", cwd=str(repo))
    print(out)
    if err:
        print(err)
    if code == 0:
        print_ok("با موفقیت به‌روزرسانی شد.")
    else:
        print_err("خطا در pull - شاید تغییرات ذخیره‌نشده دارید.")


def open_in_browser():
    """باز کردن مخزن در مرورگر"""
    print_header("باز کردن در مرورگر")
    print_info(f"URL: {REPO_URL}")
    webbrowser.open(REPO_URL)
    print_ok("در مرورگر پیش‌فرض باز شد.")


def show_structure():
    """نمایش ساختار پوشه‌ها"""
    repo = find_repo_path()
    if not repo:
        print_err("مخزن پیدا نشد.")
        return

    print_header("ساختار پوشه‌ها (فقط سطح اول)")
    items = sorted(repo.iterdir())
    dirs = [d for d in items if d.is_dir() and not d.name.startswith(".")]
    files = [f for f in items if f.is_file() and not f.name.startswith(".")]

    print("\nپوشه‌ها:")
    for d in dirs:
        print(f"  📁 {d.name}/")
    print("\nفایل‌ها:")
    for f in files[:30]:  # فقط ۳۰ فایل اول
        size = f.stat().st_size
        print(f"  📄 {f.name}  ({size:,} bytes)")
    if len(files) > 30:
        print(f"  ... و {len(files) - 30} فایل دیگر")


def show_recent_commits():
    """نمایش ۱۰ commit اخیر"""
    repo = find_repo_path()
    if not repo:
        print_err("مخزن پیدا نشد.")
        return

    print_header("۱۰ Commit اخیر")
    code, out, _ = run(
        'git log -10 --format="%h | %ad | %an | %s" --date=short',
        cwd=str(repo),
    )
    print(out)


# ================================================================
#   منوی تعاملی
# ================================================================
def show_menu():
    print("\n" + "═" * 60)
    print("  🌿  Econojin Repository Manager  🌿")
    print("  مخزن: mahak1988/eco-nojin")
    print("═" * 60)
    print("  1. کلون کردن مخزن (Clone)")
    print("  2. اطلاعات مخزن")
    print("  3. وضعیت Git")
    print("  4. لیست شاخه‌ها")
    print("  5. دریافت آخرین تغییرات (Pull)")
    print("  6. ساختار پوشه‌ها")
    print("  7. Commitهای اخیر")
    print("  8. باز کردن در مرورگر")
    print("  9. بررسی پیش‌نیازها")
    print("  0. خروج")
    print("═" * 60)

    actions = {
        "1": clone_repo,
        "2": show_info,
        "3": show_status,
        "4": list_branches,
        "5": pull_latest,
        "6": show_structure,
        "7": show_recent_commits,
        "8": open_in_browser,
        "9": check_prerequisites,
    }

    choice = input("\nانتخاب شما: ").strip()
    if choice in actions:
        actions[choice]()
        input("\n[Enter برای بازگشت به منو] ")
        return True
    elif choice == "0":
        print("\n  خدانگهدار! 👋\n")
        return False
    else:
        print_err("انتخاب نامعتبر!")
        return True


# ================================================================
#   نقطه ورود
# ================================================================
def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        commands = {
            "clone": clone_repo,
            "info": show_info,
            "status": show_status,
            "branches": list_branches,
            "pull": pull_latest,
            "structure": show_structure,
            "commits": show_recent_commits,
            "open": open_in_browser,
            "check": check_prerequisites,
            "help": lambda: print(__doc__),
        }
        if cmd in commands:
            commands[cmd]()
        else:
            print(f"دستور ناشناخته: {cmd}")
            print(f"دستورات موجود: {', '.join(commands.keys())}")
    else:
        # منوی تعاملی
        while show_menu():
            pass


if __name__ == "__main__":
    main()

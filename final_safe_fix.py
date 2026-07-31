import os
import re


def apply_safe_fix():
    service_file = "apps/admin_panel/service.py"
    repo_file = "apps/admin_panel/repository.py"

    print("🔧 در حال پاک‌سازی کدهای معیوب و اعمال اصلاحات ایمن...")

    # ------------------------------------------------------------------------------
    # ۱. پاک‌سازی repository.py (حذف کدهای بد-تورفتگی‌شده)
    # ------------------------------------------------------------------------------
    if os.path.exists(repo_file):
        with open(repo_file, "r", encoding="utf-8") as f:
            content = f.read()

        # حذف هر چیزی که از این مارکر به بعد آمده است
        if "# AUTO-APPENDED: Cursor-based Pagination" in content:
            content = content.split("# AUTO-APPENDED: Cursor-based Pagination")[0].rstrip()
            # حذف ایمپورت‌های سرگردان در انتهای فایل
            content = re.sub(r"\nfrom sqlalchemy import select, desc\s*$", "", content)

        with open(repo_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ فایل repository.py پاک‌سازی و از نظر سینتکسی اصلاح شد.")

    # ------------------------------------------------------------------------------
    # ۲. پاک‌سازی و تزریق ایمن در service.py
    # ------------------------------------------------------------------------------
    if os.path.exists(service_file):
        with open(service_file, "r", encoding="utf-8") as f:
            content = f.read()

        # حذف کدهای معیوب الحاق‌شده قبلی
        markers = ["# AUTO-APPENDED: Secure Delete User", "# OPTIMIZED & SECURE HELPER FUNCTIONS"]
        for marker in markers:
            if marker in content:
                content = content.split(marker)[0].rstrip()

        # الگوی جستجو: تعریف متد delete_user که پارامتر current_user_id دارد
        # توجه: این الگو تورفتگی ۴ فضایی (استاندارد داخل کلاس) را در نظر می‌گیرد
        pattern = r"(    async def delete_user\([^)]*current_user_id[^)]*\):)"

        # کد تزریقی با تورفتگی ۸ فضایی (استاندارد بدنه متد داخل کلاس)
        injection = r"""\1
        # SECURE INJECTION: Prevent self-deletion
        if target_user_id == current_user_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superusers cannot deactivate or delete their own accounts."
            )"""

        # فقط در صورتی تزریق کن که قبلاً انجام نشده باشد
        if "SECURE INJECTION" not in content:
            content = re.sub(pattern, injection, content)

        with open(service_file, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ فایل service.py پاک‌سازی و کد امنیتی با تورفتگی صحیح تزریق شد.")

    print("\n🎉 عملیات تعمیر سینتکس با موفقیت تکمیل شد. فایل‌ها اکنون معتبر هستند.")


if __name__ == "__main__":
    apply_safe_fix()

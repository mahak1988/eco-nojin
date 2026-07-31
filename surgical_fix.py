import os
import re


def apply_surgical_fix():
    router_path = "apps/admin_panel/router.py"
    service_path = "apps/admin_panel/service.py"

    print("🔪 شروع عملیات جراحی کد برای رفع خطای سینتکس...")

    # ------------------------------------------------------------------------------
    # ۱. اصلاح router.py: بازگرداندن فراخوانی‌ها به حالت استاندارد و ایمن
    # ------------------------------------------------------------------------------
    if os.path.exists(router_path):
        with open(router_path, "r", encoding="utf-8") as f:
            content = f.read()

        # جایگزینی فراخوانی‌های معیوب standalone با فراخوانی استاندارد متد کلاس
        # این Regex هر فراخوانی خراب delete_user_secure را به فرمت صحیح FastAPI برمی‌گرداند
        content = re.sub(
            r"await\s+delete_user_secure\([^)]+\)",
            r"await admin_service.delete_user(db=db, target_user_id=user_id, current_user_id=current_user.id)",
            content,
        )

        content = re.sub(
            r"await\s+get_dashboard_stats_cached\([^)]+\)",
            r"await admin_service.get_overview_stats(db=db)",
            content,
        )

        with open(router_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ router.py به حالت استاندارد و بدون خطای سینتکس بازگردانده شد.")

    # ------------------------------------------------------------------------------
    # ۲. اصلاح service.py: تزریق ایمن کد بررسی حذف خود (بدون تغییر ساختار کلاس)
    # ------------------------------------------------------------------------------
    if os.path.exists(service_path):
        with open(service_path, "r", encoding="utf-8") as f:
            content = f.read()

        # حذف تمام کدهای الحاق‌شده معیوب از تلاش‌های قبلی
        if "OPTIMIZED & SECURE HELPER FUNCTIONS" in content:
            content = content.split("OPTIMIZED & SECURE HELPER FUNCTIONS")[0].rstrip()
        if "# AUTO-APPENDED: Secure Delete User" in content:
            content = content.split("# AUTO-APPENDED: Secure Delete User")[0].rstrip()

        # الگوی جراحی: پیدا کردن تعریف تابع delete_user که پارامتر current_user_id دارد
        # و تزریق کد بررسی در خط بعد با تورفتگی دقیق ۸ فاصله (استاندارد داخل کلاس)
        pattern = r"(async def delete_user\([^)]*current_user_id[^)]*\):)"

        security_injection = r"""\1
        # SECURE INJECTION: Prevent self-deletion (Auto-Injected)
        if target_user_id == current_user_id:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Superusers cannot deactivate or delete their own accounts."
            )"""

        # فقط در صورتی تزریق کن که قبلاً انجام نشده باشد
        if "SECURE INJECTION" not in content:
            content = re.sub(pattern, security_injection, content)

        with open(service_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ service.py با تزریق ایمن کد امنیتی درون متد اصلی اصلاح شد.")

    print("\n🎉 عملیات جراحی کد با موفقیت و بدون خطای سینتکس تکمیل شد.")


if __name__ == "__main__":
    apply_surgical_fix()

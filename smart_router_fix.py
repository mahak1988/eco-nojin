import re

file_path = "apps/admin_panel/router.py"

print("🔍 در حال تحلیل هوشمند فایل router.py برای یافتن نام صحیح Dependency دیتابیس...")

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# ۱. یافتن نام واقعی Dependency دیتابیس که در سایر نقاط فایل استفاده شده است
# (جستجو برای الگوهایی مثل: db: AsyncSession = Depends(get_something))
match = re.search(r"db:\s*AsyncSession\s*=\s*Depends\((\w+)\)", content)
if match:
    db_dep_name = match.group(1)
    print(f"   ✅ نام Dependency شناسایی شد: {db_dep_name}")
else:
    # اگر پیدا نشد، از نام استاندارد استفاده می‌کنیم
    db_dep_name = "get_db"
    print(f"   ⚠️ نام Dependency یافت نشد، استفاده از مقدار پیش‌فرض: {db_dep_name}")

# ۲. اطمینان از وجود ایمپورت صحیح
import_stmt = f"from apps.shared_core.database.session import {db_dep_name}"
if import_stmt not in content:
    # افزودن ایمپورت به ابتدای فایل
    content = import_stmt + "\n" + content
    print(f"   ✅ ایمپورت '{import_stmt}' به فایل اضافه شد.")

# ۳. اطمینان از وجود ایمپورت AsyncSession
if "from sqlalchemy.ext.asyncio import AsyncSession" not in content:
    content = "from sqlalchemy.ext.asyncio import AsyncSession\n" + content

# ۴. اصلاح خط خراب در تابع delete_user
# جایگزینی هر نسخه خرابی از پارامتر db با نسخه صحیح و هماهنگ
content = re.sub(
    r"db:\s*AsyncSession\s*=\s*Depends\(\w+\),?",
    f"db: AsyncSession = Depends({db_dep_name}),",
    content,
)

# ۵. ذخیره فایل
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("\n🎉 فایل router.py با موفقیت و به صورت هوشمند اصلاح شد.")
print("اکنون تست‌ها باید بدون خطای NameError اجرا شوند.")

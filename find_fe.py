import os

# ۱. پسوندهایی که می‌خواهیم پیدا کنیم
extensions = ('.html', '.css', '.js', '.jsx', '.ts', '.tsx', '.vue', '.scss', '.svelte')

# ۲. پوشه‌هایی که نباید جستجو شوند
skip_dirs = {'node_modules', '.git', 'dist', 'build', '.next', 'coverage'}

found_files = []

# جستجو از پوشه فعلی (.)
for root, dirs, files in os.walk('.'):
    # حذف پوشه‌های اضافی از لیست جستجو برای سرعت بیشتر
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    
    for file in files:
        if file.endswith(extensions):
            # ساخت مسیر کامل فایل
            full_path = os.path.join(root, file)
            found_files.append(full_path)

# چاپ نتایج
print(f"✅ تعداد {len(found_files)} فایل فرانت‌اند پیدا شد:\n")
print("-" * 50)
for f in found_files:
    print(f)
print("-" * 50)
#!/usr/bin/env python3
"""
فرانت‌فایل‌یاب: شناسایی فایل‌های فرانت‌اند در یک پروژه
نحوه اجرا: python3 find_frontend.py [مسیر_پروژه]
"""

import os
import sys
import argparse

# پسوندهای رایج فرانت‌اند
FRONTEND_EXTENSIONS = {
    '.html', '.htm', '.css', '.scss', '.sass', '.less', '.styl',
    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte',
    '.astro', '.mdx'  # در صورت نیاز می‌توانید اضافه/کم کنید
}

# پوشه‌هایی که معمولاً نباید اسکن شوند
EXCLUDE_DIRS = {'node_modules', '.git', 'dist', 'build', 'out', 'coverage', '.cache', 'vendor'}

def find_frontend_files(root_dir: str) -> list[str]:
    results = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # حذف پوشه‌های ناخواسته از پیمایش
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext.lower() in FRONTEND_EXTENSIONS:
                results.append(os.path.join(dirpath, filename))
    return sorted(results)

def main():
    parser = argparse.ArgumentParser(description="شناسایی فایل‌های فرانت‌اند در پروژه")
    parser.add_argument("directory", nargs="?", default=".", help="مسیر ریشه پروژه (پیش‌فرض: پوشه فعلی)")
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"❌ خطا: '{args.directory}' یک پوشه معتبر نیست.", file=sys.stderr)
        sys.exit(1)

    frontend_files = find_frontend_files(args.directory)
    
    if not frontend_files:
        print("🔍 هیچ فایل فرانت‌اندی یافت نشد.")
        return

    print("📁 فایل‌های فرانت‌اند یافت‌شده:")
    print("-" * 60)
    for f in frontend_files:
        print(f)
    print("-" * 60)
    print(f"📊 تعداد کل: {len(frontend_files)} فایل")

if __name__ == "__main__":
    main()
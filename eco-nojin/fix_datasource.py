#!/usr/bin/env python3
"""
Final Micro-Fixer for the last 2 DataSource TypeScript errors.
"""

import re
from pathlib import Path

BASE_DIR = Path(r"D:\econojin.com\eco-nojin\apps\web\src")

files_to_fix = ["pages/DashboardPage.tsx", "pages/EducationPage.tsx"]

print("🔬 Applying final fixes to DataSource types...\n")

for file_rel_path in files_to_fix:
    file_path = BASE_DIR / file_rel_path
    if not file_path.exists():
        print(f"⚠️ File not found: {file_rel_path}")
        continue

    content = file_path.read_text(encoding="utf-8")
    original_content = content

    # الگوی ۱: اگر با 'type DataSource = ...' تعریف شده باشد
    content = re.sub(r"(type\s+DataSource\s*=\s*[^;\n]+)", r'\1 | "error"', content)

    # الگوی ۲: اگر به‌صورت inline در useState تعریف شده باشد (مثلاً useState<"api" | "local">)
    # این الگو هر چیزی را که داخل < > در useState است پیدا کرده و | "error" را به انتهای آن اضافه می‌کند
    content = re.sub(
        r"(useState\s*<\s*[^>]+)(>)",
        lambda m: (
            m.group(1) + ' | "error"' + m.group(2)
            if '| "error"' not in m.group(1)
            else m.group(0)
        ),
        content,
    )

    if content != original_content:
        # ایجاد بکاپ
        backup_path = file_path.with_suffix(file_path.suffix + ".bak2")
        backup_path.write_text(original_content, encoding="utf-8")

        # ذخیره تغییرات
        file_path.write_text(content, encoding="utf-8")
        print(f"✅ Successfully fixed: {file_rel_path}")
        print(f"   💾 Backup saved to: {backup_path.name}")
    else:
        print(
            f"ℹ️ No changes made to: {file_rel_path} (Pattern might be unique, see manual fix below)"
        )

print("\n" + "=" * 60)
print("🚀 Final step: Run 'pnpm --filter web exec tsc --noEmit' to verify 0 errors!")
print("=" * 60)

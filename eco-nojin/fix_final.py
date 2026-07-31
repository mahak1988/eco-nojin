#!/usr/bin/env python3
"""
Final Comprehensive Fix for TypeScript Cascade Errors.
Fixes DataSourceBadge, and reverts incorrect union types in state arrays.
"""

import re
from pathlib import Path

BASE_DIR = Path(r"D:\econojin.com\eco-nojin\apps\web\src")

print("🔬 Starting Final Comprehensive Fix...\n")

# 1. Fix DataSourceBadge.tsx - Add "error" to its internal DataSource type
badge_file = BASE_DIR / "components/ui/DataSourceBadge.tsx"
if badge_file.exists():
    content = badge_file.read_text(encoding="utf-8")
    original = content

    # الگوی 1: اگر type DataSource = "api" | "local" تعریف شده باشد
    content = re.sub(
        r'(type\s+DataSource\s*=\s*["\']api["\']\s*\|\s*["\']local["\'])',
        r'\1 | "error"',
        content,
    )
    # الگوی 2: اگر در interface یا inline type تعریف شده باشد
    content = re.sub(
        r'(source\s*:\s*["\']api["\']\s*\|\s*["\']local["\'])', r'\1 | "error"', content
    )

    if content != original:
        backup = badge_file.with_suffix(".tsx.bak3")
        backup.write_text(original, encoding="utf-8")
        badge_file.write_text(content, encoding="utf-8")
        print("✅ Fixed: DataSourceBadge.tsx (added 'error' to DataSource type)")

# 2. Fix DashboardPage.tsx - Revert apiSource state to proper DataSource type
dash_file = BASE_DIR / "pages/DashboardPage.tsx"
if dash_file.exists():
    content = dash_file.read_text(encoding="utf-8")
    original = content

    # حذف | "error" از state و استفاده از DataSource که اکنون شامل "error" است
    content = re.sub(
        r"const\s+\[apiSource,\s*setApiSource\]\s*=\s*useState<[^>]+>\(",
        r"const [apiSource, setApiSource] = useState<DataSource>(",
        content,
    )

    if content != original:
        backup = dash_file.with_suffix(".tsx.bak3")
        backup.write_text(original, encoding="utf-8")
        dash_file.write_text(content, encoding="utf-8")
        print(
            "✅ Fixed: DashboardPage.tsx (reverted apiSource to proper DataSource type)"
        )

# 3. Fix EducationPage.tsx - Revert array states from union types to pure arrays
edu_file = BASE_DIR / "pages/EducationPage.tsx"
if edu_file.exists():
    content = edu_file.read_text(encoding="utf-8")
    original = content

    # برگرداندن state courses به Course[] (بدون "error")
    content = re.sub(
        r"const\s+\[courses,\s*setCourses\]\s*=\s*useState<[^>]+>\(",
        r"const [courses, setCourses] = useState<Course[]>([]) ; // ",
        content,
    )
    # برگرداندن state paths به LearningPathData[] (بدون "error")
    content = re.sub(
        r"const\s+\[paths,\s*setPaths\]\s*=\s*useState<[^>]+>\(",
        r"const [paths, setPaths] = useState<LearningPathData[]>([]) ; // ",
        content,
    )
    # اصلاح setCourses و setPaths که از union type خارج شده‌اند
    # این الگو مطمئن می‌شود که prev همیشه آرایه است
    content = re.sub(
        r"setCourses\(\(prev\)\s*=>\s*prev\.map",
        r"setCourses((prev: Course[]) => prev.map",
        content,
    )
    content = re.sub(
        r"setPaths\(\(prev\)\s*=>\s*prev\.map",
        r"setPaths((prev: LearningPathData[]) => prev.map",
        content,
    )

    if content != original:
        backup = edu_file.with_suffix(".tsx.bak3")
        backup.write_text(original, encoding="utf-8")
        edu_file.write_text(content, encoding="utf-8")
        print("✅ Fixed: EducationPage.tsx (reverted array states to pure arrays)")

print("\n" + "=" * 60)
print("🚀 Final step: Run 'pnpm --filter web exec tsc --noEmit' to verify!")
print("=" * 60)

#!/usr/bin/env python3
"""
TypeScript Error Auto-Fixer for eco-nojin
Automatically applies targeted regex replacements to fix 11 specific TSC errors.
"""

import re
from pathlib import Path

# مسیر دقیق پوشه src پروژه وب
BASE_DIR = Path(r"D:\econojin.com\eco-nojin\apps\web\src")

# تعریف دقیق فایل‌ها و الگوهای جایگزینی
FIXES = [
    {
        "file": "components/Layout/Header.tsx",
        "desc": "Fix Record<string, string> casting error",
        "patterns": [
            (r"\(t as Record<string, string>\)", r"(t as any)"),
        ],
    },
    {
        "file": "components/science/ScienceMLPanel.tsx",
        "desc": "Fix unknown type rendering in pre tag",
        "patterns": [
            (r"\{pred\?\.train && \(", r"{pred?.train != null && ("),
            (
                r"(<pre[^>]*>\s*\{)\s*pred\.train\s*(\}\s*</pre>)",
                r"\1String(pred.train)\2",
            ),
        ],
    },
    {
        "file": "pages/DashboardPage.tsx",
        "desc": "Add 'error' to DataSource type",
        "patterns": [
            (r"(type\s+DataSource\s*=\s*[^\n;]+)", r'\1 | "error"'),
            (r'(useState<\s*"[^"]+")', r'\1 | "error"'),  # Fallback for inline types
        ],
    },
    {
        "file": "pages/EducationPage.tsx",
        "desc": "Add 'error' to DataSource type (if defined inline)",
        "patterns": [
            (r"(type\s+DataSource\s*=\s*[^\n;]+)", r'\1 | "error"'),
            (r'(useState<\s*"[^"]+")', r'\1 | "error"'),
        ],
    },
    {
        "file": "pages/MonitoringHubPage.tsx",
        "desc": "Wrap unknown 'l' variable in String()",
        "patterns": [
            (
                r'(<p className="text-xs text-stone-400">\s*)\{l\}(\s*</p>)',
                r"\1{String(l)}\2",
            ),
        ],
    },
    {
        "file": "pages/MonitoringSoilPage.tsx",
        "desc": "Wrap unknown 'l' variable in String()",
        "patterns": [
            (
                r'(<p className="text-xs text-stone-400">\s*)\{l\}(\s*</p>)',
                r"\1{String(l)}\2",
            ),
        ],
    },
    {
        "file": "pages/SciencePage.tsx",
        "desc": "Fix unknown type condition for persist_error",
        "patterns": [
            (r"\{result\.persist_error &&", r"{result.persist_error != null &&"),
        ],
    },
    {
        "file": "pages/SimulatorDetailPage.tsx",
        "desc": "Fix unknown type condition for advice_fa",
        "patterns": [
            (r"\{analysis\.advice_fa &&", r"{analysis.advice_fa != null &&"),
        ],
    },
]


def apply_fixes():
    print("🔬 Starting TypeScript Error Auto-Fix...\n")
    total_fixed = 0

    for fix in FIXES:
        file_path = BASE_DIR / fix["file"]

        if not file_path.exists():
            print(f"⚠️  File not found: {fix['file']}")
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            original_content = content
            changes_made = 0

            for pattern, replacement in fix["patterns"]:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    changes_made += count
                    print(
                        f"  ✅ Applied '{fix['desc']}' ({count} time(s)) in {fix['file']}"
                    )

            if content != original_content:
                # Create backup before overwriting
                backup_path = file_path.with_suffix(file_path.suffix + ".bak")
                backup_path.write_text(original_content, encoding="utf-8")

                # Write fixed content
                file_path.write_text(content, encoding="utf-8")
                total_fixed += 1
                print(f"  💾 Backup saved to: {backup_path.name}")
            else:
                print(f"  ℹ️  No changes needed for: {fix['file']}")

        except Exception as e:
            print(f"  ❌ Error processing {fix['file']}: {e}")

    print("\n" + "=" * 60)
    if total_fixed > 0:
        print(f"🎉 SUCCESS: Modified {total_fixed} file(s) successfully.")
        print("💡 Run 'pnpm --filter web exec tsc --noEmit' to verify 0 errors.")
    else:
        print("✅ All files were already up to date or patterns not found.")
    print("=" * 60)


if __name__ == "__main__":
    apply_fixes()

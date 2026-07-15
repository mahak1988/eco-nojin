#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Fix QueryClientProvider in main.tsx
================================================
رفع خطای "No QueryClient set" با افزودن QueryClientProvider

این اسکریپت:
✅ فایل main.tsx را اصلاح می‌کند
✅ QueryClientProvider را اضافه می‌کند
✅ import های لازم را می‌افزاید
✅ ساختار provider chain را اصلاح می‌کند
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "apps" / "web" / "src"

def main():
    print("\n" + "=" * 70)
    print("🔧 Fix QueryClientProvider in main.tsx")
    print("=" * 70)
    
    main_file = SRC_DIR / "main.tsx"
    
    if not main_file.exists():
        print(f"\n❌ main.tsx not found at: {main_file}")
        return
    
    # Backup
    backup_path = main_file.with_suffix(".tsx.backup")
    try:
        import shutil
        shutil.copy2(main_file, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")
    except Exception as e:
        print(f"\n⚠️  Backup failed: {e}")
    
    # Read current content
    try:
        content = main_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"\n❌ Failed to read main.tsx: {e}")
        return
    
    # Check if already fixed
    if "QueryClientProvider" in content:
        print("\n⏩ QueryClientProvider already exists in main.tsx")
        return
    
    # Step 1: Add imports
    print("\n📝 Step 1: Adding imports...")
    
    # Find the last import line
    lines = content.split("\n")
    last_import_idx = -1
    
    for i, line in enumerate(lines):
        if line.startswith("import "):
            last_import_idx = i
    
    if last_import_idx == -1:
        print("   ❌ No imports found")
        return
    
    # Add new imports after last import
    new_imports = [
        'import { QueryClientProvider } from "@tanstack/react-query";',
        'import { queryClient } from "@/lib/query-client";',
    ]
    
    for imp in new_imports:
        if imp not in content:
            lines.insert(last_import_idx + 1, imp)
            last_import_idx += 1
            print(f"   ✅ Added: {imp[:50]}...")
    
    content = "\n".join(lines)
    
    # Step 2: Wrap App with QueryClientProvider
    print("\n📝 Step 2: Wrapping App with QueryClientProvider...")
    
    # Find ReactDOM.createRoot and render
    if "ReactDOM.createRoot" in content:
        # Pattern 1: Modern React 18+
        # ReactDOM.createRoot(...).render(<App />)
        content = content.replace(
            ".render(<App />)",
            '.render(\n  <QueryClientProvider client={queryClient}>\n    <App />\n  </QueryClientProvider>\n)'
        )
        print("   ✅ Wrapped App with QueryClientProvider (React 18+)")
    elif "ReactDOM.render" in content:
        # Pattern 2: Legacy React
        content = content.replace(
            "ReactDOM.render(<App />",
            "ReactDOM.render(\n  <QueryClientProvider client={queryClient}>\n    <App />\n  </QueryClientProvider>"
        )
        print("   ✅ Wrapped App with QueryClientProvider (Legacy)")
    else:
        print("   ⚠️  Could not find ReactDOM.render pattern")
        print("   📌 Manual fix required")
    
    # Step 3: Write back
    try:
        main_file.write_text(content, encoding="utf-8")
        print(f"\n✅ main.tsx updated successfully")
    except Exception as e:
        print(f"\n❌ Failed to write main.tsx: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✅ Fix completed!")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Restart dev server: Ctrl+C, then pnpm dev")
    print("   2. Check browser console for errors")
    print("   3. If error persists, send the new error message")


if __name__ == "__main__":
    main()
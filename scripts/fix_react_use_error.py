#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Webpack Cache Error: Cannot find module './vendor-chunks/@opentelemetry.js'
================================================================================
این خطا معمولاً به دلیل کش خراب Next.js رخ می‌دهد.
r"""

import shutil
import sys
from pathlib import Path

FRONTEND_DIR = Path(r"D:\econojin.com\frontend")


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_success(msg):
    print(f"✓ {msg}")


def print_error(msg):
    print(f"✗ {msg}")


def print_info(msg):
    print(f"ℹ {msg}")


def main():
    print_header("🔧 FIX WEBPACK CACHE ERROR")

    # لیست پوشه‌هایی که باید حذف شوند
    dirs_to_clean = [
        FRONTEND_DIR / ".next",
        FRONTEND_DIR / "node_modules" / ".cache",
        FRONTEND_DIR / ".swc",
    ]

    cleaned = 0
    for dir_path in dirs_to_clean:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
                print_success(f"Deleted: {dir_path.relative_to(FRONTEND_DIR)}")
                cleaned += 1
            except Exception as e:
                print_error(f"Failed to delete {dir_path}: {e}")
        else:
            print_info(f"Already clean: {dir_path.relative_to(FRONTEND_DIR)}")

    print_header("📊 SUMMARY")
    print_success(f"Cleaned {cleaned} directories")

    print_info("\n📋 Next steps:")
    print(f"  1. cd {FRONTEND_DIR}")
    print("  2. npm run dev")
    print("  3. Wait for fresh build (~10-30 seconds)")
    print("  4. Test: http://localhost:3000/fa")

    print_info("\n💡 اگر خطا ادامه داشت:")
    print("  • node_modules را هم حذف و reinstall کنید:")
    print("    rm -r node_modules package-lock.json && npm install")
    print("  • مطمئن شوید Next.js نسخه 15.0.5+ است:")
    print("    npm list next")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

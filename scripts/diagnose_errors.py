#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تشخیص دقیق همه SyntaxError های باقی‌مانده
r"""

import ast
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


sys.path.insert(0, str(Path(__file__).parent.parent))

PROJECT_ROOT = Path(r"D:\econojin.com")


def find_all_syntax_errors():
    """پیدا کردن همه SyntaxError ها با جزئیات"""
    errors = []
    checked = 0

    IGNORE = [
        ".venv",
        "node_modules",
        "__pycache__",
        ".backup",
        ".emergency_backup",
        ".syntax_backup",
        ".warnings_backup",
        "site-packages",
    ]

    for py_file in PROJECT_ROOT.rglob("*.py"):
        if any(p in str(py_file) for p in IGNORE):
            continue

        checked += 1

        try:
            content = py_file.read_text(encoding="utf-8")
            ast.parse(content)
        except SyntaxError as e:
            # خواندن خط خطا
            try:
                lines = content.split("\n")
                error_line = lines[e.lineno - 1] if e.lineno <= len(lines) else ""
                context_start = max(0, e.lineno - 3)
                context_end = min(len(lines), e.lineno + 2)
                context = lines[context_start:context_end]
            except Exception:
                error_line = ""
                context = []

            errors.append(
                {
                    "file": str(py_file.relative_to(PROJECT_ROOT)),
                    "line": e.lineno,
                    "column": e.offset,
                    "message": e.msg,
                    "error_line": error_line,
                    "context": context,
                    "context_start": context_start + 1,
                }
            )
        except Exception as e:
            errors.append(
                {"file": str(py_file.relative_to(PROJECT_ROOT)), "error": f"Read error: {e}"}
            )

    return errors, checked


def categorize_errors(errors):
    """دسته‌بندی خطاها برای رفع خودکار"""
    categories = {"backup_files": [], "auto_generated": [], "test_files": [], "main_code": []}

    for err in errors:
        file_path = err["file"]

        if "backup" in file_path or ".bak" in file_path:
            categories["backup_files"].append(err)
        elif file_path.startswith("tests/") or "test_" in file_path:
            categories["test_files"].append(err)
        elif "generated" in file_path or "temp" in file_path:
            categories["auto_generated"].append(err)
        else:
            categories["main_code"].append(err)

    return categories


def main():
    logger.info("=" * 70)
    logger.info("  DIAGNOSTIC - شناسایی دقیق Syntax Errors")
    logger.info("=" * 70)

    errors, checked = find_all_syntax_errors()

    logger.info(f"\n  Checked: {checked} files")
    logger.info(f"  Errors found: {len(errors)}")

    if not errors:
        logger.info("\n  [OK] No syntax errors!")
        return

    # دسته‌بندی
    categories = categorize_errors(errors)

    logger.info("\n" + "-" * 70)
    logger.info("  CATEGORIZATION:")
    logger.info("-" * 70)
    for cat, items in categories.items():
        logger.info(f"  {cat}: {len(items)} files")

    # نمایش جزئیات
    logger.info("\n" + "-" * 70)
    logger.info("  DETAILED ERRORS:")
    logger.info("-" * 70)

    for i, err in enumerate(errors, 1):
        logger.info(f"\n  [{i}] {err['file']}")
        if "line" in err:
            logger.info(f"      Line {err['line']}, Col {err['column']}: {err['message']}")
            logger.info(f"      Code: {err['error_line'][:100]}")

            if err["context"]:
                logger.info(f"      Context (around line {err['context_start']}):")
                for j, line in enumerate(err["context"], err["context_start"]):
                    marker = ">>> " if j == err["line"] else "    "
                    logger.info(f"      {marker}{j:4d}: {line[:80]}")
        else:
            logger.info(f"      {err.get('error', 'Unknown error')}")

    # ذخیره گزارش JSON
    report_file = PROJECT_ROOT / "reports" / "syntax_errors.json"
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": datetime.now().isoformat(),
                "total_checked": checked,
                "total_errors": len(errors),
                "categories": {k: len(v) for k, v in categories.items()},
                "errors": errors,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    logger.info("\n" + "=" * 70)
    logger.info(f"  Report saved: {report_file}")
    logger.info("=" * 70)

    # پیشنهاد راه‌حل
    logger.info("\n  SUGGESTED ACTIONS:")
    if categories["backup_files"]:
        logger.info(f"    [AUTO-DELETE] {len(categories['backup_files'])} backup files")
    if categories["test_files"]:
        logger.info(f"    [REGENERATE] {len(categories['test_files'])} test files")
    if categories["main_code"]:
        logger.info(f"    [MANUAL-FIX] {len(categories['main_code'])} main code files")


if __name__ == "__main__":
    main()

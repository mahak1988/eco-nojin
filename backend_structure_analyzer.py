from pathlib import Path
import json
from collections import defaultdict
from typing import Dict, List, Any

# ریشهٔ پروژه (بدون نیاز به ویرایش دستی)
PROJECT_ROOT = Path(r"D:\econojin.com")

# دایرکتوری‌هایی که به‌عنوان «بک‌اند» در نظر می‌گیریم
BACKEND_DIRS = ["api", "backend", "core", "scripts"]

# فایل خروجی گزارش
OUTPUT_JSON = PROJECT_ROOT / "backend_structure_report.json"

# پوشه‌هایی که نباید پیمایش شوند (بکاپ‌ها و کش‌ها و ...)
IGNORE_DIR_KEYWORDS = [
    "_backup",
    ".git",
    "__pycache__",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".turbo",
]


def is_ignored(path: Path) -> bool:
    """
    تشخیص اینکه مسیر نباید پیمایش شود (بر اساس نام پوشه‌ها).
    """
    for part in path.parts:
        for key in IGNORE_DIR_KEYWORDS:
            if key in part:
                return True
    return False


def collect_backend_files(root: Path) -> List[Path]:
    """
    جمع‌آوری همهٔ فایل‌های پایتون در دایرکتوری‌های بک‌اند تعریف‌شده.
    """
    files: List[Path] = []
    for dirname in BACKEND_DIRS:
        base = root / dirname
        if not base.exists():
            continue
        for f in base.rglob("*.py"):
            if is_ignored(f):
                continue
            files.append(f)
    return files


def group_by_module(root: Path, files: List[Path]) -> Dict[str, Any]:
    """
    گروه‌بندی فایل‌ها بر اساس ساختار ماژول:
    - سطح اول: دایرکتوری اصلی (api / backend / core / scripts)
    - سطح دوم: زیرمسیر ماژول (مثلاً water/, economics/, auth/ یا '.')
    - لیست فایل‌ها در هر ماژول.
    """
    structure: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))

    for f in files:
        rel = f.relative_to(root).as_posix()
        parts = rel.split("/")

        if len(parts) == 1:
            # فایل مستقیم زیر ریشه (در عمل برای ما مهم نیست، ولی ثبت می‌کنیم)
            top = "."
            module_path = "."
            filename = parts[0]
        else:
            top = parts[0]  # مثلاً api / backend / core / scripts
            if len(parts) == 2:
                # مانند api/main.py
                module_path = "."
                filename = parts[1]
            else:
                # مانند api/modules/water/router.py
                module_path = "/".join(parts[1:-1]) or "."
                filename = parts[-1]

        structure[top][module_path].append(filename)

    # مرتب‌سازی برای خوانایی
    sorted_structure: Dict[str, Any] = {}
    for top, modules in sorted(structure.items()):
        sorted_modules: Dict[str, List[str]] = {}
        for module_path, filenames in sorted(modules.items()):
            sorted_modules[module_path] = sorted(filenames)
        sorted_structure[top] = sorted_modules

    return sorted_structure


def summarize_backend(root: Path) -> Dict[str, Any]:
    """
    تولید خلاصهٔ ساختار بک‌اند برای مصرف در طراحی فرانت‌اند.
    """
    files = collect_backend_files(root)

    structure = group_by_module(root, files)

    summary: Dict[str, Any] = {
        "project_root": str(root.resolve()),
        "backend_dirs": BACKEND_DIRS,
        "total_backend_files": len(files),
        "modules": structure,
    }
    return summary


def pretty_print(summary: Dict[str, Any]) -> None:
    """
    چاپ خلاصهٔ کوتاه روی کنسول برای مشاهدهٔ سریع.
    """
    print("=" * 80)
    print("BACKEND STRUCTURE REPORT")
    print("=" * 80)
    print(f"Root: {summary['project_root']}")
    print(f"Backend dirs: {', '.join(summary['backend_dirs'])}")
    print(f"Total backend Python files: {summary['total_backend_files']}")

    print("\nTop-level backend modules and example submodules:")
    modules = summary.get("modules", {})
    for top_name, submods in modules.items():
        submod_names = list(submods.keys())
        example_submods = ", ".join(submod_names[:5])
        print(f"  - {top_name}: {len(submod_names)} submodules (e.g. {example_submods})")

    print("=" * 80)
    print(f"Full JSON report saved to: {OUTPUT_JSON}")
    print("=" * 80)


def main() -> None:
    if not PROJECT_ROOT.exists():
        raise FileNotFoundError(f"Project root not found: {PROJECT_ROOT}")

    summary = summarize_backend(PROJECT_ROOT)

    # ذخیرهٔ گزارش کامل به صورت JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # چاپ خلاصه روی کنسول
    pretty_print(summary)


if __name__ == "__main__":
    main()
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# کلمات کلیدی مرتبط با ماژول آب و خاک / LDN
KEYWORDS = [
    "land_soil_water",
    "land-soil-water",
    "soilwater",
    "ldn",
]

API_ROOT_CANDIDATES = ["api", "backend", "backend-api"]
WEB_ROOT_CANDIDATES = ["web", "frontend", "apps/web"]


def is_interesting_path(path: Path) -> bool:
    low = str(path).lower().replace("\\", "/")
    return any(k in low for k in KEYWORDS)


def find_interesting_files():
    interesting = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # نادیده گرفتن venv و node_modules و pnpm-store
        if any(skip in dirpath.lower() for skip in [".venv", "venv", "node_modules", "pnpm-store"]):
            continue
        for name in filenames:
            if name.endswith((".py", ".ts", ".tsx", ".jsx")):
                full = Path(dirpath) / name
                if is_interesting_path(full):
                    interesting.append(full.relative_to(ROOT))
    return sorted(interesting)


def classify_path(rel: Path):
    parts = rel.parts
    # ساده: اگر اولین جزء api است → بک‌اند اصلی
    if len(parts) > 0 and parts[0].lower() in [c.lower() for c in API_ROOT_CANDIDATES]:
        return "API_MAIN"
    # اگر زیر web یا frontend است → فرانت‌اند اصلی
    if len(parts) > 0 and parts[0].lower() in [c.split("/")[0].lower() for c in WEB_ROOT_CANDIDATES]:
        return "WEB_MAIN"
    # اگر زیر apps/ یا appi/ است → شاخه فرعی
    if len(parts) > 0 and parts[0].lower() in ["apps", "appi"]:
        return "SIDE_BRANCH"
    return "OTHER"


def scan_imports_for(file_rel: Path):
    """ببینیم این فایل در main / روترهای اصلی import شده یا نه."""
    api_main = ROOT / "api" / "main.py"
    results = []
    if api_main.exists():
        text = api_main.read_text(encoding="utf-8", errors="ignore")
        low = text.lower()
        module_like = (
            str(file_rel.with_suffix(""))
            .replace("\\", ".")
            .replace("/", ".")
            .lower()
        )
        short_name = file_rel.stem.lower()
        if short_name in low or module_like in low:
            results.append(f"api/main.py imports something matching '{short_name}' or '{module_like}'")
    # می‌توانیم فایل‌های روتر دیگر را هم نگاه کنیم
    api_modules = ROOT / "api" / "modules"
    if api_modules.exists():
        for p in api_modules.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore").lower()
            module_like = (
                str(file_rel.with_suffix(""))
                .replace("\\", ".")
                .replace("/", ".")
                .lower()
            )
            short_name = file_rel.stem.lower()
            if short_name in text or module_like in text:
                rel_router = p.relative_to(ROOT)
                results.append(f"{rel_router} imports something matching '{short_name}' or '{module_like}'")
    return results


def main():
    files = find_interesting_files()
    print("=== Soil/Water/LDN related files ===")
    if not files:
        print("No interesting files found.")
        return

    for rel in files:
        category = classify_path(rel)
        print(f"- {rel}  [{category}]")
        if category in ("API_MAIN", "SIDE_BRANCH"):
            imports = scan_imports_for(rel)
            for imp in imports:
                print(f"    -> {imp}")

    print("\nHint:")
    print("  - فایل‌هایی که [SIDE_BRANCH] هستند ولی هیچ import در api/main.py یا api/modules/* ندارند،")
    print("    فعلاً به بک‌اند اصلی وصل نیستند و در عمل ‘مسیر انحرافی’ حساب می‌شوند.")
    print("  - فایل‌های [API_MAIN] متصل به بک‌اند اصلی هستند (اگر import تشخیص داده شده باشد).")


if __name__ == '__main__':
    main()
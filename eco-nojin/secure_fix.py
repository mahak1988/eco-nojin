#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
  secure_fix.py — اسکریپت اصلاح و ایمن‌سازی پروژه econojin
═══════════════════════════════════════════════════════════════════════════
اقدامات:
  ۱. اصلاح تنظیمات Git (حذف core.hooksPath، بازگرداندن remote origin)
  ۲. راه‌اندازی pre-commit hook محلی (بدون نیاز به gitleaks/winget)
  ۳. به‌روزرسانی .gitignore و حذف فایل‌های حساس از tracking
  ۴. پاکسازی backupها و فایل‌های موقت
  ۵. گزارش فایل‌های نیازمند اصلاح دستی

استفاده:
  python secure_fix.py                          # فقط گزارش (بدون تغییر)
  python secure_fix.py --apply                  # اعمال تغییرات امن
  python secure_fix.py --apply --delete-backups # + حذف backupها
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
ORIGIN_URL = "https://github.com/mahak1988/eco-nojin.git"

# فایل‌هایی که باید از git tracking حذف شوند (روی دیسک می‌مانند)
UNTRACK_PATTERNS = [".env", ".env.bak", "*.log", "reports/guardian_*.md"]

# دایرکتوری‌های backup/موقت که باید حذف شوند
BACKUP_DIR_PATTERNS = [".sync_backup_*", "__repo_sync_tmp__"]

GITIGNORE_ENTRIES = [
    "# ── Secrets & environment ──",
    ".env", ".env.*", "!.env.example",
    "*.pem", "*.key", "*.p12", "*.pfx",
    "# ── Backups & temp ──",
    ".sync_backup_*/", "__repo_sync_tmp__/", "*.bak",
    "# ── Dependencies & stores ──",
    ".pnpm-store/", "node_modules/",
    "# ── Reports with potential secrets ──",
    "reports/guardian_*.md",
    "# ── Logs ──",
    "*.log",
]

PRECOMMIT_CONFIG = """\
repos:
  - repo: local
    hooks:
      - id: secure-project-analyzer
        name: Secure Project Analyzer (secret scan)
        entry: python project_analyzer.py . --no-network --no-git --fail-on critical
        language: system
        pass_filenames: false
        always_run: true
        stages: [pre-commit]
"""


# ──────────────────────────── توابع کمکی ────────────────────────────
def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    """اجرای امن دستور git (بدون shell، با timeout)."""
    return subprocess.run(["git", "-C", str(REPO_ROOT), *args],
                          capture_output=True, text=True, check=check, timeout=60)


def is_git_repo() -> bool:
    r = git("rev-parse", "--is-inside-work-tree", check=False)
    return r.returncode == 0 and r.stdout.strip() == "true"


def step(num: str, title: str) -> None:
    print(f"\n{'─' * 62}\n  [{num}] {title}\n{'─' * 62}")


def ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def warn(msg: str) -> None:
    print(f"  ⚠️  {msg}")


def info(msg: str) -> None:
    print(f"  ℹ️  {msg}")


# ──────────────────────────── اقدامات ────────────────────────────
def fix_git_config(apply: bool) -> None:
    step("۱", "اصلاح تنظیمات Git")

    # الف) حذف core.hooksPath (مانع نصب pre-commit است)
    r = git("config", "--get", "core.hooksPath", check=False)
    if r.returncode == 0 and r.stdout.strip():
        warn(f"core.hooksPath = {r.stdout.strip()} (باید حذف شود)")
        if apply:
            git("config", "--unset-all", "core.hooksPath", check=False)
            ok("core.hooksPath حذف شد")
    else:
        ok("core.hooksPath تنظیم نیست")

    # ب) بازگرداندن remote origin (توسط git filter-repo حذف شده)
    r = git("remote", "get-url", "origin", check=False)
    if r.returncode != 0:
        warn("remote origin موجود نیست")
        info(f"افزودن: {ORIGIN_URL}")
        if apply:
            git("remote", "add", "origin", ORIGIN_URL, check=False)
            ok("remote origin افزوده شد")
    else:
        ok(f"origin = {r.stdout.strip()}")


def setup_precommit(apply: bool) -> None:
    step("۲", "راه‌اندازی pre-commit hook محلی (جایگزین gitleaks)")
    config = REPO_ROOT / ".pre-commit-config.yaml"

    if apply:
        config.write_text(PRECOMMIT_CONFIG, encoding="utf-8")
        ok(f"{config.name} نوشته شد (از project_analyzer.py استفاده می‌کند)")
        r = subprocess.run([sys.executable, "-m", "pre_commit", "install"],
                           capture_output=True, text=True, cwd=REPO_ROOT)
        if r.returncode == 0:
            ok("hook نصب شد — از این پس هر commit اسکن می‌شود")
        else:
            warn(f"نصب hook ناموفق: {r.stderr.strip()}")
            info("به‌صورت دستی اجرا کنید: pre-commit install")
    else:
        info(f"نوشتن {config.name} و اجرای `pre-commit install`")
        info("hook محلی، project_analyzer.py را پیش از هر commit اجرا می‌کند")


def update_gitignore(apply: bool) -> None:
    step("۳", "به‌روزرسانی .gitignore و حذف فایل‌های حساس از tracking")
    gitignore = REPO_ROOT / ".gitignore"
    existing = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    existing_lines = set(existing.splitlines())

    missing = [e for e in GITIGNORE_ENTRIES
               if not e.startswith("#") and e not in existing_lines]
    if missing:
        warn(f"{len(missing)} الگوی مفقود در .gitignore:")
        for m in missing:
            print(f"     + {m}")
        if apply:
            with gitignore.open("a", encoding="utf-8") as f:
                f.write("\n# ── Added by secure_fix.py ──\n")
                for e in GITIGNORE_ENTRIES:
                    if e not in existing_lines:
                        f.write(e + "\n")
            ok(".gitignore به‌روزرسانی شد")
    else:
        ok(".gitignore کامل است")

    # حذف فایل‌های حساس از tracking (فایل‌ها روی دیسک می‌مانند)
    for pattern in UNTRACK_PATTERNS:
        r = git("ls-files", pattern, check=False)
        tracked = [f for f in r.stdout.splitlines() if f.strip()]
        if tracked:
            warn(f"{len(tracked)} فایل tracked حساس ({pattern}):")
            for f in tracked[:5]:
                print(f"     - {f}")
            if len(tracked) > 5:
                print(f"     … و {len(tracked) - 5} مورد دیگر")
            if apply:
                git("rm", "--cached", "-r", "--ignore-unmatch", *tracked, check=False)
                ok("از tracking حذف شدند (روی دیسک باقی‌اند)")


def cleanup_backups(apply: bool, delete: bool) -> None:
    step("۴", "پاکسازی backupها و فایل‌های موقت")
    found: list[Path] = []
    for pattern in BACKUP_DIR_PATTERNS:
        found.extend(p for p in REPO_ROOT.glob(pattern))
    env_bak = REPO_ROOT / ".env.bak"
    if env_bak.exists():
        found.append(env_bak)

    if not found:
        ok("هیچ backup/temp یافت نشد")
        return

    for d in found:
        kind = "دایرکتوری" if d.is_dir() else "فایل"
        warn(f"{d.name} ({kind})")

    if delete and apply:
        for d in found:
            try:
                if d.is_dir():
                    shutil.rmtree(d, ignore_errors=True)
                else:
                    d.unlink(missing_ok=True)
                print(f"     🗑️  حذف شد: {d.name}")
            except OSError as exc:
                warn(f"حذف {d.name} ناموفق: {exc}")
        ok("پاکسازی کامل شد")
    elif not delete:
        info("برای حذف، از --delete-backups استفاده کنید")


def report_manual_fixes() -> None:
    step("۵", "فایل‌های نیازمند اصلاح دستی")
    report_path = REPO_ROOT / "project-analysis.json"
    if not report_path.exists():
        info("ابتدا project_analyzer.py را اجرا کنید تا گزارش تولید شود")
        return

    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"خواندن گزارش ناموفق: {exc}")
        return

    # فقط یافته‌های واقعی (حذف نویز storeها و backupها)
    noise = (".pnpm-store", "__repo_sync_tmp__", ".sync_backup_", "node_modules")
    findings = [f for f in data.get("findings", [])
                if f["severity"] in ("critical", "high")
                and not f["file"].startswith(noise)]

    if not findings:
        ok("هیچ یافته بحرانی/زیاد واقعی باقی نمانده است")
        return

    by_file: dict[str, list[dict]] = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    for file, items in sorted(by_file.items()):
        print(f"\n  📄 {file}")
        for it in items:
            print(f"     خط {it['line']}: {it['title']}")

    print("\n  📋 راهنمای اصلاح (به ترتیب اولویت):")
    print("     ۱. 🔴 رمزهای واقعی را ROTATE کنید (DB prod، QDRANT_API_KEY، superuser)")
    print("     ۲. مقادیر hardcode را با ${VAR} یا os.getenv('VAR') جایگزین کنید")
    print("     ۳. رمزهای تست/README کم‌اهمیت‌اند؛ می‌توانید mask یا حذف کنید")


def final_reminders() -> None:
    print(f"\n{'═' * 62}")
    print("  ⚠️  اقدامات دستی ضروری (خودکار نمی‌شوند):")
    print("─" * 62)
    print("  ۱. ROTATE کردن همه رمزهای لو‌رفته:")
    print("     • رمز دیتابیس Production (docker-compose.prod.yml)")
    print("     • QDRANT_API_KEY (.env)")
    print("     • FIRST_SUPERUSER_PASSWORD (config.py)")
    print("     • رمز دیتابیس test/CI (workflowها)")
    print()
    print("  ۲. push تاریخچه بازنویسی‌شده به GitHub (با احتیاط):")
    print("     git push --force --set-upstream origin main")
    print("     ⚠️  اگر repo تیمی است، ابتدا با تیم هماهنگ کنید")
    print()
    print("  ۳. اگر repo عمومی است، GitHub Secret Scanning را فعال کنید")
    print("═" * 62)


# ──────────────────────────── main ────────────────────────────
def main() -> int:
    p = argparse.ArgumentParser(
        description="اسکریپت اصلاح امنیتی پروژه econojin",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=("نمونه‌ها:\n"
                "  python secure_fix.py                          # فقط گزارش\n"
                "  python secure_fix.py --apply                  # اعمال تغییرات\n"
                "  python secure_fix.py --apply --delete-backups # + حذف backupها\n"),
    )
    p.add_argument("--apply", action="store_true",
                   help="اعمال تغییرات (پیش‌فرض: فقط گزارش)")
    p.add_argument("--delete-backups", action="store_true",
                   help="حذف دایرکتوری‌های backup و .env.bak")
    args = p.parse_args()

    print("═" * 62)
    print("  🔧 اسکریپت اصلاح امنیتی — econojin.com")
    print("═" * 62)

    if not is_git_repo():
        print("  ❌ این دایرکتوری یک مخزن git نیست")
        return 2

    if not args.apply:
        info("حالت گزارش — برای اعمال تغییرات: --apply")

    fix_git_config(args.apply)
    setup_precommit(args.apply)
    update_gitignore(args.apply)
    cleanup_backups(args.apply, args.delete_backups)
    report_manual_fixes()
    final_reminders()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

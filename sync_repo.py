#!/usr/bin/env python3
"""
=============================================================================
  Econojin Repository Sync Script  v2.0
  ─────────────────────────────────────
  همگام‌سازی پروژه محلی با مخزن GitHub:
    • جایگزینی فایل‌های موجود با نسخه مخزن (با مقایسه SHA-256)
    • استخراج فایل‌های جدید (موجود در مخزن ولی نه در پروژه)
    • پشتیبان‌گیری خودکار قبل از هر تغییر
    • گزارش تفصیلی (Console + JSON)

  Usage:
    python sync_repo.py                     # sync با پشتیبان‌گیری
    python sync_repo.py --dry-run           # فقط پیش‌نمایش، بدون تغییر
    python sync_repo.py --no-backup         # بدون پشتیبان‌گیری
    python sync_repo.py --branch develop    # شاخه دیگر
    python sync_repo.py --project D:\proj   # مسیر سفارشی
=============================================================================
"""

import argparse
import hashlib
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
#  Configuration
# ─────────────────────────────────────────────────────────────────────────────

REPO_URL       = "https://github.com/mahak1988/eco-nojin.git"
DEFAULT_BRANCH = "main"
PROJECT_ROOT   = Path(r"D:\econojin.com")

# پوشه‌هایی که هرگز همگام‌سازی نمی‌شوند
EXCLUDE_DIRS: set[str] = {
    ".git",
    "node_modules",
    ".pnpm-store",
    "repos",              # مخازن مرجع (shadcn-ui, fastapi-template, ...)
    ".venv",
    "__pycache__",
    ".next",
    "dist",
    "build",
    ".turbo",
    ".cache",
    ".idea",
    ".vs",
    ".sync_backup_",      # پوشه‌های پشتیبان قبلی
}

# فایل‌هایی که هرگز رونویسی نمی‌شوند
EXCLUDE_FILES: set[str] = {
    ".env",               # secrets محلی
    ".env.local",
    "econojin.db",        # دیتابیس محلی SQLite
}

# ─────────────────────────────────────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────────────────────────────────────

LOG_FORMAT = "%(asctime)s │ %(levelname)-7s │ %(message)s"
LOG_DATE   = "%H:%M:%S"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATE)
log = logging.getLogger("repo-sync")

# ─────────────────────────────────────────────────────────────────────────────
#  Data Models
# ─────────────────────────────────────────────────────────────────────────────

class Action(Enum):
    REPLACE  = "REPLACE"
    NEW      = "NEW"
    SKIP     = "SKIP"
    EXCLUDED = "EXCLUDED"


@dataclass
class FileRecord:
    rel_path: str
    action:   Action
    src_size: int = 0
    dst_size: int = 0
    src_hash: str = ""
    dst_hash: str = ""
    error:    str = ""


@dataclass
class SyncReport:
    started_at:   str  = ""
    finished_at:  str  = ""
    branch:       str  = ""
    dry_run:      bool = False
    total_scanned: int  = 0
    replaced:     list[FileRecord] = field(default_factory=list)
    new_files:    list[FileRecord] = field(default_factory=list)
    identical:    list[FileRecord] = field(default_factory=list)
    excluded:     list[FileRecord] = field(default_factory=list)
    errors:       list[FileRecord] = field(default_factory=list)
    backup_dir:   str  = ""

    @property
    def n_replaced(self) -> int:  return len(self.replaced)
    @property
    def n_new(self) -> int:       return len(self.new_files)
    @property
    def n_identical(self) -> int: return len(self.identical)
    @property
    def n_excluded(self) -> int:  return len(self.excluded)
    @property
    def n_errors(self) -> int:    return len(self.errors)

# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def file_sha256(path: Path, chunk: int = 1 << 16) -> str:
    """SHA-256 به‌صورت streaming — مناسب فایل‌های بزرگ."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while block := f.read(chunk):
                h.update(block)
        return h.hexdigest()
    except (OSError, PermissionError) as exc:
        log.warning("Cannot hash %s: %s", path, exc)
        return ""


def is_excluded(rel: Path) -> bool:
    """آیا مسیر در لیست استثنائات است؟"""
    for part in rel.parts[:-1]:
        if part in EXCLUDE_DIRS:
            return True
        # پوشه‌های پشتیبان قبلی
        if part.startswith(".sync_backup_"):
            return True
    if rel.name in EXCLUDE_FILES:
        return True
    return False


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_copy(src: Path, dst: Path) -> None:
    """کپی با ایجاد خودکار پوشه والد + حفظ metadata."""
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


def human_size(n: int | float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"

# ─────────────────────────────────────────────────────────────────────────────
#  Git Operations
# ─────────────────────────────────────────────────────────────────────────────

def run_git(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess:
    cmd = ["git"] + args
    log.debug("Running: %s", " ".join(cmd))
    return subprocess.run(
        cmd, cwd=cwd,
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def clone_repo(dest: Path, branch: str) -> bool:
    """Shallow-clone مخزن به مسیر موقت."""
    log.info("⬇  Cloning %s (branch=%s) → %s", REPO_URL, branch, dest)
    result = run_git([
        "clone",
        "--depth", "1",
        "--branch", branch,
        "--single-branch",
        REPO_URL,
        str(dest),
    ])
    if result.returncode != 0:
        log.error("Clone failed:\n%s", result.stderr)
        return False
    log.info("✅ Clone complete.")
    return True

# ─────────────────────────────────────────────────────────────────────────────
#  Core Sync Logic
# ─────────────────────────────────────────────────────────────────────────────

def collect_repo_files(repo_root: Path) -> list[Path]:
    """جمع‌آوری تمام فایل‌های مخزن (مسیرهای نسبی)."""
    files: list[Path] = []
    for root, dirs, filenames in os.walk(repo_root):
        dirs[:] = [
            d for d in dirs
            if d not in EXCLUDE_DIRS and not d.startswith(".sync_backup_")
        ]
        for fn in filenames:
            full = Path(root) / fn
            rel  = full.relative_to(repo_root)
            if not is_excluded(rel):
                files.append(rel)
    return sorted(files)


def sync_files(
    repo_root:    Path,
    project_root: Path,
    backup_root:  Path | None,
    dry_run:      bool,
) -> SyncReport:
    """مقایسه و همگام‌سازی فایل‌ها."""

    report = SyncReport(
        started_at=datetime.now().isoformat(timespec="seconds"),
        dry_run=dry_run,
    )

    repo_files = collect_repo_files(repo_root)
    report.total_scanned = len(repo_files)
    log.info("📂 Found %d files in repository (after exclusions).", len(repo_files))

    for i, rel in enumerate(repo_files, 1):
        src = repo_root / rel
        dst = project_root / rel

        # ── 1. مستثنی ──
        if is_excluded(rel):
            report.excluded.append(FileRecord(str(rel), Action.EXCLUDED))
            continue

        # ── 2. فایل جدید ──
        if not dst.exists():
            rec = FileRecord(
                rel_path=str(rel), action=Action.NEW,
                src_size=src.stat().st_size,
                src_hash=file_sha256(src),
            )
            if not dry_run:
                try:
                    safe_copy(src, dst)
                except Exception as exc:
                    rec.error = str(exc)
                    report.errors.append(rec)
                    continue
            report.new_files.append(rec)
            if i % 200 == 0:
                log.info("  … %d / %d", i, len(repo_files))
            continue

        # ── 3. مقایسه hash ──
        src_hash = file_sha256(src)
        dst_hash = file_sha256(dst)

        if src_hash == dst_hash:
            report.identical.append(FileRecord(str(rel), Action.SKIP))
            continue

        # ── 4. جایگزینی ──
        rec = FileRecord(
            rel_path=str(rel), action=Action.REPLACE,
            src_size=src.stat().st_size, dst_size=dst.stat().st_size,
            src_hash=src_hash,           dst_hash=dst_hash,
        )
        if not dry_run:
            try:
                if backup_root:
                    safe_copy(dst, backup_root / rel)
                safe_copy(src, dst)
            except Exception as exc:
                rec.error = str(exc)
                report.errors.append(rec)
                continue
        report.replaced.append(rec)

        if i % 200 == 0:
            log.info("  … %d / %d", i, len(repo_files))

    report.finished_at = datetime.now().isoformat(timespec="seconds")
    return report

# ─────────────────────────────────────────────────────────────────────────────
#  Report Output
# ─────────────────────────────────────────────────────────────────────────────

def print_report(r: SyncReport) -> None:
    W = 74
    print("\n" + "═" * W)
    print("  📊  ECONOJIN SYNC REPORT")
    print("═" * W)
    print(f"  Started   : {r.started_at}")
    print(f"  Finished  : {r.finished_at}")
    print(f"  Branch    : {r.branch}")
    print(f"  Dry-run   : {'YES — no changes made' if r.dry_run else 'NO'}")
    if r.backup_dir:
        print(f"  Backup    : {r.backup_dir}")
    print("─" * W)
    print(f"  Total scanned      : {r.total_scanned:>6}")
    print(f"  ✅ Replaced         : {r.n_replaced:>6}")
    print(f"  🆕 New files        : {r.n_new:>6}")
    print(f"  ⏭  Identical        : {r.n_identical:>6}")
    print(f"  🚫 Excluded         : {r.n_excluded:>6}")
    print(f"  ❌ Errors           : {r.n_errors:>6}")
    print("─" * W)

    if r.replaced:
        print(f"\n  📝 REPLACED ({r.n_replaced}):")
        print("  " + "─" * (W - 2))
        for rec in r.replaced[:100]:
            d = rec.src_size - rec.dst_size
            s = "+" if d >= 0 else ""
            print(f"    {rec.rel_path}")
            print(f"      {human_size(rec.dst_size)} → {human_size(rec.src_size)}  ({s}{human_size(d)})")
        if r.n_replaced > 100:
            print(f"    … +{r.n_replaced - 100} more (see JSON)")

    if r.new_files:
        print(f"\n  🆕 NEW ({r.n_new}):")
        print("  " + "─" * (W - 2))
        for rec in r.new_files[:100]:
            print(f"    {rec.rel_path}  ({human_size(rec.src_size)})")
        if r.n_new > 100:
            print(f"    … +{r.n_new - 100} more (see JSON)")

    if r.errors:
        print(f"\n  ❌ ERRORS ({r.n_errors}):")
        print("  " + "─" * (W - 2))
        for rec in r.errors:
            print(f"    {rec.rel_path}: {rec.error}")

    print("\n" + "═" * W)


def save_json_report(r: SyncReport, path: Path) -> None:
    data = {
        "started_at":  r.started_at,
        "finished_at": r.finished_at,
        "branch":      r.branch,
        "dry_run":     r.dry_run,
        "backup_dir":  r.backup_dir,
        "summary": {
            "total_scanned": r.total_scanned,
            "replaced":      r.n_replaced,
            "new_files":     r.n_new,
            "identical":     r.n_identical,
            "excluded":      r.n_excluded,
            "errors":        r.n_errors,
        },
        "replaced_files": [
            {
                "path": x.rel_path,
                "old_size": x.dst_size, "new_size": x.src_size,
                "old_hash": x.dst_hash[:16], "new_hash": x.src_hash[:16],
            }
            for x in r.replaced
        ],
        "new_files": [
            {"path": x.rel_path, "size": x.src_size, "hash": x.src_hash[:16]}
            for x in r.new_files
        ],
        "errors": [
            {"path": x.rel_path, "error": x.error}
            for x in r.errors
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info("📄 JSON report → %s", path)

# ─────────────────────────────────────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(
        description="Sync local Econojin project with GitHub repo.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python sync_repo.py                       # sync + backup
  python sync_repo.py --dry-run             # preview only
  python sync_repo.py --no-backup           # no backup
  python sync_repo.py --branch develop      # different branch
  python sync_repo.py --project D:\\other    # custom path
        """,
    )
    ap.add_argument("--dry-run",   action="store_true", help="پیش‌نمایش بدون تغییر")
    ap.add_argument("--no-backup", action="store_true", help="بدون پشتیبان‌گیری")
    ap.add_argument("--branch",    default=DEFAULT_BRANCH)
    ap.add_argument("--project",   default=str(PROJECT_ROOT))
    ap.add_argument("--verbose",   action="store_true")
    args = ap.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_root = Path(args.project).resolve()
    if not project_root.is_dir():
        log.error("Project root not found: %s", project_root)
        return 1

    log.info("🚀 Econojin Repo Sync")
    log.info("   Project : %s", project_root)
    log.info("   Repo    : %s", REPO_URL)
    log.info("   Branch  : %s", args.branch)
    log.info("   Dry-run : %s", args.dry_run)
    log.info("   Backup  : %s", "NO" if args.no_backup else "YES")

    tmp_dir    = Path(tempfile.mkdtemp(prefix="econojin_sync_"))
    clone_dest = tmp_dir / "repo"

    try:
        # 1 ── Clone
        if not clone_repo(clone_dest, args.branch):
            return 1

        # 2 ── Backup dir
        backup_root: Path | None = None
        if not args.no_backup and not args.dry_run:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_root = project_root / f".sync_backup_{ts}"
            ensure_dir(backup_root)
            log.info("💾 Backup → %s", backup_root)

        # 3 ── Sync
        report = sync_files(clone_dest, project_root, backup_root, args.dry_run)
        report.branch = args.branch
        if backup_root:
            report.backup_dir = str(backup_root)

        # 4 ── Console report
        print_report(report)

        # 5 ── JSON report
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_json_report(report, project_root / f"sync_report_{ts}.json")

        # 6 ── Exit code
        if report.n_errors:
            log.warning("⚠️  Done with %d error(s).", report.n_errors)
            return 2
        log.info("✅ Sync completed successfully.")
        return 0

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        log.debug("Temp cleaned: %s", tmp_dir)


if __name__ == "__main__":
    sys.exit(main())
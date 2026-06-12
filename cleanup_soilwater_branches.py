import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

BACKEND_DIR = ROOT / "apps" / "backend-api" / "app" / "land_soil_water"
WEB_DIR = ROOT / "apps" / "web" / "src" / "app"

BACKUP_ROOT = ROOT / "zzz_legacy_land_soil_water_strict"


def list_current():
    print("=== CURRENT STATE ===")
    print(f"Backend dir: {BACKEND_DIR}  -> exists={BACKEND_DIR.exists()}")
    if BACKEND_DIR.exists():
        for p in sorted(BACKEND_DIR.glob("*")):
            print("  backend:", p.name)

    print(f"Web dir: {WEB_DIR}  -> exists={WEB_DIR.exists()}")
    if WEB_DIR.exists():
        for p in WEB_DIR.rglob("*land-soil-water*"):
            if p.is_file():
                print("  web:", p.relative_to(ROOT))


def main():
    print("=== STRICT CLEANUP: land_soil_water in apps/* ===")
    list_current()

    confirm = input("\nType 'YES' to MOVE these files to backup and clear apps/*: ").strip()
    if confirm != "YES":
        print("Aborted. No files moved.")
        return

    BACKUP_ROOT.mkdir(exist_ok=True)

    # 1) backend: apps/backend-api/app/land_soil_water/*
    if BACKEND_DIR.exists():
        for p in sorted(BACKEND_DIR.rglob("*")):
            if p.is_file():
                rel = p.relative_to(ROOT)
                dest = BACKUP_ROOT / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                print(f"→ Moving backend file {rel}  -->  {dest.relative_to(ROOT)}")
                shutil.move(str(p), str(dest))
        # بعد از خالی شدن، خود پوشه را هم به بکاپ ببریم
        print(f"→ Moving empty backend dir {BACKEND_DIR.relative_to(ROOT)} to backup root")
        dest_dir = BACKUP_ROOT / BACKEND_DIR.relative_to(ROOT)
        dest_dir.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.move(str(BACKEND_DIR), str(dest_dir))
        except Exception as e:
            print(f"  (skip moving backend dir: {e})")

    # 2) web pages: apps/web/src/app/**/land-soil-water**
    if WEB_DIR.exists():
        for p in sorted(WEB_DIR.rglob("*land-soil-water*")):
            if p.is_file():
                rel = p.relative_to(ROOT)
                dest = BACKUP_ROOT / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                print(f"→ Moving web file {rel}  -->  {dest.relative_to(ROOT)}")
                shutil.move(str(p), str(dest))

    print("\n=== AFTER MOVE ===")
    list_current()

    print("\n✅ Done. All moved to", BACKUP_ROOT.relative_to(ROOT))


if __name__ == "__main__":
    main()
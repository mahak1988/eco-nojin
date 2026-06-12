import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent
SOURCE = ROOT / "scripts" / "soil_water_module.py"
TARGET = ROOT / "api" / "modules" / "soil_water" / "models.py"


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Source not found: {SOURCE}")

    text = SOURCE.read_text(encoding="utf-8")
    lines = text.splitlines()

    keep = []
    in_block = False

    for line in lines:
        stripped = line.lstrip()

        # شروع بخش مدل‌های ORM: کلاس‌هایی که از Base ارث می‌برند
        if stripped.startswith("class ") and "(Base)" in stripped:
            in_block = True

        if in_block:
            keep.append(line)

    if not keep:
        raise SystemExit("No ORM classes (class ... (Base)) found in source")

    header = """from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from api.core.database import Base

"""

    new_models = header + "\n".join(keep) + "\n"

    TARGET.parent.mkdir(parents=True, exist_ok=True)

    if TARGET.exists():
        backup = TARGET.with_suffix(".py.bak")
        shutil.copy2(TARGET, backup)
        print(f"Backup created: {backup}")

    TARGET.write_text(new_models, encoding="utf-8")
    print(f"Rewritten: {TARGET}")


if __name__ == "__main__":
    main()
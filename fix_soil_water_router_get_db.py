import pathlib

ROOT = pathlib.Path(__file__).resolve().parent

def main() -> None:
    target = ROOT / "api" / "modules" / "soil_water" / "router.py"

    text = target.read_text(encoding="utf-8")

    # اگر قبلاً import اشتباه اضافه شده، حذفش کن
    text = text.replace(
        "from api.core.dependencies import get_db\n",
        ""
    )

    # اگر import درست از admin_router استفاده می‌شود، همان را پیدا کن
    admin_router = ROOT / "api" / "modules" / "soil_water" / "admin_router.py"
    admin_text = admin_router.read_text(encoding="utf-8")

    # دنبال خطی که get_db را import کرده می‌گردیم
    import_line = None
    for line in admin_text.splitlines():
        if "get_db" in line and "import" in line:
            import_line = line.strip()
            break

    if not import_line:
        raise RuntimeError("خط import مربوط به get_db در admin_router.py پیدا نشد؛ لطفاً دستی چک کن.")

    # اگر در router.py همین import نیست، به بالای فایل اضافه‌اش کن
    lines = text.splitlines()
    if import_line not in text:
        # بعد از اولین بلوک import ها اضافه می‌کنیم
        insert_pos = 0
        while insert_pos < len(lines) and lines[insert_pos].startswith("from "):
            insert_pos += 1
        while insert_pos < len(lines) and lines[insert_pos].startswith("import "):
            insert_pos += 1

        lines.insert(insert_pos, import_line)
        text = "\n".join(lines)

    target.write_text(text, encoding="utf-8")
    print("soil_water/router.py get_db import fixed to:", import_line)


if __name__ == "__main__":
    main()
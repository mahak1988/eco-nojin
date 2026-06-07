# 02_run_econojin.py
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

PROJECT = Path(__file__).parent / "econojin-super-platform"
BACKEND = PROJECT / "backend"
FRONTEND = PROJECT / "frontend"


def run_service(name, cmd, cwd):
    """اجرای سرویس در یک ترد جداگانه"""
    print(f"🟢 شروع {name}...")
    proc = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8"
    )
    for line in proc.stdout:
        sys.stdout.write(f"[{name}] {line}")
        sys.stdout.flush()


def run_backend():
    venv_pip = (
        BACKEND / ".venv" / "Scripts" / "python.exe"
        if os.name == "nt"
        else BACKEND / ".venv" / "bin" / "python"
    )
    if not venv_pip.exists():
        print("❌ محیط مجازی بک‌اند یافت نشد. ابتدا 01_setup_econojin.py را اجرا کنید.")
        return
    cmd = [
        str(venv_pip),
        "-m",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
    ]
    threading.Thread(target=run_service, args=("Backend", cmd, BACKEND), daemon=True).start()


def run_frontend():
    npm = "npm.cmd" if os.name == "nt" else "npm"
    if not (FRONTEND / "node_modules").exists():
        print("❌ پوشه node_modules یافت نشد. ابتدا 01_setup_econojin.py را اجرا کنید.")
        return
    cmd = [npm, "run", "dev"]
    threading.Thread(target=run_service, args=("Frontend", cmd, FRONTEND), daemon=True).start()


if __name__ == "__main__":
    print("🌍 ابرپروژه اکو نوژین در حال راه‌اندازی...")
    run_backend()
    time.sleep(2)  # فاصله کوتاه برای استارت بک‌اند
    run_frontend()

    print("\n" + "=" * 50)
    print("🔗 دسترسی‌ها:")
    print("   بک‌اند:  http://127.0.0.1:8000")
    print("   فرانت‌اند: http://127.0.0.1:3000")
    print("   مستندات: http://127.0.0.1:8000/docs")
    print("=" * 50)
    print("💡 برای توقف: Ctrl+C را فشار دهید.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 پروژه متوقف شد.")

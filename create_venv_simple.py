# create_venv_simple.py
import os, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"

print(f"🔧 Creating virtual environment in {VENV}...")

# روش ۱: تلاش با venv
try:
    subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    print("✅ Created with venv")
except:
    # روش ۲: تلاش با virtualenv
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "virtualenv", "--user"], check=True)
        subprocess.run([sys.executable, "-m", "virtualenv", str(VENV)], check=True)
        print("✅ Created with virtualenv")
    except:
        # روش ۳: استفاده مستقیم از پایتون بدون venv (فقط برای نصب پکیج‌ها)
        print("⚠️ Could not create venv. Using system Python directly.")
        VENV = None

print(f"\n🚀 Next steps:")
if VENV and VENV.exists():
    print(f"   1. Activate: {VENV}\\Scripts\\activate.bat")
    print(f"   2. Install: pip install fastapi uvicorn pydantic sqlalchemy")
    print(f"   3. Run: python api\\main.py")
else:
    print(f"   1. Install directly: python -m pip install fastapi uvicorn pydantic sqlalchemy")
    print(f"   2. Run: python api\\main.py")
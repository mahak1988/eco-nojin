#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اجرای ساده بک‌اند و فرانت‌اند (برای توسعه)"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

print("\n🌱 Eco Nojin - Development Mode")
print("=" * 50)
print("1. اجرای بک‌اند (FastAPI)")
print("2. اجرای فرانت‌اند (Vite)")
print("3. اجرای همزمان هر دو")
print("4. خروج")
choice = input("\nانتخاب (1-4): ")

if choice == "1":
    os.chdir(ROOT)
    subprocess.run([sys.executable, "scripts/run_backend.py"])
elif choice == "2":
    subprocess.run([sys.executable, "scripts/run_frontend.py"])
elif choice == "3":
    subprocess.run([sys.executable, "scripts/run_all.py"])
else:
    print("خروج.")

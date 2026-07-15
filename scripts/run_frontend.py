#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اجرای فرانت‌اند Eco Nojin"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "apps" / "web"
os.chdir(WEB_DIR)

# بررسی وجود pnpm
try:
    subprocess.run(["pnpm", "--version"], capture_output=True, check=True)
except:
    print("⚠️ pnpm یافت نشد. در حال نصب...")
    subprocess.run(["npm", "install", "-g", "pnpm"], check=True)

# نصب وابستگی‌ها در صورت نیاز
if not (WEB_DIR / "node_modules").exists():
    print("📦 نصب وابستگی‌ها...")
    subprocess.run(["pnpm", "install"], check=True)

# اجرا
cmd = ["pnpm", "run", "dev"]
try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    print("\n🛑 متوقف شد.")
except Exception as e:
    print(f"❌ خطا: {e}")

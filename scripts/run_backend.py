#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اجرای بک‌اند Eco Nojin"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)

cmd = [sys.executable, "-m", "uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    print("\n🛑 متوقف شد.")
except Exception as e:
    print(f"❌ خطا: {e}")

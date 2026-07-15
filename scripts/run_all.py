#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اجرای همزمان تمام سرویس‌های Eco Nojin"""

import os
import sys
import subprocess
import signal
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
processes = []

def run_backend():
    os.chdir(ROOT)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "apps.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

def run_frontend():
    os.chdir(ROOT / "apps" / "web")
    return subprocess.Popen(
        ["pnpm", "run", "dev"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1
    )

def log_output(name, proc):
    def loop():
        for line in iter(proc.stdout.readline, ''):
            if line:
                print(f"[{name}] {line.rstrip()}")
    threading.Thread(target=loop, daemon=True).start()

def signal_handler(sig, frame):
    print("\n🛑 در حال توقف سرویس‌ها...")
    for _, proc in processes:
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("\n" + "=" * 60)
print("🌱 Eco Nojin - همه سرویس‌ها")
print("=" * 60)

# شروع
procs = [
    ("Backend", run_backend()),
    ("Frontend", run_frontend()),
]
for name, proc in procs:
    processes.append((name, proc))
    log_output(name, proc)
    print(f"✅ {name} شروع شد (PID: {proc.pid})")

print("\n📌 دسترسی‌ها:")
print("   بک‌اند: http://localhost:8000")
print("   مستندات API: http://localhost:8000/docs")
print("   فرانت‌اند: http://localhost:5173")
print("   (Ctrl+C برای توقف)")
print("=" * 60 + "\n")

try:
    for _, proc in processes:
        proc.wait()
except KeyboardInterrupt:
    signal_handler(None, None)

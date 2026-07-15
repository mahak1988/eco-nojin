#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - اسکریپت رفع مشکلات و راه‌اندازی پروژه

این اسکریپت به‌طور خودکار:
1. فایل‌های گم‌شده (main.py، requirements.txt، ...) را ایجاد می‌کند
2. کتابخانه‌های سبک و ضروری را نصب می‌کند
3. یکپارچگی بین ماژول‌ها را برقرار می‌کند
4. اسکریپت‌های اجرایی را ایجاد می‌کند
5. فایل .env.example را می‌سازد

نکته: کتابخانه‌های سنگین (tensorflow, torch, transformers, faiss, qdrant) به‌صورت پیش‌فرض نصب نمی‌شوند.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional

# ============================================================
# تنظیمات
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = PROJECT_ROOT / "apps"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# ============================================================
# کتابخانه‌های سبک و ضروری
# ============================================================

CORE_PACKAGES = [
    "fastapi==0.115.0",
    "uvicorn[standard]==0.30.6",
    "pydantic==2.9.2",
    "pydantic-settings==2.5.2",
    "python-dotenv==1.0.1",
    "sqlalchemy[asyncio]==2.0.35",
    "psycopg[binary]==3.2.3",
    "alembic==1.13.2",
    "python-jose[cryptography]==3.3.0",
    "passlib[bcrypt]==1.7.4",
    "python-multipart==0.0.12",
    "bcrypt==4.0.1",
    "email-validator==2.2.0",
    "httpx==0.27.0",
    "aiofiles==24.1.0",
    "pytest==8.3.0",
    "pytest-asyncio==0.24.0",
    "anyio==4.6.0",
]

# کتابخانه‌های سبک برای AI (بدون tensorflow/torch)
LIGHT_AI_PACKAGES = [
    "langchain==0.3.0",
    "langchain-community==0.3.0",
    "langchain-core==0.3.0",
    "langgraph==0.2.0",
]

# کتابخانه‌های علمی سبک
SCIENTIFIC_PACKAGES = [
    "numpy==1.26.0",
    "scipy==1.14.0",
    "pandas==2.2.0",
]

# کتابخانه‌های اختیاری (سنگین) - پیش‌فرض نصب نمی‌شوند
HEAVY_PACKAGES = [
    "sentence-transformers",
    "faiss-cpu",
    "qdrant-client",
    "torch",
    "tensorflow",
    "transformers",
]

# ============================================================
# توابع کمکی
# ============================================================

def log(message: str, level: str = "INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "HEADER": "\033[95m",
        "END": "\033[0m",
    }
    print(f"{colors.get(level, '')}[{level}]{colors.get('END', '')} {message}")

def create_file(path: Path, content: str, overwrite: bool = False):
    """ایجاد فایل با محتوا"""
    if path.exists() and not overwrite:
        log(f"⏩ {path.relative_to(PROJECT_ROOT)} از قبل وجود دارد", "WARNING")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"✅ ایجاد: {path.relative_to(PROJECT_ROOT)}", "SUCCESS")
    return True

def install_packages(packages: List[str], description: str = "") -> bool:
    """نصب بسته‌ها با pip"""
    if not packages:
        return True
    log(f"📦 نصب {description} ({len(packages)} بسته)...", "INFO")
    try:
        for pkg in packages:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                capture_output=True,
                check=True,
                text=True
            )
            log(f"   ✅ {pkg}", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log(f"   ❌ خطا در نصب: {e}", "ERROR")
        return False

# ============================================================
# ۱. ایجاد فایل main.py
# ============================================================

def create_main_py():
    """ایجاد apps/main.py به‌عنوان نقطه ورود بک‌اند"""
    content = '''# -*- coding: utf-8 -*-
"""
Eco Nojin - نقطه ورود اصلی بک‌اند

این فایل تمام ماژول‌ها را یکپارچه می‌کند:
- users: مدیریت کاربران و احراز هویت
- ai_agents: عامل‌های هوش مصنوعی
- shared: کدهای مشترک
- simulation: شبیه‌سازهای علمی
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# بارگذاری متغیرهای محیطی
load_dotenv()

# ایجاد اپلیکیشن
app = FastAPI(
    title="Eco Nojin API",
    description="پلتفرم جامع کشاورزی، آب، محیط‌زیست و اقتصاد",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# تنظیمات CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# ثبت روترهای ماژول‌ها
# ============================================================

try:
    from apps.users.router import router as users_router
    app.include_router(users_router, prefix="/api/users", tags=["Users"])
    print("✅ users: روتر بارگذاری شد")
except ImportError as e:
    print(f"⚠️ users: {e}")

try:
    from apps.ai_agents.router import router as ai_agents_router
    app.include_router(ai_agents_router, prefix="/api/ai-agents", tags=["AI Agents"])
    print("✅ ai_agents: روتر بارگذاری شد")
except ImportError as e:
    print(f"⚠️ ai_agents: {e}")

# ============================================================
# مسیرهای عمومی
# ============================================================

@app.get("/")
async def root():
    return {
        "message": "Eco Nojin API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "modules": ["users", "ai_agents", "shared", "simulation"],
    }

# ============================================================
# اجرا (برای محیط توسعه)
# ============================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port, reload=True)
'''
    return create_file(APPS_DIR / "main.py", content)

# ============================================================
# ۲. ایجاد requirements.txt
# ============================================================

def create_requirements():
    """ایجاد requirements.txt با کتابخانه‌های سبک"""
    lines = [
        "# ============================================================",
        "# Eco Nojin - وابستگی‌های اصلی (نسخه سبک)",
        "# ============================================================",
        "",
        "# هسته (Core)",
    ]
    lines.extend(CORE_PACKAGES)
    lines.extend([
        "",
        "# هوش مصنوعی سبک (بدون tensorflow/torch)",
    ])
    lines.extend(LIGHT_AI_PACKAGES)
    lines.extend([
        "",
        "# محاسبات علمی",
    ])
    lines.extend(SCIENTIFIC_PACKAGES)
    lines.extend([
        "",
        "# کتابخانه‌های سنگین (اختیاری - برای نصب دستی)",
        "# ============================================================",
        "# برای نصب کتابخانه‌های سنگین، این خطوط را از حالت نظر خارج کنید:",
        "# sentence-transformers",
        "# faiss-cpu",
        "# qdrant-client",
        "# torch",
        "# tensorflow",
        "# transformers",
    ])
    content = "\n".join(lines)
    return create_file(PROJECT_ROOT / "requirements.txt", content)

# ============================================================
# ۳. ایجاد shared/__init__.py
# ============================================================

def create_shared_init():
    """ایجاد apps/shared/__init__.py برای یکپارچه‌سازی"""
    content = '''# -*- coding: utf-8 -*-
"""
Eco Nojin - کدهای مشترک بین ماژول‌ها
"""

# دیتابیس
try:
    from apps.shared.database.session import get_db, AsyncSessionLocal
except ImportError:
    pass

# هوش مصنوعی
try:
    from apps.shared.ai.llm_factory import get_llm
    from apps.shared.ai.fallback.brain import FallbackBrain
except ImportError:
    pass

__all__ = [
    "get_db",
    "AsyncSessionLocal",
    "get_llm",
    "FallbackBrain",
]
'''
    return create_file(APPS_DIR / "shared" / "__init__.py", content)

# ============================================================
# ۴. ایجاد اسکریپت‌های اجرایی
# ============================================================

def create_run_scripts():
    """ایجاد اسکریپت‌های اجرایی در پوشه scripts"""
    scripts_dir = SCRIPTS_DIR
    scripts_dir.mkdir(parents=True, exist_ok=True)

    # run_backend.py
    run_backend = '''#!/usr/bin/env python3
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
    print("\\n🛑 متوقف شد.")
except Exception as e:
    print(f"❌ خطا: {e}")
'''
    create_file(scripts_dir / "run_backend.py", run_backend)

    # run_frontend.py
    run_frontend = '''#!/usr/bin/env python3
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
    print("\\n🛑 متوقف شد.")
except Exception as e:
    print(f"❌ خطا: {e}")
'''
    create_file(scripts_dir / "run_frontend.py", run_frontend)

    # run_all.py
    run_all = '''#!/usr/bin/env python3
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
    print("\\n🛑 در حال توقف سرویس‌ها...")
    for _, proc in processes:
        proc.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

print("\\n" + "=" * 60)
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

print("\\n📌 دسترسی‌ها:")
print("   بک‌اند: http://localhost:8000")
print("   مستندات API: http://localhost:8000/docs")
print("   فرانت‌اند: http://localhost:5173")
print("   (Ctrl+C برای توقف)")
print("=" * 60 + "\\n")

try:
    for _, proc in processes:
        proc.wait()
except KeyboardInterrupt:
    signal_handler(None, None)
'''
    create_file(scripts_dir / "run_all.py", run_all)

    # run_dev.py (نسخه ساده)
    run_dev = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""اجرای ساده بک‌اند و فرانت‌اند (برای توسعه)"""

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

print("\\n🌱 Eco Nojin - Development Mode")
print("=" * 50)
print("1. اجرای بک‌اند (FastAPI)")
print("2. اجرای فرانت‌اند (Vite)")
print("3. اجرای همزمان هر دو")
print("4. خروج")
choice = input("\\nانتخاب (1-4): ")

if choice == "1":
    os.chdir(ROOT)
    subprocess.run([sys.executable, "scripts/run_backend.py"])
elif choice == "2":
    subprocess.run([sys.executable, "scripts/run_frontend.py"])
elif choice == "3":
    subprocess.run([sys.executable, "scripts/run_all.py"])
else:
    print("خروج.")
'''
    create_file(scripts_dir / "run_dev.py", run_dev)

    # run_free_services.py
    run_services = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تست سرویس‌های رایگان Eco Nojin"""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

def test_supabase():
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        if not url or not key:
            return "❌ SUPABASE_URL یا SUPABASE_ANON_KEY تنظیم نشده"
        client = create_client(url, key)
        result = client.table("users").select("*").limit(1).execute()
        return "✅ اتصال به Supabase برقرار است"
    except Exception as e:
        return f"❌ خطا: {e}"

def test_openrouter():
    try:
        import httpx
        key = os.getenv("OPENROUTER_API_KEY")
        if not key:
            return "❌ OPENROUTER_API_KEY تنظیم نشده"
        return "✅ کلید OpenRouter تنظیم شده است"
    except Exception as e:
        return f"❌ خطا: {e}"

def test_yahoo():
    try:
        import yfinance as yf
        ticker = yf.Ticker("AAPL")
        data = ticker.history(period="1d")
        if len(data) > 0:
            return f"✅ اتصال برقرار است. قیمت: {data['Close'].iloc[-1]}"
        return "⚠️ داده‌ای دریافت نشد"
    except ImportError:
        return "⚠️ yfinance نصب نشده (pip install yfinance)"
    except Exception as e:
        return f"❌ خطا: {e}"

print("\\n" + "=" * 60)
print("🆓 تست سرویس‌های رایگان")
print("=" * 60)
print(f"Supabase: {test_supabase()}")
print(f"OpenRouter: {test_openrouter()}")
print(f"Yahoo Finance: {test_yahoo()}")
print("=" * 60)
'''
    create_file(scripts_dir / "run_free_services.py", run_services)

    log("✅ تمام اسکریپت‌های اجرایی ایجاد شدند", "SUCCESS")
    return True

# ============================================================
# ۵. ایجاد .env.example
# ============================================================

def create_env_example():
    """ایجاد فایل .env.example"""
    content = '''# ============================================================
# Eco Nojin - متغیرهای محیطی
# ============================================================

# محیط
ENV_STATE=development
DEBUG=True

# سرور
HOST=0.0.0.0
PORT=8000

# امنیت
SECRET_KEY=your-secret-key-here-change-me-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# دیتابیس
DATABASE_URL=sqlite:///./econojin.db
# برای Supabase:
# DATABASE_URL=postgresql://user:password@host:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# سرویس‌های خارجی
OPENROUTER_API_KEY=sk-or-v1-...
ALPHA_VANTAGE_API_KEY=...
TUSHARE_TOKEN=...
OPENWEATHER_API_KEY=...

# بلاکچین (اختیاری)
ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/...
OWNER_PRIVATE_KEY=0x...
ECOCOIN_CONTRACT_ADDRESS=0x...

# ============================================================
# فرانت‌اند (در apps/web/.env)
# ============================================================
VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
'''
    return create_file(PROJECT_ROOT / ".env.example", content)

# ============================================================
# ۶. نصب کتابخانه‌ها
# ============================================================

def install_light_packages():
    """نصب کتابخانه‌های سبک و ضروری"""
    log("\n📦 نصب کتابخانه‌های ضروری...", "HEADER")
    all_packages = CORE_PACKAGES + LIGHT_AI_PACKAGES + SCIENTIFIC_PACKAGES
    success = True
    for pkg in all_packages:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                capture_output=True,
                check=True,
                text=True
            )
            log(f"   ✅ {pkg}", "SUCCESS")
        except subprocess.CalledProcessError:
            log(f"   ❌ {pkg} (خطا)", "ERROR")
            success = False
    return success

# ============================================================
# ۷. اجرای اصلی
# ============================================================

def main():
    log("\n🌱 Eco Nojin - اسکریپت رفع مشکلات و راه‌اندازی", "HEADER")
    log("=" * 60, "HEADER")

    # 1. ایجاد فایل‌های گم‌شده
    log("\n📁 مرحله ۱: ایجاد فایل‌های گم‌شده", "HEADER")
    create_main_py()
    create_requirements()
    create_shared_init()
    create_run_scripts()
    create_env_example()

    # 2. نصب کتابخانه‌های سبک
    log("\n📦 مرحله ۲: نصب کتابخانه‌های سبک", "HEADER")
    install_light_packages()

    # 3. پیام نهایی
    log("\n" + "=" * 60, "SUCCESS")
    log("✅ پروژه با موفقیت راه‌اندازی شد!", "SUCCESS")
    log("=" * 60, "SUCCESS")
    log("\n📌 مراحل بعدی:", "INFO")
    log("   1. کپی .env.example به .env و تنظیم کلیدها")
    log("   2. اجرای: python scripts/run_dev.py")
    log("   3. یا: python scripts/run_all.py (اجرای همزمان)")
    log("   4. مشاهده مستندات API: http://localhost:8000/docs")
    log("\n📦 کتابخانه‌های سنگین (اختیاری):", "INFO")
    log("   برای نصب دستی: pip install sentence-transformers faiss-cpu qdrant-client")
    log("   (این کتابخانه‌ها برای RAG و embedding نیاز هستند)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("\n⏹️ متوقف شد.", "WARNING")
        sys.exit(0)
    except Exception as e:
        log(f"❌ خطا: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════════
  🌿  Econojin Development Manager  🌿
  -----------------------------------------------------------------
  مخزن: https://github.com/mahak1988/eco-nojin.git
  پلتفرم: Windows / PowerShell / VSCode Terminal
  نیازمندی: Python 3.10+ (شما 3.14.6 دارید ✓)

  امکانات:
    1) کلون / به‌روزرسانی مخزن
    2) ساخت virtual environment (.venv)
    3) تولید خودکار فایل .env با SECRET_KEY تصادفی
    4) نصب وابستگی‌های Python (با requirements.txt صحیح)
    5) بررسی و نصب Node.js و pnpm
    6) نصب وابستگی‌های Frontend (pnpm install)
    7) اجرای Backend (FastAPI در پورت 8000)
    8) اجرای Frontend (Vite در پورت 5173)
    9) اجرای همزمان Backend + Frontend
   10) اجرا با Docker (docker-compose.dev.yml)
   11) Health Check برای سرویس‌ها
   12) اجرای Migration (Alembic)
   13) اجرای تست‌ها (pytest)
   14) پاک‌سازی cache و node_modules
   15) اطلاعات مخزن (وضعیت، شاخه‌ها، commitها)
   16) ساخت شاخه جدید + Commit + Push (Workflow ساده)
    0) خروج
═══════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import os
import sys
import subprocess
import secrets
import shutil
import json
import time
import webbrowser
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────
# تنظیمات اصلی
# ─────────────────────────────────────────────────────────────────────
REPO_URL = "https://github.com/mahak1988/eco-nojin.git"
REPO_NAME = "eco-nojin"

# مسیر پایه: همان پوشه‌ای که اسکریپت در آن قرار دارد
BASE_DIR = Path(__file__).resolve().parent
REPO_DIR = BASE_DIR / REPO_NAME
VENV_DIR = REPO_DIR / ".venv"
ENV_FILE = REPO_DIR / ".env"
ENV_EXAMPLE = REPO_DIR / ".env.example"
REQUIREMENTS_FILE = REPO_DIR / "requirements.txt"
PYTHON_VERSION_MIN = (3, 10)

# مسیرهای اجرایی در ویندوز
VENV_PYTHON = VENV_DIR / "Scripts" / "python.exe"
VENV_PIP = VENV_DIR / "Scripts" / "pip.exe"
VENV_UVICORN = VENV_DIR / "Scripts" / "uvicorn.exe"


# ─────────────────────────────────────────────────────────────────────
# ابزارهای کمکی
# ─────────────────────────────────────────────────────────────────────
def banner(text: str = "", char: str = "═", width: int = 65) -> None:
    print()
    print(char * width)
    if text:
        print(f"  {text}")
        print(char * width)


def info(msg: str) -> None:
    print(f"  [i] {msg}")


def ok(msg: str) -> None:
    print(f"  [✓] {msg}")


def warn(msg: str) -> None:
    print(f"  [!] {msg}")


def err(msg: str) -> None:
    print(f"  [✗] {msg}")


def pause() -> None:
    try:
        input("\n  [Enter برای بازگشت به منو] ")
    except (EOFError, KeyboardInterrupt):
        pass


def run(cmd: list[str] | str, cwd: Path | None = None,
        check: bool = False, capture: bool = False,
        shell: bool = False) -> subprocess.CompletedProcess:
    """اجرای دستور با خروجی استاندارد."""
    if isinstance(cmd, str) and not shell:
        cmd = cmd.split()
    if isinstance(cmd, list) and shell:
        cmd = " ".join(cmd)
    return subprocess.run(
        cmd, cwd=str(cwd) if cwd else None,
        shell=shell, check=check,
        capture_output=capture, text=True,
        encoding="utf-8", errors="replace",
    )


def has(cmd: str) -> bool:
    """بررسی وجود یک دستور در PATH."""
    return shutil.which(cmd) is not None


# ─────────────────────────────────────────────────────────────────────
# ۱. کلون / به‌روزرسانی مخزن
# ─────────────────────────────────────────────────────────────────────
def action_clone_repo() -> None:
    banner("کلون / به‌روزرسانی eco-nojin")

    if REPO_DIR.exists() and (REPO_DIR / ".git").exists():
        info(f"مخزن از قبل موجود است: {REPO_DIR}")
        info("در حال دریافت آخرین تغییرات (git pull)...")
        result = run(["git", "pull"], cwd=REPO_DIR)
        if result.returncode == 0:
            ok("به‌روزرسانی شد.")
        else:
            err("خطا در git pull.")
    else:
        info(f"کلون به: {REPO_DIR}")
        result = run(["git", "clone", REPO_URL, str(REPO_DIR)])
        if result.returncode == 0:
            ok("مخزن با موفقیت کلون شد.")
        else:
            err("خطا در کلون.")
            return

    info(f"مسیر: {REPO_DIR}")
    pause()


# ─────────────────────────────────────────────────────────────────────
# ۲. ساخت virtual environment
# ─────────────────────────────────────────────────────────────────────
def action_create_venv() -> None:
    banner("ساخت Virtual Environment")

    if not REPO_DIR.exists():
        err("ابتدا مخزن را کلون کنید (گزینه ۱).")
        pause()
        return

    if VENV_DIR.exists():
        info(f"venv از قبل موجود است: {VENV_DIR}")
        ans = input("  بازنویسی شود؟ (y/N): ").strip().lower()
        if ans != "y":
            info("لغو شد.")
            pause()
            return
        shutil.rmtree(VENV_DIR, ignore_errors=True)

    info("در حال ساخت venv با python...")
    result = run([sys.executable, "-m", "venv", str(VENV_DIR)])
    if result.returncode == 0 and VENV_PYTHON.exists():
        ok(f"venv ساخته شد: {VENV_DIR}")
        info(f"Python: {VENV_PYTHON}")

        # ارتقای pip
        info("ارتقای pip...")
        run([str(VENV_PYTHON), "-m", "pip", "install", "--upgrade", "pip"])
        ok("pip به‌روزرسانی شد.")
    else:
        err("خطا در ساخت venv.")
        print(result.stderr)

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۳. تولید خودکار فایل .env
# ─────────────────────────────────────────────────────────────────────
def generate_secret(length: int = 64) -> str:
    return secrets.token_urlsafe(length)[:length]


def action_create_env() -> None:
    banner("تولید فایل .env")

    if not REPO_DIR.exists():
        err("ابتدا مخزن را کلون کنید.")
        pause()
        return

    if ENV_FILE.exists():
        info(f".env از قبل موجود است: {ENV_FILE}")
        ans = input("  بازنویسی شود؟ (y/N): ").strip().lower()
        if ans != "y":
            info("لغو شد.")
            pause()
            return

    if ENV_EXAMPLE.exists():
        info("بر اساس .env.example تولید می‌شود...")
        content = ENV_EXAMPLE.read_text(encoding="utf-8", errors="replace")
    else:
        info(".env.example پیدا نشد؛ از قالب پیش‌فرض استفاده می‌شود.")
        content = """# Econojin .env (auto-generated)
DATABASE_URL=***
SECRET_KEY=***
JWT_SECRET_KEY=***
"""

    # جایگزینی مقادیر *** با secret های واقعی
    replacements = {
        "DATABASE_URL": "sqlite+aiosqlite:///./econojin.db",
        "POSTGRES_PASSWORD": generate_secret(32),
        "SECRET_KEY": generate_secret(48),
        "JWT_SECRET_KEY": generate_secret(48),
        "FIRST_SUPERUSER_PASSWORD": generate_secret(24),
        "APP_KEYS": generate_secret(32),
        "API_TOKEN_SALT": generate_secret(32),
        "ADMIN_JWT_SECRET": generate_secret(32),
        "TRANSFER_TOKEN_SALT": generate_secret(32),
        "LLM_PROVIDER": "fake",
        "ENVIRONMENT": "local",
    }

    new_lines = []
    for line in content.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in replacements:
                new_lines.append(f"{key}={replacements[key]}")
                continue
            if "***" in line:
                # مقدار generic - تولید secret
                new_lines.append(f"{key}={generate_secret(32)}")
                continue
        new_lines.append(line)

    ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    ok(f".env ساخته شد: {ENV_FILE}")
    warn("برای فعال‌سازی کلیدهای واقعی (LLM_API_KEY, FAO_API_KEY, ...) فایل را ویرایش کنید.")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۴. نصب وابستگی‌های Python
# ─────────────────────────────────────────────────────────────────────
# لیست حداقلی وابستگی‌های لازم برای راه‌اندازی بک‌اند
# چون requirements.txt مخزن خراب است (UTF-16 با BOM و محتوای نامعتبر)،
# این لیست دستی را استفاده می‌کنیم.
MINIMAL_REQUIREMENTS = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy>=2.0.0",
    "aiosqlite>=0.20.0",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.6.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "python-multipart>=0.0.12",
    "python-dotenv>=1.0.1",
    "httpx>=0.27.0",
    "structlog>=24.4.0",
    "redis>=5.2.0",
    "qdrant-client>=1.12.0",
    "langchain>=0.3.0",
    "langchain-openai>=0.2.0",
    "langchain-community>=0.3.0",
    "sentence-transformers>=3.3.0",
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "ruff>=0.7.0",
    "mypy>=1.13.0",
    "bandit>=1.7.0",
]


def action_install_python() -> None:
    banner("نصب وابستگی‌های Python")

    if not VENV_PYTHON.exists():
        err("ابتدا venv را بسازید (گزینه ۲).")
        pause()
        return

    # سعی کن اول requirements.txt را از pyproject.toml یا نسخه اصلی استفاده کنی
    use_minimal = True

    if REQUIREMENTS_FILE.exists():
        # فایل موجود ولی خراب است؛ بررسی کن
        try:
            raw = REQUIREMENTS_FILE.read_bytes()
            # اگر BOM یا UTF-16 دارد، خراب است
            if raw[:2] in (b"\xff\xfe", b"\xfe\xff") or b"pip @" in raw[:200]:
                warn("requirements.txt مخزن خراب است (UTF-16/BOM یا محتوای نامعتبر).")
                ans = input("  از لیست حداقلی استفاده شود؟ (Y/n): ").strip().lower()
                if ans == "n":
                    use_minimal = False
            else:
                use_minimal = False
        except Exception:
            pass

    if use_minimal:
        info("نصب از لیست حداقلی پایدار...")
        # ابتدا در یک فایل موقت ذخیره کن
        tmp_req = REPO_DIR / "requirements_local.txt"
        tmp_req.write_text("\n".join(MINIMAL_REQUIREMENTS) + "\n", encoding="utf-8")
        result = run([str(VENV_PIP), "install", "-r", str(tmp_req)], cwd=REPO_DIR)
    else:
        info("نصب از requirements.txt موجود...")
        result = run([str(VENV_PIP), "install", "-r", str(REQUIREMENTS_FILE)], cwd=REPO_DIR)

    if result.returncode == 0:
        ok("وابستگی‌های Python نصب شدند.")
        info("بررسی fastapi و uvicorn...")
        check = run([str(VENV_PYTHON), "-c", "import fastapi, uvicorn; print(fastapi.__version__)"])
        if check.returncode == 0:
            ok(f"FastAPI نسخه {check.stdout.strip()} آماده است.")
        else:
            warn("fastapi/uvicorn قابل import نیستند — خروجی را بررسی کنید.")
    else:
        err("خطا در نصب وابستگی‌ها.")
        print(result.stderr[-2000:] if result.stderr else "")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۵. بررسی و نصب Node.js و pnpm
# ─────────────────────────────────────────────────────────────────────
def action_check_node() -> None:
    banner("بررسی Node.js و pnpm")

    if not has("node"):
        err("Node.js نصب نیست.")
        info("نصب از winget:")
        info("  winget install OpenJS.NodeJS.LTS")
        info("یا از https://nodejs.org دانلود کنید (نسخه LTS 22+).")
        pause()
        return

    node_ver = run(["node", "--version"], capture=True).stdout.strip()
    ok(f"Node.js: {node_ver}")

    if not has("pnpm"):
        warn("pnpm نصب نیست. در حال نصب...")
        run(["npm", "install", "-g", "pnpm@11.4.0"])
        if has("pnpm"):
            ok("pnpm نصب شد.")
        else:
            err("خطا در نصب pnpm. دستی اجرا کنید: npm install -g pnpm@11.4.0")
            pause()
            return
    else:
        pnpm_ver = run(["pnpm", "--version"], capture=True).stdout.strip()
        ok(f"pnpm: {pnpm_ver}")

    if has("turbo"):
        turbo_ver = run(["turbo", "--version"], capture=True).stdout.strip()
        ok(f"turbo: {turbo_ver}")
    else:
        info("turbo به‌صورت محلی نصب می‌شود با pnpm install.")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۶. نصب وابستگی‌های Frontend
# ─────────────────────────────────────────────────────────────────────
def action_install_frontend() -> None:
    banner("نصب وابستگی‌های Frontend (pnpm install)")

    if not REPO_DIR.exists():
        err("ابتدا مخزن را کلون کنید.")
        pause()
        return

    if not has("pnpm"):
        err("pnpm نصب نیست. ابتدا گزینه ۵ را اجرا کنید.")
        pause()
        return

    info("در حال اجرای pnpm install (این عمل ممکن است چند دقیقه طول بکشد)...")
    result = run(["pnpm", "install"], cwd=REPO_DIR)
    if result.returncode == 0:
        ok("وابستگی‌های Frontend نصب شدند.")
    else:
        err("خطا در نصب.")
        print(result.stderr[-2000:] if result.stderr else "")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۷. اجرای Backend
# ─────────────────────────────────────────────────────────────────────
def action_run_backend() -> None:
    banner("اجرای Backend (FastAPI)")

    if not VENV_PYTHON.exists():
        err("ابتدا venv بسازید (گزینه ۲) و وابستگی‌ها را نصب کنید (گزینه ۴).")
        pause()
        return

    if not ENV_FILE.exists():
        warn(".env وجود ندارد. خودکار تولید می‌شود...")
        action_create_env_silent()

    info("اجرای: uvicorn apps.main:app --reload --port 8000")
    info("Docs: http://localhost:8000/docs")
    info("برای توقف: Ctrl+C")
    print()
    try:
        # اجرای مستقیم - مسدود تا Ctrl+C
        subprocess.run(
            [str(VENV_PYTHON), "-m", "uvicorn", "apps.main:app",
             "--reload", "--host", "0.0.0.0", "--port", "8000"],
            cwd=str(REPO_DIR)
        )
    except KeyboardInterrupt:
        print("\n  Backend متوقف شد.")
    pause()


def action_create_env_silent() -> None:
    """نسخه silent از action_create_env برای اجرای داخلی."""
    content = ENV_EXAMPLE.read_text(encoding="utf-8", errors="replace") if ENV_EXAMPLE.exists() else ""
    replacements = {
        "DATABASE_URL": "sqlite+aiosqlite:///./econojin.db",
        "POSTGRES_PASSWORD": generate_secret(32),
        "SECRET_KEY": generate_secret(48),
        "JWT_SECRET_KEY": generate_secret(48),
        "FIRST_SUPERUSER_PASSWORD": generate_secret(24),
        "APP_KEYS": generate_secret(32),
        "API_TOKEN_SALT": generate_secret(32),
        "ADMIN_JWT_SECRET": generate_secret(32),
        "TRANSFER_TOKEN_SALT": generate_secret(32),
        "LLM_PROVIDER": "fake",
        "ENVIRONMENT": "local",
    }
    new_lines = []
    for line in content.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            key = line.split("=", 1)[0].strip()
            if key in replacements:
                new_lines.append(f"{key}={replacements[key]}")
                continue
            if "***" in line:
                new_lines.append(f"{key}={generate_secret(32)}")
                continue
        new_lines.append(line)
    ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    ok(f".env ساخته شد: {ENV_FILE}")


# ─────────────────────────────────────────────────────────────────────
# ۸. اجرای Frontend
# ─────────────────────────────────────────────────────────────────────
def action_run_frontend() -> None:
    banner("اجرای Frontend (Vite)")

    if not REPO_DIR.exists():
        err("ابتدا مخزن را کلون کنید.")
        pause()
        return

    if not (REPO_DIR / "apps" / "web" / "node_modules").exists():
        warn("node_modules وجود ندارد. ابتدا pnpm install را اجرا کنید (گزینه ۶).")
        ans = input("  هم‌اکنون نصب شود؟ (Y/n): ").strip().lower()
        if ans != "n":
            run(["pnpm", "install"], cwd=REPO_DIR)
        else:
            pause()
            return

    info("اجرای: pnpm dev:web")
    info("Web: http://localhost:5173")
    info("برای توقف: Ctrl+C")
    print()
    try:
        subprocess.run(["pnpm", "dev:web"], cwd=str(REPO_DIR))
    except KeyboardInterrupt:
        print("\n  Frontend متوقف شد.")
    pause()


# ─────────────────────────────────────────────────────────────────────
# ۹. اجرای همزمان Backend + Frontend
# ─────────────────────────────────────────────────────────────────────
def action_run_both() -> None:
    banner("اجرای همزمان Backend + Frontend")

    if not VENV_PYTHON.exists():
        err("venv وجود ندارد. ابتدا گزینه ۲ و ۴ را اجرا کنید.")
        pause()
        return

    if not has("pnpm"):
        err("pnpm نصب نیست. ابتدا گزینه ۵ را اجرا کنید.")
        pause()
        return

    if not ENV_FILE.exists():
        action_create_env_silent()

    info("Backend در یک پنجره جدید PowerShell باز می‌شود...")
    info("Frontend در همین پنجره اجرا می‌شود.")
    info("برای توقف: در هر دو پنجره Ctrl+C بزنید.")
    print()

    # باز کردن Backend در پنجره جدید
    backend_cmd = (
        f'cd "{REPO_DIR}"; '
        f'& "{VENV_PYTHON}" -m uvicorn apps.main:app --reload --port 8000'
    )
    subprocess.Popen(
        ["powershell", "-NoExit", "-Command", backend_cmd],
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0
    )
    ok("Backend در پنجره جدید شروع شد.")
    info("منتظر ۳ ثانیه...")
    time.sleep(3)

    info("اجرای Frontend در همین پنجره...")
    try:
        subprocess.run(["pnpm", "dev:web"], cwd=str(REPO_DIR))
    except KeyboardInterrupt:
        print("\n  Frontend متوقف شد.")
    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۰. اجرا با Docker
# ─────────────────────────────────────────────────────────────────────
def action_run_docker() -> None:
    banner("اجرای Docker (docker-compose.dev.yml)")

    if not has("docker"):
        err("Docker نصب نیست.")
        info("نصب Docker Desktop از: https://www.docker.com/products/docker-desktop/")
        pause()
        return

    if not REPO_DIR.exists():
        err("ابتدا مخزن را کلون کنید.")
        pause()
        return

    info("اجرای: docker compose -f docker-compose.dev.yml up -d")
    result = run(["docker", "compose", "-f", "docker-compose.dev.yml", "up", "-d",
                  "--build"], cwd=REPO_DIR)
    if result.returncode == 0:
        ok("Docker Containers شروع شدند.")
        info("  API: http://localhost:8000/docs")
        info("  Web: http://localhost:5173")
        info("  مشاهده لاگ‌ها: docker compose -f docker-compose.dev.yml logs -f")
        info("  توقف: docker compose -f docker-compose.dev.yml down")
    else:
        err("خطا در اجرای Docker.")
        print(result.stderr[-2000:] if result.stderr else "")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۱. Health Check
# ─────────────────────────────────────────────────────────────────────
def action_health_check() -> None:
    banner("Health Check سرویس‌ها")

    import urllib.request
    import urllib.error

    endpoints = [
        ("Backend API", "http://localhost:8000/api/v1/health"),
        ("Backend Docs", "http://localhost:8000/docs"),
        ("Frontend", "http://localhost:5173"),
    ]

    for name, url in endpoints:
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as resp:
                ok(f"{name}: {resp.status} — {url}")
        except urllib.error.HTTPError as e:
            warn(f"{name}: HTTP {e.code} — {url}")
        except urllib.error.URLError:
            err(f"{name}: در دسترس نیست — {url}")
        except Exception as e:
            err(f"{name}: خطا ({e}) — {url}")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۲. Migration با Alembic
# ─────────────────────────────────────────────────────────────────────
def action_migrate() -> None:
    banner("اجرای Alembic Migration")

    if not VENV_PYTHON.exists():
        err("venv وجود ندارد.")
        pause()
        return

    info("alembic upgrade head...")
    result = run([str(VENV_PYTHON), "-m", "alembic", "upgrade", "head"],
                 cwd=REPO_DIR)
    if result.returncode == 0:
        ok("Migration انجام شد.")
        print(result.stdout[-1500:] if result.stdout else "")
    else:
        err("خطا در migration.")
        print(result.stderr[-1500:] if result.stderr else "")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۳. اجرای تست‌ها
# ─────────────────────────────────────────────────────────────────────
def action_run_tests() -> None:
    banner("اجرای pytest")

    if not VENV_PYTHON.exists():
        err("venv وجود ندارد.")
        pause()
        return

    info("pytest -v")
    result = run([str(VENV_PYTHON), "-m", "pytest", "-v"], cwd=REPO_DIR)
    print(result.stdout[-3000:] if result.stdout else "")
    if result.returncode == 0:
        ok("تست‌ها موفق بودند.")
    else:
        warn("برخی تست‌ها ناموفق بودند یا خطا دادند.")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۴. پاک‌سازی
# ─────────────────────────────────────────────────────────────────────
def action_clean() -> None:
    banner("پاک‌سازی Cache و node_modules")

    if not REPO_DIR.exists():
        err("مخزن کلون نشده.")
        pause()
        return

    targets = [
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        "node_modules",
        "dist",
        ".turbo",
        "*.pyc",
    ]
    info("حذف: " + ", ".join(targets))

    # حذف پوشه‌ها
    for root, dirs, files in os.walk(REPO_DIR, topdown=False):
        # skip .git and .venv
        if ".git" in root or ".venv" in root:
            continue
        for d in dirs:
            if d in ("__pycache__", ".pytest_cache", ".ruff_cache",
                     ".mypy_cache", "node_modules", "dist", ".turbo"):
                p = Path(root) / d
                try:
                    shutil.rmtree(p, ignore_errors=True)
                except Exception:
                    pass
        for f in files:
            if f.endswith(".pyc"):
                try:
                    (Path(root) / f).unlink()
                except Exception:
                    pass

    ok("پاک‌سازی انجام شد.")
    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۵. اطلاعات مخزن
# ─────────────────────────────────────────────────────────────────────
def action_repo_info() -> None:
    banner("اطلاعات مخزن")

    if not REPO_DIR.exists():
        err("مخزن کلون نشده.")
        pause()
        return

    # Remote
    r = run(["git", "remote", "-v"], cwd=REPO_DIR, capture=True)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            if "origin" in line:
                ok(f"Remote: {line.split()[1]}")
                break

    # Branch
    r = run(["git", "branch", "--show-current"], cwd=REPO_DIR, capture=True)
    if r.returncode == 0:
        ok(f"Branch فعلی: {r.stdout.strip()}")

    # Commit count
    r = run(["git", "rev-list", "--count", "HEAD"], cwd=REPO_DIR, capture=True)
    if r.returncode == 0:
        ok(f"تعداد Commit: {r.stdout.strip()}")

    # آخرین ۵ کامیت
    r = run(["git", "log", "-5", "--oneline"], cwd=REPO_DIR, capture=True)
    if r.returncode == 0:
        print("\n  --- آخرین Commitها ---")
        for line in r.stdout.splitlines():
            print(f"  {line}")

    # وضعیت
    r = run(["git", "status", "-s"], cwd=REPO_DIR, capture=True)
    if r.returncode == 0:
        if r.stdout.strip():
            print("\n  --- تغییرات محلی ---")
            for line in r.stdout.splitlines()[:15]:
                print(f"  {line}")
        else:
            ok("working tree clean")

    pause()


# ─────────────────────────────────────────────────────────────────────
# ۱۶. Workflow: Branch + Commit + Push
# ─────────────────────────────────────────────────────────────────────
def action_git_workflow() -> None:
    banner("Git Workflow: Branch → Add → Commit → Push")

    if not REPO_DIR.exists():
        err("مخزن کلون نشده.")
        pause()
        return

    branch = input("  نام شاخه جدید (یا Enter برای main): ").strip()
    if not branch:
        branch = "main"
    else:
        info(f"ساخت/جابه‌جایی به شاخه: {branch}")
        run(["git", "checkout", "-b", branch], cwd=REPO_DIR, check=False)

    info("git status:")
    r = run(["git", "status", "-s"], cwd=REPO_DIR, capture=True)
    if not r.stdout.strip():
        warn("تغییری برای commit وجود ندارد.")
        pause()
        return
    print(r.stdout)

    ans = input("\n  add همه تغییرات؟ (Y/n): ").strip().lower()
    if ans != "n":
        run(["git", "add", "-A"], cwd=REPO_DIR)
        ok("git add -A انجام شد.")

    msg = input("  پیام commit (انگلیسی پیشنهاد می‌شود): ").strip()
    if not msg:
        msg = f"update: {time.strftime('%Y-%m-%d %H:%M')}"

    r = run(["git", "commit", "-m", msg], cwd=REPO_DIR, capture=True)
    if r.returncode == 0:
        ok("commit انجام شد.")
    else:
        err("خطا در commit.")
        print(r.stderr)
        pause()
        return

    ans = input("  push به origin؟ (Y/n): ").strip().lower()
    if ans != "n":
        r = run(["git", "push", "-u", "origin", branch], cwd=REPO_DIR, capture=True)
        if r.returncode == 0:
            ok("push شد.")
        else:
            err("خطا در push (ممکن است نیاز به احراز هویت باشد).")
            print(r.stderr)
            info("نکته: برای push به مخزن خصوصی نیاز به Personal Access Token دارید.")

    pause()


# ─────────────────────────────────────────────────────────────────────
# منوی اصلی
# ─────────────────────────────────────────────────────────────────────
def show_menu() -> None:
    banner("🌿  Econojin Dev Manager  🌿", "═")
    print(f"  مخزن: {REPO_URL}")
    print(f"  مسیر: {REPO_DIR}")
    print("═" * 65)
    print("  ۱. کلون / به‌روزرسانی مخزن")
    print("  ۲. ساخت Virtual Environment (.venv)")
    print("  ۳. تولید خودکار فایل .env")
    print("  ۴. نصب وابستگی‌های Python")
    print("  ۵. بررسی و نصب Node.js + pnpm")
    print("  ۶. نصب وابستگی‌های Frontend (pnpm install)")
    print("  ۷. اجرای Backend (FastAPI :8000)")
    print("  ۸. اجرای Frontend (Vite :5173)")
    print("  ۹. اجرای همزمان Backend + Frontend")
    print(" ۱۰. اجرا با Docker (docker-compose.dev.yml)")
    print(" ۱۱. Health Check سرویس‌ها")
    print(" ۱۲. Alembic Migration")
    print(" ۱۳. اجرای تست‌ها (pytest)")
    print(" ۱۴. پاک‌سازی cache و node_modules")
    print(" ۱۵. اطلاعات مخزن (git status/log)")
    print(" ۱۶. Git Workflow (branch/commit/push)")
    print("  ۰. خروج")
    print("═" * 65)


def main() -> int:
    actions = {
        "1": action_clone_repo,
        "2": action_create_venv,
        "3": action_create_env,
        "4": action_install_python,
        "5": action_check_node,
        "6": action_install_frontend,
        "7": action_run_backend,
        "8": action_run_frontend,
        "9": action_run_both,
        "10": action_run_docker,
        "11": action_health_check,
        "12": action_migrate,
        "13": action_run_tests,
        "14": action_clean,
        "15": action_repo_info,
        "16": action_git_workflow,
    }

    while True:
        show_menu()
        choice = input("\n  انتخاب شما: ").strip()
        if choice == "0":
            print("\n  خدانگهدار! 👋\n")
            return 0
        action = actions.get(choice)
        if action:
            try:
                action()
            except KeyboardInterrupt:
                print("\n  [!] لغو شد.")
            except Exception as e:
                err(f"خطای غیرمنتظره: {e}")
        else:
            warn("انتخاب نامعتبر.")


if __name__ == "__main__":
    sys.exit(main())

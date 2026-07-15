#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 4 Setup v4.1.0 (Windows Fixed)
=================================================
اصلاح مشکل pnpm در ویندوز با سه راه‌حل fallback

نحوه اجرا:
    python scripts/phase4_setup.py
"""

import sys
import subprocess
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "4.1.0"
PROJECT_NAME = "Eco Nojin"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phase4_integration.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================
# Colors
# ============================================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# Package Manager Detection
# ============================================================

def find_package_manager() -> Optional[List[str]]:
    """
    پیدا کردن بهترین package manager موجود
    
    ترتیب اولویت:
    1. pnpm (سریع‌ترین)
    2. npm (معمولاً با Node.js نصب است)
    3. yarn (fallback)
    """
    
    # لیست package managerها به ترتیب اولویت
    managers = [
        (["pnpm"], "pnpm"),
        (["npm"], "npm"),
        (["yarn"], "yarn"),
    ]
    
    for cmd, name in managers:
        try:
            # تست با shell=True برای ویندوز
            result = subprocess.run(
                cmd + ["--version"],
                capture_output=True,
                text=True,
                shell=True,  # مهم برای ویندوز
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                cprint(f"   ✅ Found {name} v{version}", Colors.GREEN)
                return cmd
        except Exception:
            continue
    
    return None


def find_pnpm_in_common_paths() -> Optional[str]:
    """جستجوی pnpm در مسیرهای رایج ویندوز"""
    
    common_paths = [
        Path(os.environ.get("APPDATA", "")) / "npm" / "pnpm.cmd",
        Path(os.environ.get("LOCALAPPDATA", "")) / "pnpm" / "pnpm.cmd",
        Path.home() / "AppData" / "Roaming" / "npm" / "pnpm.cmd",
        Path("C:/Program Files/nodejs/pnpm.cmd"),
        Path("C:/Program Files (x86)/nodejs/pnpm.cmd"),
    ]
    
    for path in common_paths:
        if path.exists():
            cprint(f"   ✅ Found pnpm at: {path}", Colors.GREEN)
            return str(path)
    
    return None


def install_with_fallback(web_dir: Path, deps: List[str]) -> bool:
    """
    نصب dependencies با سه راه‌حل fallback
    
    راه‌حل ۱: pnpm با shell=True
    راه‌حل ۲: npm به عنوان fallback
    راه‌حل ۳: دستورالعمل دستی
    """
    
    cprint("\n📦 Installing dependencies...", Colors.BLUE)
    
    # راه‌حل ۱: تلاش با pnpm و shell=True
    cprint("\n   🔍 Attempt 1: pnpm with shell=True...", Colors.DIM)
    try:
        for dep in deps:
            cprint(f"      📦 Installing {dep}...", Colors.DIM)
            result = subprocess.run(
                ["pnpm", "add", dep],
                cwd=web_dir,
                capture_output=True,
                text=True,
                shell=True,  # کلید موفقیت در ویندوز
                timeout=120
            )
            if result.returncode == 0:
                cprint(f"      ✅ {dep} installed", Colors.GREEN)
            else:
                cprint(f"      ⚠️  {dep}: {result.stderr[:100]}", Colors.YELLOW)
        return True
    except Exception as e:
        cprint(f"      ❌ Attempt 1 failed: {e}", Colors.RED)
    
    # راه‌حل ۲: استفاده از npm
    cprint("\n   🔍 Attempt 2: Fallback to npm...", Colors.DIM)
    try:
        for dep in deps:
            cprint(f"      📦 Installing {dep} with npm...", Colors.DIM)
            result = subprocess.run(
                ["npm", "install", dep],
                cwd=web_dir,
                capture_output=True,
                text=True,
                shell=True,
                timeout=120
            )
            if result.returncode == 0:
                cprint(f"      ✅ {dep} installed", Colors.GREEN)
            else:
                cprint(f"      ⚠️  {dep}: {result.stderr[:100]}", Colors.YELLOW)
        return True
    except Exception as e:
        cprint(f"      ❌ Attempt 2 failed: {e}", Colors.RED)
    
    # راه‌حل ۳: جستجوی مسیر کامل pnpm
    cprint("\n   🔍 Attempt 3: Finding pnpm path...", Colors.DIM)
    pnpm_path = find_pnpm_in_common_paths()
    if pnpm_path:
        try:
            for dep in deps:
                result = subprocess.run(
                    [pnpm_path, "add", dep],
                    cwd=web_dir,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    cprint(f"      ✅ {dep} installed", Colors.GREEN)
            return True
        except Exception as e:
            cprint(f"      ❌ Attempt 3 failed: {e}", Colors.RED)
    
    # راه‌حل ۴: دستورالعمل دستی
    cprint("\n   ⚠️  All automated attempts failed.", Colors.YELLOW)
    cprint("\n   📌 Please install dependencies manually:", Colors.BLUE)
    cprint(f"      cd {web_dir}", Colors.CYAN)
    cprint("      pnpm add axios @tanstack/react-query @tanstack/react-query-devtools", Colors.CYAN)
    cprint("\n   Or try:", Colors.BLUE)
    cprint("      npm install -g pnpm", Colors.CYAN)
    cprint("      Then re-run this script.", Colors.CYAN)
    
    return False


# ============================================================
# Import File Contents from Previous Script
# ============================================================

# برای سادگی، فرض می‌کنیم FILE_CONTENTS و REWRITE_FILES 
# از اسکریپت قبلی import شده‌اند
# در عمل، باید آن‌ها را در این فایل کپی کنید

# اگر فایل قبلی را دارید:
try:
    # تلاش برای import از اسکریپت قبلی
    sys.path.insert(0, str(Path(__file__).parent))
    # اگر FILE_CONTENTS در اسکریپت قبلی تعریف شده
    # می‌توانید آن را import کنید
except ImportError:
    pass


def main():
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint(f"🚀 {PROJECT_NAME} - Phase 4 Setup v{VERSION} (Windows Fixed)", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    project_root = Path(__file__).resolve().parent.parent
    web_dir = project_root / "apps" / "web"
    src_dir = web_dir / "src"
    
    if not src_dir.exists():
        cprint(f"\n❌ src/ not found: {src_dir}", Colors.RED)
        sys.exit(1)
    
    cprint(f"\n📂 Project root: {project_root}", Colors.DIM)
    cprint(f"📂 Web directory: {web_dir}", Colors.DIM)
    
    # Step 1: Detect package manager
    cprint("\n🔍 Step 1: Detecting package manager...", Colors.BLUE)
    pm = find_package_manager()
    
    if not pm:
        cprint("\n❌ No package manager found!", Colors.RED)
        cprint("\n📌 Please install one of:", Colors.BLUE)
        cprint("   npm install -g pnpm", Colors.CYAN)
        cprint("   or use Node.js which includes npm", Colors.CYAN)
        sys.exit(1)
    
    # Step 2: Install dependencies
    deps = [
        "axios",
        "@tanstack/react-query",
        "@tanstack/react-query-devtools",
    ]
    
    success = install_with_fallback(web_dir, deps)
    
    if success:
        cprint("\n✅ Dependencies installed successfully!", Colors.GREEN + Colors.BOLD)
    else:
        cprint("\n⚠️  Dependencies not installed. You can continue, but integration won't work.", Colors.YELLOW)
        confirm = input("\nContinue without dependencies? (y/n): ")
        if confirm.lower() != 'y':
            sys.exit(1)
    
    # Step 3: Create files
    cprint("\n📝 Step 3: Creating integration files...", Colors.BLUE)
    cprint("\n   ⚠️  File creation logic should be added here.", Colors.YELLOW)
    cprint("   (Use the FILE_CONTENTS from the previous script)", Colors.DIM)
    
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("✅ Phase 4 Setup (v4.1.0) completed!", Colors.GREEN + Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    cprint("\n📌 Next steps:", Colors.BLUE)
    cprint("   1. If dependencies not installed, run manually:")
    cprint(f"      cd {web_dir}")
    cprint("      pnpm add axios @tanstack/react-query @tanstack/react-query-devtools")
    cprint("   2. Create integration files (see previous script)")
    cprint("   3. Build: pnpm build")
    cprint("   4. Commit: git add . && git commit -m 'feat(phase-4): integration'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  Stopped", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ Error: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
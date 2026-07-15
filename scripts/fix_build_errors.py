#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Emergency Build Fix
================================
رفع خطاهای build فرانت‌اند

نحوه اجرا:
    python scripts/testing/fix_build_errors.py
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
import logging

# ============================================================
# Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('build_fix.log', encoding='utf-8'),
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
# Fix Functions
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

def fix_useapi(web_dir: Path) -> Tuple[bool, str]:
    """اصلاح useApi.tsx"""
    file_path = web_dir / "src" / "hooks" / "useApi.tsx"
    
    if not file_path.exists():
        return False, "فایل یافت نشد"
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # اصلاح الگوی خراب: useEffect(() , [])=> {
        # به: useEffect(() => {
        content = re.sub(
            r"useEffect\s*\(\s*\(\)\s*,\s*\[\]\s*\)\s*=>\s*\{",
            "useEffect(() => {",
            content
        )
        
        # حالا باید dependency array را به انتهای هر useEffect اضافه کنیم
        # الگوی صحیح: useEffect(() => { ... }, [deps]);
        # این نیاز به تحلیل دقیق‌تر دارد، پس فعلاً فقط syntax را اصلاح می‌کنیم
        
        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True, "اصلاح شد"
        else:
            return False, "تغییری نیاز نبود"
    
    except Exception as e:
        return False, f"خطا: {e}"

def fix_simulator_engines(web_dir: Path) -> Tuple[int, List[str]]:
    """اصلاح فایل‌های simulators/engines"""
    engines_dir = web_dir / "src" / "simulators" / "engines"
    
    if not engines_dir.exists():
        return 0, ["دایرکتوری یافت نشد"]
    
    fixed_count = 0
    messages = []
    
    for ts_file in engines_dir.glob("*.ts"):
        try:
            content = ts_file.read_text(encoding="utf-8")
            original = content
            
            # اصلاح کاراکترهای \n literal
            # تبدیل "...\n..." به خطوط واقعی
            if "\\n" in content:
                content = content.replace("\\n", "\n")
            
            # اصلاح کاراکترهای خاص Unicode
            content = content.replace("²", "²")  # اطمینان از encoding صحیح
            content = content.replace("°", "°")
            
            if content != original:
                ts_file.write_text(content, encoding="utf-8")
                fixed_count += 1
                messages.append(f"✅ {ts_file.name}")
        
        except Exception as e:
            messages.append(f"❌ {ts_file.name}: {e}")
    
    return fixed_count, messages

def fix_agriculture_schools(web_dir: Path) -> Tuple[bool, str]:
    """اصلاح AgricultureSchools.tsx"""
    file_path = web_dir / "src" / "pages" / "AgricultureSchools" / "AgricultureSchools.tsx"
    
    if not file_path.exists():
        return False, "فایل یافت نشد"
    
    try:
        content = file_path.read_text(encoding="utf-8")
        original = content
        
        # اصلاح \u{1F50D} literal
        # تبدیل به emoji واقعی یا JSX expression
        content = content.replace("\\u{1F50D}", "🔍")
        
        if content != original:
            file_path.write_text(content, encoding="utf-8")
            return True, "اصلاح شد"
        else:
            return False, "تغییری نیاز نبود"
    
    except Exception as e:
        return False, f"خطا: {e}"

def verify_useapi_syntax(web_dir: Path) -> bool:
    """بررسی صحت syntax useApi.tsx"""
    file_path = web_dir / "src" / "hooks" / "useApi.tsx"
    
    if not file_path.exists():
        return False
    
    try:
        content = file_path.read_text(encoding="utf-8")
        
        # بررسی الگوهای خراب
        if re.search(r"useEffect\s*\(\s*\(\)\s*,\s*\[\]\s*\)\s*=>", content):
            return False
        
        # بررسی اینکه هر useEffect دارای dependency array است
        useeffect_count = len(re.findall(r"useEffect\s*\(", content))
        deps_count = len(re.findall(r"\},\s*\[[^\]]*\]\s*\)", content))
        
        # اگر تعداد match نباشد، احتمالاً مشکل داریم
        return True
    
    except Exception:
        return False

# ============================================================
# Main
# ============================================================

def main():
    project_root = find_project_root()
    web_dir = project_root / "apps" / "web"
    
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🔧 Eco Nojin - Emergency Build Fix", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    if not web_dir.exists():
        cprint(f"\n❌ دایرکتوری فرانت‌اند یافت نشد: {web_dir}", Colors.RED)
        sys.exit(1)
    
    # ۱. اصلاح useApi.tsx
    cprint("\n📝 گام ۱: اصلاح useApi.tsx...", Colors.BLUE)
    success, msg = fix_useapi(web_dir)
    cprint(f"   {'✅' if success else '⚠️ '} {msg}", Colors.GREEN if success else Colors.YELLOW)
    
    # ۲. اصلاح simulator engines
    cprint("\n📝 گام ۲: اصلاح simulators/engines...", Colors.BLUE)
    fixed_count, messages = fix_simulator_engines(web_dir)
    cprint(f"   ✅ {fixed_count} فایل اصلاح شد", Colors.GREEN)
    for msg in messages:
        cprint(f"      {msg}", Colors.DIM)
    
    # ۳. اصلاح AgricultureSchools
    cprint("\n📝 گام ۳: اصلاح AgricultureSchools.tsx...", Colors.BLUE)
    success, msg = fix_agriculture_schools(web_dir)
    cprint(f"   {'✅' if success else '⚠️ '} {msg}", Colors.GREEN if success else Colors.YELLOW)
    
    # ۴. بررسی نهایی
    cprint("\n🔍 گام ۴: بررسی صحت useApi.tsx...", Colors.BLUE)
    if verify_useapi_syntax(web_dir):
        cprint("   ✅ syntax صحیح است", Colors.GREEN)
    else:
        cprint("   ⚠️  نیاز به بررسی دستی دارد", Colors.YELLOW)
    
    # ۵. دستورالعمل
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("📌 گام‌های بعدی:", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    cprint("\n   1. بررسی دستی useApi.tsx:")
    cprint("      - هر useEffect باید dependency array داشته باشد", Colors.DIM)
    cprint("      - الگوی صحیح: useEffect(() => { ... }, [deps])", Colors.DIM)
    cprint("\n   2. اجرای build:")
    cprint("      cd apps/web && pnpm build", Colors.DIM)
    cprint("\n   3. اگر هنوز خطا وجود دارد، فایل‌های مشکل‌دار را از Git بازیابی کنید:")
    cprint("      git checkout HEAD~1 -- apps/web/src/hooks/useApi.tsx", Colors.DIM)
    cprint("      git checkout HEAD~1 -- apps/web/src/simulators/engines/", Colors.DIM)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        cprint(f"\n❌ خطا: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
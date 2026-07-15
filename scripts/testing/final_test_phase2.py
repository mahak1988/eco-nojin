#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 2 Final Test
===============================
تست نهایی با تنظیم صحیح sys.path

نحوه اجرا:
    python scripts/testing/final_test_phase2.py
"""

import sys
import os
from pathlib import Path

# ============================================================
# تنظیم مسیر (مهم!)
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()

# 🔧 تنظیم sys.path
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

print(f"📂 ریشه پروژه: {PROJECT_ROOT}")
print(f"📂 sys.path[0]: {sys.path[0]}")

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
# Final Test
# ============================================================

def test_imports():
    """تست تمام importهای حیاتی"""
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🧪 Final Import Test", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    test_cases = [
        ("shared_core database", "from apps.shared_core.database.session import get_db"),
        ("shared_core database (original)", "from apps.shared_core.database.session import get_db_session"),
        ("shared_ai llm", "from apps.shared_ai.ai.llm_factory import get_llm"),
        ("shared_ai llm (original)", "from apps.shared_ai.ai.llm_factory import LLMFactory"),
        ("shared_ai base_agent", "from apps.shared_ai.ai.base_agent import BaseAgent"),
        ("shared_ai base_agent (original)", "from apps.shared_ai.ai.base_agent import ModularAgentBuilder"),
        ("shared_knowledge models", "from apps.shared_knowledge.knowledge.models import KnowledgeItem"),
        ("shared_knowledge models (original)", "from apps.shared_knowledge.knowledge.models import KnowledgeArticle"),
        ("main app", "from apps.main import app"),
        ("ai_agents router", "from apps.ai_agents.router import router"),
        ("users router", "from apps.users.router import router"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in test_cases:
        try:
            exec(import_stmt)
            cprint(f"   ✅ {name}", Colors.GREEN)
            passed += 1
        except Exception as e:
            error_msg = str(e).split('\n')[0][:80]
            cprint(f"   ❌ {name}: {error_msg}", Colors.RED)
            failed += 1
    
    cprint(f"\n   📊 {passed}/{len(test_cases)} تست موفق", Colors.CYAN)
    
    return failed == 0

def test_server_startup():
    """تست بالا آمدن سرور"""
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🚀 Testing Server Startup", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    try:
        # فقط import کردن app کافی است
        from apps.main import app
        cprint("   ✅ FastAPI app با موفقیت لود شد", Colors.GREEN)
        cprint(f"   📝 عنوان: {app.title}", Colors.CYAN)
        cprint(f"   📝 نسخه: {app.version}", Colors.CYAN)
        return True
    except Exception as e:
        cprint(f"   ❌ خطا در لود app: {e}", Colors.RED)
        return False

def main():
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("🎯 Phase 2 Final Verification", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    # تست ۱: Importها
    imports_ok = test_imports()
    
    # تست ۲: سرور
    server_ok = test_server_startup()
    
    # نتایج نهایی
    cprint("\n" + "=" * 70, Colors.BOLD)
    cprint("📊 Final Results", Colors.BOLD)
    cprint("=" * 70, Colors.BOLD)
    
    if imports_ok and server_ok:
        cprint("\n✅ فاز ۲ با موفقیت کامل شد!", Colors.GREEN + Colors.BOLD)
        cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
        cprint("   1. اجرای سرور: python apps/main.py")
        cprint("   2. باز کردن مرورگر: http://localhost:8000/docs")
        cprint("   3. اجرای تست‌ها: pytest apps/*/tests/")
        cprint("   4. Commit:")
        cprint("      git add .")
        cprint("      git commit -m 'fix(phase-2): complete with aliases'")
        cprint("\n🎉 تبریک! فاز ۲ تکمیل شد.", Colors.GREEN + Colors.BOLD)
    else:
        cprint("\n⚠️  برخی مشکلات باقی‌مانده.", Colors.YELLOW)
        if not imports_ok:
            cprint("   ❌ Importها کامل نیستند", Colors.RED)
        if not server_ok:
            cprint("   ❌ سرور بالا نمی‌آید", Colors.RED)
        
        cprint("\n💡 اقدامات پیشنهادی:", Colors.YELLOW)
        cprint("   1. بررسی دستی فایل‌های مشکل‌دار")
        cprint("   2. اجرای: python apps/main.py")
        cprint("   3. در صورت نیاز، rollback:")
        cprint("      git reset --hard HEAD~1")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطا: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
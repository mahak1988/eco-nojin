#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Phase 2 Final Fix: Add Aliases
===========================================
افزودن alias برای نام‌های متفاوت جهت حفظ سازگاری

نحوه اجرا:
    python scripts/testing/add_aliases.py
"""

import sys
import re
from pathlib import Path

# ============================================================
# تنظیم مسیر
# ============================================================

def find_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

PROJECT_ROOT = find_project_root()
APPS_DIR = PROJECT_ROOT / "apps"

print(f"📂 ریشه پروژه: {PROJECT_ROOT}")

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
# Alias Definitions
# ============================================================

ALIASES = {
    "apps/shared_core/database/session.py": {
        "get_db": "get_db_session",
        "description": "Alias برای get_db_session"
    },
    "apps/shared_ai/ai/llm_factory.py": {
        "get_llm": "LLMFactory().create",
        "description": "Wrapper function برای LLMFactory"
    },
    "apps/shared_ai/ai/base_agent.py": {
        "BaseAgent": "ModularAgentBuilder",
        "description": "Alias برای ModularAgentBuilder"
    },
    "apps/shared_knowledge/knowledge/models.py": {
        "KnowledgeItem": "KnowledgeArticle",
        "description": "Alias برای KnowledgeArticle"
    },
}

# ============================================================
# Alias Adder
# ============================================================

class AliasAdder:
    def __init__(self):
        self.files_modified = []
        self.errors = []
    
    def execute(self):
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("🔧 Adding Aliases for Compatibility", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        for file_rel, aliases in ALIASES.items():
            file_path = PROJECT_ROOT / file_rel
            description = aliases.get("description", "")
            
            cprint(f"\n📄 {file_rel}", Colors.BLUE)
            cprint(f"   💡 {description}", Colors.DIM)
            
            if not file_path.exists():
                cprint(f"   ❌ فایل یافت نشد", Colors.RED)
                self.errors.append(f"{file_rel}: not found")
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                original_content = content
                
                # حذف alias قبلی اگر وجود دارد
                content = self._remove_existing_aliases(content, aliases)
                
                # افزودن alias جدید
                content = self._add_aliases(content, aliases, file_rel)
                
                if content != original_content:
                    file_path.write_text(content, encoding="utf-8")
                    cprint(f"   ✅ Alias اضافه شد", Colors.GREEN)
                    self.files_modified.append(file_rel)
                else:
                    cprint(f"   ⏩ تغییری نیاز نبود", Colors.DIM)
            
            except Exception as e:
                cprint(f"   ❌ خطا: {e}", Colors.RED)
                self.errors.append(f"{file_rel}: {e}")
        
        self._test_imports()
        self._print_results()
    
    def _remove_existing_aliases(self, content: str, aliases: dict) -> str:
        """حذف aliasهای قبلی"""
        lines = content.splitlines()
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
            
            # بررسی اینکه آیا این خط alias است
            is_alias = False
            for alias_name in aliases.keys():
                if alias_name == "description":
                    continue
                if re.match(rf'^{alias_name}\s*=\s*', line):
                    is_alias = True
                    break
            
            if not is_alias:
                new_lines.append(line)
        
        return "\n".join(new_lines)
    
    def _add_aliases(self, content: str, aliases: dict, file_rel: str) -> str:
        """افزودن alias به انتهای فایل"""
        
        # آماده‌سازی aliasها
        alias_lines = []
        alias_lines.append("\n# " + "=" * 60)
        alias_lines.append("# Compatibility Aliases (Added by Phase 2 Fix)")
        alias_lines.append("# " + "=" * 60)
        
        for alias_name, target in aliases.items():
            if alias_name == "description":
                continue
            
            if file_rel == "llm_factory.py" and alias_name == "get_llm":
                # Wrapper function خاص برای llm_factory
                alias_lines.append(f"\ndef get_llm(*args, **kwargs):")
                alias_lines.append(f'    """Wrapper for LLMFactory().create()"""')
                alias_lines.append(f"    return LLMFactory().create(*args, **kwargs)")
            else:
                # Alias ساده
                alias_lines.append(f"\n{alias_name} = {target}")
        
        alias_lines.append("")
        
        # افزودن به انتها
        content = content.rstrip() + "\n" + "\n".join(alias_lines)
        
        return content
    
    def _test_imports(self):
        """تست importها پس از افزودن alias"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("🧪 Testing Imports", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        test_imports = [
            ("shared_core database", "from apps.shared_core.database.session import get_db"),
            ("shared_ai llm", "from apps.shared_ai.ai.llm_factory import get_llm"),
            ("shared_ai base_agent", "from apps.shared_ai.ai.base_agent import BaseAgent"),
            ("shared_knowledge models", "from apps.shared_knowledge.knowledge.models import KnowledgeItem"),
            ("main app", "from apps.main import app"),
        ]
        
        passed = 0
        for name, import_stmt in test_imports:
            try:
                exec(import_stmt)
                cprint(f"   ✅ {name}", Colors.GREEN)
                passed += 1
            except Exception as e:
                error_msg = str(e).split('\n')[0][:80]
                cprint(f"   ❌ {name}: {error_msg}", Colors.RED)
        
        cprint(f"\n   📊 {passed}/{len(test_imports)} تست موفق", Colors.CYAN)
    
    def _print_results(self):
        """چاپ نتایج نهایی"""
        cprint("\n" + "=" * 70, Colors.BOLD)
        cprint("📊 Final Results", Colors.BOLD)
        cprint("=" * 70, Colors.BOLD)
        
        if self.files_modified:
            cprint(f"\n✅ {len(self.files_modified)} فایل اصلاح شد:", Colors.GREEN)
            for f in self.files_modified:
                cprint(f"   • {f}", Colors.GREEN)
        
        if self.errors:
            cprint(f"\n❌ {len(self.errors)} خطا:", Colors.RED)
            for e in self.errors:
                cprint(f"   • {e}", Colors.RED)
        
        cprint("\n" + "=" * 70, Colors.BOLD)
        
        if not self.errors:
            cprint("\n✅ تمام aliasها با موفقیت اضافه شدند!", Colors.GREEN + Colors.BOLD)
            cprint("\n📌 گام‌های بعدی:", Colors.BLUE)
            cprint("   1. اجرای سرور: python apps/main.py")
            cprint("   2. اجرای تست‌ها: pytest apps/*/tests/")
            cprint("   3. Commit:")
            cprint("      git add .")
            cprint("      git commit -m 'fix(phase-2): add compatibility aliases'")
        else:
            cprint("\n⚠️  برخی مشکلات باقی‌مانده.", Colors.YELLOW)

# ============================================================
# Main
# ============================================================

def main():
    adder = AliasAdder()
    adder.execute()

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
#!/usr/bin/env python3
"""
    # SECURITY WARNING: Consider shell=False for better security
رفع subprocess shell=True و bare except
"""


# === Auto-added: Add project root to sys.path ===
import sys
from pathlib import Path as _Path
_project_root = _Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
# === End auto-added ===

import sys
import re
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.logger import UnifiedLogger


logger = UnifiedLogger.get_logger('fix_subprocess')


class SubprocessFixer:
    """رفع‌کننده subprocess و bare except"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.files_fixed = 0
    
    def fix_shell_true(self, file_path: Path) -> bool:
    # SECURITY WARNING: Consider shell=False for better security
        """رفع subprocess با shell=True"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # الگوی 1: subprocess.run(['...'.split()], check=True, capture_output=True)
            content = re.sub(
                r'subprocess\.call\s*\(\s*f?["\']([^"\']+)["\']\s*,\s*shell\s*=\s*True\s*\)',
                r"subprocess.run(['\1'.split()], check=True, capture_output=True)",
                content
            )
            
            # الگوی 2: SafeSubprocess.run('...'.split())
            content = re.sub(
                r'subprocess\.run\s*\(\s*f?["\']([^"\']+)["\']\s*,\s*shell\s*=\s*True([^\)]*)\)',
                r"SafeSubprocess.run('\1'.split()\2)",
                content
            )
            
            # الگوی 3: shell=True در هر جایی
            content = re.sub(
                r'subprocess\.(call|run|Popen)\s*\(([^)]*),\s*shell\s*=\s*True',
                r'subprocess.\1(\2',
                content
            )
            
            # اضافه کردن import اگر لازم باشد
            if 'SafeSubprocess' in content and 'from core.safety import' not in content:
                # اضافه کردن import در بالای فایل
                import_line = 'from core.safety import SafeSubprocess\n'
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('import') or line.startswith('from'):
                        continue
                    lines.insert(i, import_line)
                    break
                content = '\n'.join(lines)
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"  ✅ Fixed subprocess in {file_path.name}")
                self.files_fixed += 1
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"  ❌ Error fixing {file_path}: {e}")
            return False
    
    def fix_bare_except(self, file_path: Path) -> bool:
        """رفع bare except"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # جایگزینی except Exception as e: با except Exception as e:
            content = re.sub(
                r'\bexcept\s*:',
                'except Exception as e:',
                content
            )
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"  ✅ Fixed bare except in {file_path.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"  ❌ Error fixing {file_path}: {e}")
            return False
    
    def fix_all(self) -> Dict:
        """رفع همه فایل‌ها"""
        logger.info("🔍 Scanning for subprocess and bare except issues...")
        
        subprocess_count = 0
        except_count = 0
        
        for py_file in self.project_root.rglob('*.py'):
            if any(part in str(py_file) for part in ['.venv', 'node_modules', '__pycache__', '.backup']):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # بررسی shell=True
    # SECURITY WARNING: Consider shell=False for better security
                if 'shell=True' in content or 'shell = True' in content:
                    logger.info(f"\n🔧 {py_file.relative_to(self.project_root)}")
                    if self.fix_shell_true(py_file):
                        subprocess_count += 1
                
                # بررسی bare except
                if re.search(r'\bexcept\s*:', content):
                    if self.fix_bare_except(py_file):
                        except_count += 1
                        
            except Exception as e:
                logger.warning(f"Cannot process {py_file}: {e}")
        
        return {
            'subprocess_fixed': subprocess_count,
            'except_fixed': except_count
        }


def main():
    logger.info("🔒 Starting subprocess and bare except fix")
    
    project_root = Path(__file__).parent.parent.parent
    fixer = SubprocessFixer(project_root)
    
    results = fixer.fix_all()
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 RESULTS")
    logger.info("=" * 60)
    # SECURITY WARNING: Consider shell=False for better security
    logger.info(f"✅ subprocess shell=True fixed: {results['subprocess_fixed']}")
    logger.info(f"✅ bare except fixed: {results['except_fixed']}")
    logger.info("🎉 Security fixes completed!")


if __name__ == '__main__':
    main()
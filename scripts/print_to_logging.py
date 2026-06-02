#!/usr/bin/env python3
"""
تبدیل خودکار print statements به logging
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


logger = UnifiedLogger.get_logger('print_to_logging')


class PrintToLogger:
    """تبدیل‌کننده print به logging"""
    
    # الگوهای تشخیص سطح لاگ از محتوا
    LEVEL_PATTERNS = {
        'error': [r'error', r'fail', r'exception', r'❌', r'خطا'],
        'warning': [r'warning', r'warn', r'⚠️', r'هشدار'],
        'info': [r'success', r'complete', r'start', r'✅', r'شروع'],
        'debug': [r'debug', r'trace', r'🔍']
    }
    
    def detect_level(self, message: str) -> str:
        """تشخیص سطح لاگ از محتوا"""
        message_lower = message.lower()
        
        for level, patterns in self.LEVEL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return level
        
        return 'info'
    
    def convert_file(self, file_path: Path) -> Dict:
        """تبدیل یک فایل"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original = content
            
            # شمارنده تغییرات
            changes = {'error': 0, 'warning': 0, 'info': 0, 'debug': 0}
            
            # پیدا کردن همه print statements
            lines = content.split('\n')
            new_lines = []
            added_import = False
            
            for i, line in enumerate(lines):
                # شناسایی print statement
                match = re.match(
                    r'^(\s*)print\s*\(\s*(.+?)\s*\)(\s*)$',
                    line
                )
                
                if match:
                    indent = match.group(1)
                    message = match.group(2)
                    
                    # تشخیص سطح
                    level = self.detect_level(message)
                    changes[level] += 1
                    
                    # تولید خط جدید
                    new_line = f"{indent}logger.{level}({message})"
                    new_lines.append(new_line)
                    
                    # اضافه کردن import در اولین جایگزینی
                    if not added_import:
                        # پیدا کردن محل مناسب برای import
                        import_idx = 0
                        for j, prev_line in enumerate(new_lines[:-1]):
                            if prev_line.startswith('import') or prev_line.startswith('from'):
                                import_idx = j + 1
                        
                        new_lines.insert(
                            import_idx,
                            'from scripts.core.logger import UnifiedLogger'
                        )
                        new_lines.insert(
                            import_idx + 1,
                            "logger = UnifiedLogger.get_logger(__name__)"
                        )
                        new_lines.insert(import_idx + 2, '')
                        added_import = True
                else:
                    new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                file_path.write_text(content, encoding='utf-8')
                logger.info(f"  ✅ Converted {file_path.name}: {sum(changes.values())} print → logging")
                return {
                    'file': str(file_path),
                    'changes': changes,
                    'success': True
                }
            
            return {'file': str(file_path), 'changes': changes, 'success': False}
            
        except Exception as e:
            logger.error(f"  ❌ Error converting {file_path}: {e}")
            return {'file': str(file_path), 'error': str(e), 'success': False}
    
    def convert_all(self) -> Dict:
        """تبدیل همه فایل‌ها"""
        logger.info("🔍 Scanning for print statements...")
        
        results = []
        total_changes = {'error': 0, 'warning': 0, 'info': 0, 'debug': 0}
        
        project_root = Path(__file__).parent.parent.parent
        
        for py_file in project_root.rglob('*.py'):
            if any(part in str(py_file) for part in [
                '.venv', 'node_modules', '__pycache__',
                '.backup', 'scripts/core/logger.py'
            ]):
                continue
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                # شمارش print ها
                print_count = len(re.findall(r'\bprint\s*\(', content))
                
                if print_count > 0:
                    result = self.convert_file(py_file)
                    results.append(result)
                    
                    if result['success']:
                        for level, count in result['changes'].items():
                            total_changes[level] += count
                            
            except Exception as e:
                logger.warning(f"Cannot process {py_file}: {e}")
        
        return {
            'total_files': len(results),
            'successful': sum(1 for r in results if r.get('success')),
            'changes': total_changes,
            'total_conversions': sum(total_changes.values())
        }


def main():
    logger.info("📝 Starting print to logging conversion")
    
    converter = PrintToLogger()
    results = converter.convert_all()
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 CONVERSION REPORT")
    logger.info("=" * 60)
    logger.info(f"Files processed: {results['total_files']}")
    logger.info(f"Files modified: {results['successful']}")
    logger.info(f"Total conversions: {results['total_conversions']}")
    logger.info("\nBreakdown by level:")
    for level, count in results['changes'].items():
        logger.info(f"  - {level.upper()}: {count}")
    
    logger.info("\n🎉 Print statements converted to logging!")


if __name__ == '__main__':
    main()
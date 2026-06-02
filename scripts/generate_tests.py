#!/usr/bin/env python3
"""
تولید خودکار unit tests برای توابع موجود
"""


# === Auto-added: Add project root to sys.path ===
import sys
from pathlib import Path as _Path
_project_root = _Path(__file__).parent.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))
# === End auto-added ===

import sys
import ast
import inspect
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))
from core.logger import UnifiedLogger


logger = UnifiedLogger.get_logger('generate_tests')


class TestGenerator:
    """تولیدکننده خودکار تست"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tests_dir = project_root / 'tests'
        self.tests_dir.mkdir(exist_ok=True)
        (self.tests_dir / '__init__.py').touch()
    
    def extract_functions(self, file_path: Path) -> List[Dict]:
        """استخراج توابع از فایل"""
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            functions = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # نادیده گرفتن private و dunder
                    if node.name.startswith('_'):
                        continue
                    
                    # استخراج آرگومان‌ها
                    args = []
                    for arg in node.args.args:
                        if arg.arg == 'self':
                            continue
                        args.append({
                            'name': arg.arg,
                            'annotation': ast.unparse(arg.annotation) if arg.annotation else 'Any'
                        })
                    
                    # استخراج return type
                    returns = ast.unparse(node.returns) if node.returns else 'Any'
                    
                    functions.append({
                        'name': node.name,
                        'args': args,
                        'returns': returns,
                        'line': node.lineno,
                        'docstring': ast.get_docstring(node)
                    })
            
            return functions
            
        except Exception as e:
            logger.warning(f"Cannot parse {file_path}: {e}")
            return []
    
    def generate_test_code(
        self,
        module_path: str,
        function: Dict
    ) -> str:
        """تولید کد تست برای یک تابع"""
        
        func_name = function['name']
        args = function['args']
        returns = function['returns']
        
        # تولید پارامترهای تست
        test_params = []
        for arg in args:
            arg_type = arg['annotation']
            if arg_type in ['int', 'float']:
                test_params.append(f"{arg['name']}=1")
            elif arg_type == 'str':
                test_params.append(f"{arg['name']}='test'")
            elif arg_type == 'bool':
                test_params.append(f"{arg['name']}=True")
            elif arg_type == 'dict' or 'Dict' in arg_type:
                test_params.append(f"{arg['name']}={{}}")
            elif arg_type == 'list' or 'List' in arg_type:
                test_params.append(f"{arg['name']}=[]")
            else:
                test_params.append(f"{arg['name']}=None")
        
        params_str = ', '.join(test_params)
        
        test_code = f'''
    def test_{func_name}_basic(self):
        """تست پایه برای {func_name}"""
        # Arrange
        # TODO: Setup test data
        
        # Act
        result = {func_name}({params_str})
        
        # Assert
        assert result is not None
    
    def test_{func_name}_invalid_input(self):
        """تست ورودی نامعتبر برای {func_name}"""
        with pytest.raises((ValueError, TypeError)):
            {func_name}()
    
    def test_{func_name}_edge_cases(self):
        """تست حالت‌های خاص برای {func_name}"""
        # TODO: Add edge case tests
        pass
'''
        
        return test_code
    
    def generate_test_file(
        self,
        source_file: Path,
        functions: List[Dict]
    ) -> Optional[Path]:
        """تولید فایل تست کامل"""
        
        if not functions:
            return None
        
        # نام فایل تست
        test_filename = f"test_{source_file.stem}.py"
        test_file = self.tests_dir / test_filename
        
        # محاسبه مسیر import
        relative_path = source_file.relative_to(self.project_root)
        module_path = str(relative_path).replace('/', '.').replace('.py', '')
        
        # تولید محتوای فایل
        content = f'''"""
تست‌های خودکار برای {source_file.name}
تولید شده توسط TestGenerator
"""

import pytest
import sys
from pathlib import Path

# افزودن مسیر پروژه
sys.path.insert(0, str(Path(__file__).parent.parent))

from {module_path} import (
    {", ".join(f["name"] for f in functions)}
)


class Test{source_file.stem.title()}:
    """کلاس تست برای {source_file.name}"""
'''
        
        # اضافه کردن تست‌ها
        for func in functions:
            content += self.generate_test_code(module_path, func)
        
        # اضافه کردن fixtures
        content += f'''

    @pytest.fixture
    def sample_data(self):
        """داده نمونه برای تست‌ها"""
        return {{
            'test_key': 'test_value',
            'number': 42,
            'list': [1, 2, 3]
        }}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
'''
        
        # نوشتن فایل
        test_file.write_text(content, encoding='utf-8')
        logger.info(f"  ✅ Generated: {test_filename} ({len(functions)} tests)")
        
        return test_file
    
    def generate_all(self) -> Dict:
        """تولید تست برای همه فایل‌ها"""
        logger.info("🔍 Scanning for testable functions...")
        
        results = {
            'files_processed': 0,
            'test_files_created': 0,
            'total_tests': 0
        }
        
        # پوشه‌های هدف
        target_dirs = ['apps', 'core', 'scripts/models', 'scripts/api', 'scripts/utils']
        
        for target in target_dirs:
            target_path = self.project_root / target
            if not target_path.exists():
                continue
            
            for py_file in target_path.rglob('*.py'):
                if py_file.name.startswith('test_') or py_file.name == '__init__.py':
                    continue
                
                functions = self.extract_functions(py_file)
                
                if functions:
                    results['files_processed'] += 1
                    test_file = self.generate_test_file(py_file, functions)
                    
                    if test_file:
                        results['test_files_created'] += 1
                        results['total_tests'] += len(functions) * 3  # 3 تست per function
        
        return results


def main():
    logger.info("🧪 Starting automatic test generation")
    
    project_root = Path(__file__).parent.parent.parent
    generator = TestGenerator(project_root)
    
    results = generator.generate_all()
    
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST GENERATION REPORT")
    logger.info("=" * 60)
    logger.info(f"Files processed: {results['files_processed']}")
    logger.info(f"Test files created: {results['test_files_created']}")
    logger.info(f"Total test functions: {results['total_tests']}")
    logger.info("\n🎉 Test generation completed!")
    logger.info(f"\n💡 Run tests with: pytest tests/ -v")


if __name__ == '__main__':
    main()
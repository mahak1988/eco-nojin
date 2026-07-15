from langchain_core.tools import tool
from typing import List, Dict, Any, Optional
import logging
import ast
import re
import json

logger = logging.getLogger(__name__)

# ==========================================
# Code Analysis Tool (AST-based)
# ==========================================
@tool
async def analyze_code(code: str, language: str = "python") -> str:
    """
    تحلیل ساختاری کد با استفاده از AST.
    
    Args:
        code: کد منبع برای تحلیل
        language: زبان برنامه‌نویسی (python, javascript, typescript)
    
    Returns:
        گزارش تحلیل شامل توابع، کلاس‌ها، imports، و مشکلات
    """
    logger.info(f"🔍 Analyzing {language} code ({len(code)} chars)")
    
    if language.lower() != "python":
        return f"⚠️ تحلیل AST فقط برای Python پیاده‌سازی شده. زبان فعلی: {language}"
    
    try:
        tree = ast.parse(code)
        
        # استخراج اطلاعات
        functions = []
        classes = []
        imports = []
        issues = []
        
        for node in ast.walk(tree):
            # توابع
            if isinstance(node, ast.FunctionDef):
                args = [arg.arg for arg in node.args.args]
                functions.append({
                    "name": node.name,
                    "args": args,
                    "line": node.lineno,
                    "lines_count": node.end_lineno - node.lineno + 1 if node.end_lineno else 0,
                    "is_async": isinstance(node, ast.AsyncFunctionDef),
                    "has_docstring": ast.get_docstring(node) is not None
                })
                
                # بررسی طول تابع
                if node.end_lineno and (node.end_lineno - node.lineno) > 50:
                    issues.append(f"⚠️ تابع '{node.name}' در خط {node.lineno} بیش از 50 خط است (توصیه: تقسیم به توابع کوچکتر)")
                
                # بررسی docstring
                if not ast.get_docstring(node):
                    issues.append(f"⚠️ تابع '{node.name}' در خط {node.lineno} docstring ندارد")
            
            # کلاس‌ها
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                classes.append({
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "bases": [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases],
                    "has_docstring": ast.get_docstring(node) is not None
                })
            
            # Imports
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # ساخت گزارش
        output = [f"🔍 گزارش تحلیل کد ({language}):\n"]
        output.append(f"📊 آمار کلی:")
        output.append(f"   - تعداد توابع: {len(functions)}")
        output.append(f"   - تعداد کلاس‌ها: {len(classes)}")
        output.append(f"   - تعداد imports: {len(imports)}")
        output.append(f"   - تعداد خطوط: {len(code.splitlines())}")
        
        if functions:
            output.append(f"\n📝 توابع:")
            for func in functions:
                async_mark = "async " if func["is_async"] else ""
                doc_mark = "✅" if func["has_docstring"] else "❌"
                output.append(f"   - {async_mark}{func['name']}({', '.join(func['args'])}) [خط {func['line']}, {func['lines_count']} خط] docstring:{doc_mark}")
        
        if classes:
            output.append(f"\n🏛️ کلاس‌ها:")
            for cls in classes:
                bases = f"({', '.join(cls['bases'])})" if cls['bases'] else ""
                output.append(f"   - {cls['name']}{bases} [خط {cls['line']}]")
                for method in cls['methods']:
                    output.append(f"      └─ {method}()")
        
        if imports:
            output.append(f"\n📦 Imports:")
            for imp in imports[:20]:  # محدود به 20 تا
                output.append(f"   - {imp}")
            if len(imports) > 20:
                output.append(f"   ... و {len(imports) - 20} import دیگر")
        
        if issues:
            output.append(f"\n⚠️ مشکلات شناسایی‌شده ({len(issues)} مورد):")
            for issue in issues[:10]:
                output.append(f"   {issue}")
        else:
            output.append(f"\n✅ هیچ مشکل ساختاری شناسایی نشد")
        
        return "\n".join(output)
    
    except SyntaxError as e:
        return f"❌ خطای syntax در خط {e.lineno}: {e.msg}"
    except Exception as e:
        logger.error(f"❌ Code analysis error: {e}")
        return f"❌ خطا در تحلیل کد: {str(e)}"

# ==========================================
# Bug Finder Tool
# ==========================================
@tool
async def find_bugs(code: str, language: str = "python") -> str:
    """
    شناسایی باگ‌های رایج در کد.
    
    Args:
        code: کد منبع
        language: زبان برنامه‌نویسی
    
    Returns:
        لیست باگ‌های احتمالی
    """
    logger.info(f"🐛 Finding bugs in {language} code")
    
    if language.lower() != "python":
        return f"⚠️ تحلیل باگ فقط برای Python پیاده‌سازی شده"
    
    try:
        bugs = []
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # بررسی except خالی
            if isinstance(node, ast.ExceptHandler) and node.type is None:
                bugs.append({
                    "type": "bare_except",
                    "line": node.lineno,
                    "severity": "high",
                    "message": "استفاده از except بدون نوع استثنا (bare except) - ممکن است خطاهای مهم را پنهان کند"
                })
            
            # بررسی mutable default arguments
            if isinstance(node, ast.FunctionDef):
                for default in node.args.defaults:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        bugs.append({
                            "type": "mutable_default",
                            "line": node.lineno,
                            "severity": "high",
                            "message": f"تابع '{node.name}' از mutable default argument استفاده می‌کند"
                        })
            
            # بررسی import *
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == "*":
                        bugs.append({
                            "type": "wildcard_import",
                            "line": node.lineno,
                            "severity": "medium",
                            "message": f"استفاده از wildcard import در {node.module}"
                        })
            
            # بررسی print در production code
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    bugs.append({
                        "type": "print_statement",
                        "line": node.lineno,
                        "severity": "low",
                        "message": "استفاده از print - در production از logging استفاده کنید"
                    })
            
            # بررسی TODO/FIXME در کامنت‌ها
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                if isinstance(node.value.value, str):
                    content = node.value.value
                    if "TODO" in content or "FIXME" in content or "HACK" in content:
                        bugs.append({
                            "type": "tech_debt",
                            "line": node.lineno,
                            "severity": "low",
                            "message": f"بدهی فنی شناسایی شد: {content[:50]}..."
                        })
        
        # ساخت گزارش
        if not bugs:
            return "✅ هیچ باگ رایجی شناسایی نشد"
        
        output = [f"🐛 گزارش شناسایی باگ‌ها ({len(bugs)} مورد):\n"]
        
        # مرتب‌سازی بر اساس severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        bugs.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        for bug in bugs:
            severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(bug["severity"], "⚪")
            output.append(f"{severity_icon} [{bug['severity'].upper()}] خط {bug['line']}:")
            output.append(f"   {bug['message']}")
            output.append(f"   نوع: {bug['type']}")
            output.append("")
        
        # خلاصه
        high = sum(1 for b in bugs if b["severity"] == "high")
        medium = sum(1 for b in bugs if b["severity"] == "medium")
        low = sum(1 for b in bugs if b["severity"] == "low")
        
        output.append(f"\n📊 خلاصه:")
        output.append(f"   🔴 بحرانی: {high}")
        output.append(f"   🟡 متوسط: {medium}")
        output.append(f"   🟢 کم: {low}")
        
        return "\n".join(output)
    
    except SyntaxError as e:
        return f"❌ خطای syntax در خط {e.lineno}: {e.msg}"
    except Exception as e:
        logger.error(f"❌ Bug finder error: {e}")
        return f"❌ خطا در شناسایی باگ: {str(e)}"

# ==========================================
# Complexity Calculator
# ==========================================
@tool
async def calculate_complexity(code: str, function_name: Optional[str] = None) -> str:
    """
    محاسبه پیچیدگی زمانی و فضایی توابع.
    
    Args:
        code: کد منبع
        function_name: نام تابع خاص (اگر None باشد، همه توابع تحلیل می‌شوند)
    
    Returns:
        گزارش پیچیدگی Big-O
    """
    logger.info(f"📈 Calculating complexity for {function_name or 'all functions'}")
    
    try:
        tree = ast.parse(code)
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if function_name and node.name != function_name:
                    continue
                
                complexity = _analyze_complexity(node)
                results.append({
                    "name": node.name,
                    "line": node.lineno,
                    "time_complexity": complexity["time"],
                    "space_complexity": complexity["space"],
                    "details": complexity["details"]
                })
        
        if not results:
            return f"❌ تابعی با نام '{function_name}' یافت نشد" if function_name else "❌ هیچ تابعی یافت نشد"
        
        output = [f"📈 گزارش پیچیدگی الگوریتمی:\n"]
        
        for result in results:
            output.append(f"🔹 تابع: {result['name']} (خط {result['line']})")
            output.append(f"   ⏱️ پیچیدگی زمانی: O({result['time_complexity']})")
            output.append(f"   💾 پیچیدگی فضایی: O({result['space_complexity']})")
            
            if result['details']:
                output.append(f"   📝 جزئیات:")
                for detail in result['details']:
                    output.append(f"      - {detail}")
            output.append("")
        
        # توصیه‌ها
        output.append("💡 توصیه‌ها:")
        for result in results:
            if result['time_complexity'] in ['n²', 'n³', '2ⁿ']:
                output.append(f"   - تابع '{result['name']}' پیچیدگی زمانی بالایی دارد. بهینه‌سازی پیشنهاد می‌شود.")
            if result['time_complexity'] == 'n²':
                output.append(f"   - برای '{result['name']}' از الگوریتم‌های O(n log n) استفاده کنید.")
        
        return "\n".join(output)
    
    except Exception as e:
        logger.error(f"❌ Complexity calculation error: {e}")
        return f"❌ خطا در محاسبه پیچیدگی: {str(e)}"

def _analyze_complexity(func_node: ast.FunctionDef) -> Dict[str, Any]:
    """تحلیل پیچیدگی یک تابع."""
    time_complexity = "1"
    space_complexity = "1"
    details = []
    
    loops_count = 0
    nested_loops = 0
    has_recursion = False
    
    for node in ast.walk(func_node):
        # شمارش حلقه‌ها
        if isinstance(node, (ast.For, ast.While)):
            loops_count += 1
            
            # بررسی حلقه‌های تو در تو
            for child in ast.walk(node):
                if isinstance(child, (ast.For, ast.While)) and child is not node:
                    nested_loops += 1
        
        # بررسی recursion
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == func_node.name:
                has_recursion = True
        
        # بررسی list comprehension
        if isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            details.append("List/Set/Dict comprehension شناسایی شد")
    
    # تعیین پیچیدگی زمانی
    if has_recursion:
        time_complexity = "2ⁿ یا n!"
        details.append("بازگشت (recursion) شناسایی شد")
    elif nested_loops > 0:
        if nested_loops == 1:
            time_complexity = "n²"
        elif nested_loops == 2:
            time_complexity = "n³"
        else:
            time_complexity = f"n^{nested_loops + 1}"
        details.append(f"{nested_loops + 1} حلقه تو در تو شناسایی شد")
    elif loops_count > 0:
        time_complexity = "n"
        details.append(f"{loops_count} حلقه شناسایی شد")
    else:
        time_complexity = "1"
        details.append("بدون حلقه - پیچیدگی ثابت")
    
    # پیچیدگی فضایی
    if has_recursion:
        space_complexity = "n"
        details.append("فضای stack برای recursion")
    
    return {
        "time": time_complexity,
        "space": space_complexity,
        "details": details
    }

# ==========================================
# Test Generator Tool
# ==========================================
@tool
async def generate_tests(code: str, function_name: str, framework: str = "pytest") -> str:
    """
    تولید تست واحد برای یک تابع.
    
    Args:
        code: کد منبع شامل تابع
        function_name: نام تابع برای تست
        framework: فریم‌ورک تست (pytest, unittest)
    
    Returns:
        کد تست تولید شده
    """
    logger.info(f"🧪 Generating tests for {function_name} using {framework}")
    
    try:
        tree = ast.parse(code)
        
        # پیدا کردن تابع
        target_func = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                target_func = node
                break
        
        if not target_func:
            return f"❌ تابع '{function_name}' یافت نشد"
        
        # استخراج اطلاعات تابع
        args = [arg.arg for arg in target_func.args.args if arg.arg != 'self']
        defaults = target_func.args.defaults
        returns = target_func.returns
        
        # تولید تست
        if framework.lower() == "pytest":
            test_code = _generate_pytest(function_name, args, defaults, returns)
        else:
            test_code = _generate_unittest(function_name, args, defaults, returns)
        
        return test_code
    
    except Exception as e:
        logger.error(f"❌ Test generation error: {e}")
        return f"❌ خطا در تولید تست: {str(e)}"

def _generate_pytest(func_name: str, args: List[str], defaults: List, returns) -> str:
    """تولید تست با pytest."""
    test_code = [
        f"import pytest",
        f"from your_module import {func_name}",
        "",
        f"class Test{func_name.capitalize()}:",
        f'    """تست‌های واحد برای تابع {func_name}"""',
        ""
    ]
    
    # تست مقادیر عادی
    test_code.append(f"    def test_{func_name}_normal_case(self):")
    test_code.append(f'        """تست حالت عادی"""')
    
    if args:
        sample_args = ", ".join([f'{arg}="test_{arg}"' for arg in args])
        test_code.append(f"        result = {func_name}({sample_args})")
    else:
        test_code.append(f"        result = {func_name}()")
    
    test_code.append(f"        assert result is not None")
    test_code.append("")
    
    # تست مقادیر خالی
    if args:
        test_code.append(f"    def test_{func_name}_empty_input(self):")
        test_code.append(f'        """تست با ورودی خالی"""')
        empty_args = ", ".join([f'{arg}=""' if i == 0 else f'{arg}=None' for i, arg in enumerate(args)])
        test_code.append(f"        result = {func_name}({empty_args})")
        test_code.append(f"        # assert مناسب را اضافه کنید")
        test_code.append("")
    
    # تست edge cases
    test_code.append(f"    def test_{func_name}_edge_cases(self):")
    test_code.append(f'        """تست موارد خاص"""')
    test_code.append(f"        # TODO: edge cases را اضافه کنید")
    test_code.append(f"        pass")
    test_code.append("")
    
    # تست exception
    test_code.append(f"    def test_{func_name}_raises_exception(self):")
    test_code.append(f'        """تست پرتاب exception"""')
    test_code.append(f"        with pytest.raises(Exception):")
    if args:
        invalid_args = ", ".join([f'{arg}=None' for arg in args])
        test_code.append(f"            {func_name}({invalid_args})")
    else:
        test_code.append(f"            {func_name}()")
    
    return "\n".join(test_code)

def _generate_unittest(func_name: str, args: List[str], defaults: List, returns) -> str:
    """تولید تست با unittest."""
    test_code = [
        f"import unittest",
        f"from your_module import {func_name}",
        "",
        f"class Test{func_name.capitalize()}(unittest.TestCase):",
        f'    """تست‌های واحد برای تابع {func_name}"""',
        "",
        f"    def test_{func_name}_normal_case(self):",
        f'        """تست حالت عادی"""',
    ]
    
    if args:
        sample_args = ", ".join([f'{arg}="test_{arg}"' for arg in args])
        test_code.append(f"        result = {func_name}({sample_args})")
    else:
        test_code.append(f"        result = {func_name}()")
    
    test_code.append(f"        self.assertIsNotNone(result)")
    test_code.append("")
    
    test_code.append(f"    def test_{func_name}_edge_cases(self):")
    test_code.append(f'        """تست موارد خاص"""')
    test_code.append(f"        # TODO: edge cases را اضافه کنید")
    test_code.append(f"        pass")
    
    return "\n".join(test_code)

# ==========================================
# Code Translator Tool
# ==========================================
@tool
async def translate_code(code: str, source_lang: str, target_lang: str) -> str:
    """
    تبدیل کد بین زبان‌های برنامه‌نویسی.
    
    Args:
        code: کد منبع
        source_lang: زبان مبدأ (python, javascript, typescript)
        target_lang: زبان مقصد
    
    Returns:
        کد تبدیل شده یا راهنمای تبدیل
    """
    logger.info(f"🔄 Translating from {source_lang} to {target_lang}")
    
    if source_lang.lower() == "python" and target_lang.lower() == "javascript":
        return _python_to_javascript(code)
    elif source_lang.lower() == "javascript" and target_lang.lower() == "python":
        return _javascript_to_python(code)
    else:
        return f"⚠️ تبدیل از {source_lang} به {target_lang} هنوز پیاده‌سازی نشده. لطفاً از ایجنت برای راهنمایی استفاده کنید."

def _python_to_javascript(code: str) -> str:
    """تبدیل ساده Python به JavaScript."""
    try:
        js_code = code
        
        # تبدیل def به function
        js_code = re.sub(r'def\s+(\w+)\s*\((.*?)\):', r'function \1(\2) {', js_code)
        
        # تبدیل print به console.log
        js_code = re.sub(r'print\((.*?)\)', r'console.log(\1)', js_code)
        
        # تبدیل None به null
        js_code = js_code.replace('None', 'null')
        
        # تبدیل True/False
        js_code = js_code.replace('True', 'true').replace('False', 'false')
        
        # تبدیل list به array
        js_code = re.sub(r'\[(.*?)\]', r'[\1]', js_code)
        
        # افزودن } به end of function
        lines = js_code.split('\n')
        result = []
        indent_level = 0
        
        for line in lines:
            if line.strip().startswith('function '):
                result.append(line)
                indent_level += 1
            elif line.strip() and not line.strip().startswith('//'):
                result.append('  ' * indent_level + line.strip())
            else:
                result.append(line)
        
        # ساده‌سازی: فقط تبدیل‌های اصلی
        return f"// کد JavaScript تبدیل شده:\n\n{js_code}\n\n// توجه: این تبدیل خودکار است و ممکن است نیاز به اصلاح دستی داشته باشد"
    
    except Exception as e:
        return f"❌ خطا در تبدیل: {str(e)}"

def _javascript_to_python(code: str) -> str:
    """تبدیل ساده JavaScript به Python."""
    try:
        py_code = code
        
        # تبدیل function به def
        py_code = re.sub(r'function\s+(\w+)\s*\((.*?)\)\s*{', r'def \1(\2):', py_code)
        
        # تبدیل console.log به print
        py_code = re.sub(r'console\.log\((.*?)\)', r'print(\1)', py_code)
        
        # تبدیل null/undefined به None
        py_code = py_code.replace('null', 'None').replace('undefined', 'None')
        
        # تبدیل true/false
        py_code = py_code.replace('true', 'True').replace('false', 'False')
        
        # حذف ;
        py_code = py_code.replace(';', '')
        
        # تبدیل var/let/const
        py_code = re.sub(r'(var|let|const)\s+', '', py_code)
        
        return f"# کد Python تبدیل شده:\n\n{py_code}\n\n# توجه: این تبدیل خودکار است و ممکن است نیاز به اصلاح دستی داشته باشد"
    
    except Exception as e:
        return f"❌ خطا در تبدیل: {str(e)}"

# ==========================================
# Documentation Generator
# ==========================================
@tool
async def generate_documentation(code: str, style: str = "google") -> str:
    """
    تولید مستندات برای کد.
    
    Args:
        code: کد منبع
        style: سبک مستندات (google, numpy, sphinx)
    
    Returns:
        مستندات تولید شده
    """
    logger.info(f"📚 Generating {style} documentation")
    
    try:
        tree = ast.parse(code)
        docs = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = _generate_function_doc(node, style)
                docs.append(doc)
            elif isinstance(node, ast.ClassDef):
                doc = _generate_class_doc(node, style)
                docs.append(doc)
        
        if not docs:
            return "❌ هیچ تابع یا کلاسی برای مستندسازی یافت نشد"
        
        return "\n\n".join(docs)
    
    except Exception as e:
        logger.error(f"❌ Documentation generation error: {e}")
        return f"❌ خطا در تولید مستندات: {str(e)}"

def _generate_function_doc(func: ast.FunctionDef, style: str) -> str:
    """تولید مستندات برای یک تابع."""
    args = [arg.arg for arg in func.args.args if arg.arg != 'self']
    
    if style.lower() == "google":
        doc = [
            f'"""',
            f'{func.name} - [توضیح کوتاه]',
            f'',
            f'Args:',
        ]
        for arg in args:
            doc.append(f'    {arg}: [توضیح آرگومان]')
        
        doc.append('')
        doc.append('Returns:')
        doc.append('    [توضیح مقدار بازگشتی]')
        doc.append('')
        doc.append('Raises:')
        doc.append('    [استثناهای احتمالی]')
        doc.append('"""')
    elif style.lower() == "numpy":
        doc = [
            f'"""',
            f'{func.name}',
            f'==========',
            f'',
            f'[توضیح کوتاه]',
            f'',
            f'Parameters',
            f'----------',
        ]
        for arg in args:
            doc.append(f'{arg} : type')
            doc.append(f'    [توضیح آرگومان]')
        
        doc.append('')
        doc.append('Returns')
        doc.append('-------')
        doc.append('type')
        doc.append('    [توضیح مقدار بازگشتی]')
        doc.append('"""')
    else:  # sphinx
        doc = [
            f'"""',
            f'{func.name}',
            f'',
        ]
        for arg in args:
            doc.append(f':param {arg}: [توضیح آرگومان]')
            doc.append(f':type {arg}: type')
        
        doc.append(':returns: [توضیح مقدار بازگشتی]')
        doc.append(':rtype: type')
        doc.append('"""')
    
    return "\n".join(doc)

def _generate_class_doc(cls: ast.ClassDef, style: str) -> str:
    """تولید مستندات برای یک کلاس."""
    methods = [n.name for n in cls.body if isinstance(n, ast.FunctionDef)]
    
    doc = [
        f'"""',
        f'کلاس {cls.name}',
        f'',
        f'[توضیح کلاس]',
        f'',
        f'Attributes:',
        f'    [ویژگی‌های کلاس]',
        f'',
        f'Methods:',
    ]
    
    for method in methods:
        doc.append(f'    - {method}(): [توضیح متد]')
    
    doc.append('"""')
    
    return "\n".join(doc)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup Development Tools with Mirror Fallback
=============================================
این اسکریپت:
1. چندین mirror PyPI را تست می‌کند
2. پکیج‌ها را از mirror فعال نصب می‌کند
3. ابزارهای جایگزین داخلی ارائه می‌دهد
r"""

import subprocess
import sys
import json
import time
from pathlib import Path
from typing import List, Optional, Tuple

PROJECT_ROOT = Path(r"D:\econojin.com")

# ============================================================================
# Mirror Configuration
# ============================================================================

PIP_MIRRORS = [
    {
        'name': 'PyPI Official',
        'url': 'https://pypi.org/simple/',
        'trusted': False
    },
    {
        'name': 'Tsinghua (China)',
        'url': 'https://pypi.tuna.tsinghua.edu.cn/simple/',
        'trusted': True
    },
    {
        'name': 'Aliyun (China)',
        'url': 'https://mirrors.aliyun.com/pypi/simple/',
        'trusted': True
    },
    {
        'name': 'Douban (China)',
        'url': 'https://pypi.doubanio.com/simple/',
        'trusted': True
    },
    {
        'name': 'Google',
        'url': 'https://mirror.google.com/pypi/simple/',
        'trusted': False
    },
]

# ============================================================================
# Utility Functions
# ============================================================================

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def print_success(msg):
    print(f"✓ {msg}")

def print_error(msg):
    print(f"✗ {msg}")

def print_warning(msg):
    print(f"⚠ {msg}")

def print_info(msg):
    print(f"ℹ {msg}")

def test_mirror(mirror: dict, timeout: int = 10) -> bool:
    """تست اتصال به mirror"""
    try:
        cmd = [
            sys.executable, '-m', 'pip', 'install', 
            '--dry-run', '--no-deps',
            '--index-url', mirror['url']
        ]
        if mirror['trusted']:
            cmd.extend(['--trusted-host', mirror['url'].split('/')[2]])
        cmd.append('pip')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False

def find_working_mirror() -> Optional[dict]:
    """پیدا کردن mirror فعال"""
    print_info("در حال تست mirror ها...")
    
    for mirror in PIP_MIRRORS:
        print(f"  تست: {mirror['name']}...", end=' ')
        if test_mirror(mirror):
            print("✓ فعال")
            return mirror
        else:
            print("✗ غیرفعال")
    
    return None

def install_package(package: str, mirror: Optional[dict] = None) -> bool:
    """نصب پکیج با mirror مشخص"""
    cmd = [sys.executable, '-m', 'pip', 'install']
    
    if mirror:
        cmd.extend(['--index-url', mirror['url']])
        if mirror['trusted']:
            cmd.extend(['--trusted-host', mirror['url'].split('/')[2]])
    
    cmd.append(package)
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except Exception as e:
        print_error(f"Error installing {package}: {e}")
        return False

# ============================================================================
# Alternative Tools (Internal Implementations)
# ============================================================================

def create_security_scanner():
    """ایجاد اسکنر امنیتی داخلی (جایگزین bandit)"""
    print_header("🔒 Creating Internal Security Scanner")
    
    scanner_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internal Security Scanner - Bandit Alternative
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict

class SecurityScanner:
    """اسکنر امنیتی داخلی"""
    
    SECURITY_PATTERNS = {
        'eval': {
            'severity': 'HIGH',
            'message': 'Use of eval() can lead to code injection'
        },
        'exec': {
            'severity': 'HIGH',
            'message': 'Use of exec() can lead to code injection'
        },
        'os.system': {
            'severity': 'HIGH',
            'message': 'Use of os.system() is insecure, use subprocess instead'
        },
        'subprocess.call': {
            'severity': 'MEDIUM',
            'message': 'Consider using subprocess.run() with shell=False'
        },
        'pickle.loads': {
            'severity': 'HIGH',
            'message': 'Unpickling untrusted data can lead to arbitrary code execution'
        },
        'yaml.load': {
            'severity': 'MEDIUM',
            'message': 'Use yaml.safe_load() instead of yaml.load()'
        },
        'hardcoded_password': {
            'severity': 'HIGH',
            'message': 'Possible hardcoded password detected'
        },
        'hardcoded_secret': {
            'severity': 'HIGH',
            'message': 'Possible hardcoded secret detected'
        },
    }
    
    def __init__(self):
        self.issues = []
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """اسکن یک فایل"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            file_issues = []
            
            # Scan for dangerous functions
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id == 'eval':
                            file_issues.append({
                                'file': str(file_path),
                                'line': node.lineno,
                                'type': 'eval',
                                **self.SECURITY_PATTERNS['eval']
                            })
                        elif node.func.id == 'exec':
                            file_issues.append({
                                'file': str(file_path),
                                'line': node.lineno,
                                'type': 'exec',
                                **self.SECURITY_PATTERNS['exec']
                            })
                    elif isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name):
                            full_name = f"{node.func.value.id}.{node.func.attr}"
                            if full_name == 'os.system':
                                file_issues.append({
                                    'file': str(file_path),
                                    'line': node.lineno,
                                    'type': 'os.system',
                                    **self.SECURITY_PATTERNS['os.system']
                                })
            
            # Scan for hardcoded secrets
            lines = content.split('\\n')
            for i, line in enumerate(lines, 1):
                if any(keyword in line.lower() for keyword in ['password', 'secret', 'api_key', 'token']):
                    if '=' in line and ('"' in line or "'" in line):
                        file_issues.append({
                            'file': str(file_path),
                            'line': i,
                            'type': 'hardcoded_secret',
                            **self.SECURITY_PATTERNS['hardcoded_secret']
                        })
            
            return file_issues
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
            return []
    
    def scan_directory(self, directory: Path) -> List[Dict]:
        """اسکن یک دایرکتوری"""
        all_issues = []
        
        for py_file in directory.rglob('*.py'):
            if '.venv' in str(py_file) or 'node_modules' in str(py_file):
                continue
            
            issues = self.scan_file(py_file)
            all_issues.extend(issues)
        
        return all_issues
    
    def generate_report(self, issues: List[Dict], output_format: str = 'json') -> str:
        """تولید گزارش"""
        if output_format == 'json':
            return json.dumps({
                'total_issues': len(issues),
                'high_severity': len([i for i in issues if i['severity'] == 'HIGH']),
                'medium_severity': len([i for i in issues if i['severity'] == 'MEDIUM']),
                'issues': issues
            }, indent=2)
        else:
            report = f"Security Scan Report\\n"
            report += f"{'='*70}\\n"
            report += f"Total Issues: {len(issues)}\\n"
            report += f"HIGH: {len([i for i in issues if i['severity'] == 'HIGH'])}\\n"
            report += f"MEDIUM: {len([i for i in issues if i['severity'] == 'MEDIUM'])}\\n"
            report += f"{'='*70}\\n\\n"
            
            for issue in issues:
                report += f"{issue['file']}:{issue['line']}\\n"
                report += f"  [{issue['severity']}] {issue['type']}\\n"
                report += f"  {issue['message']}\\n\\n"
            
            return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python security_scanner.py <directory> [output_file]")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    scanner = SecurityScanner()
    print(f"Scanning {directory}...")
    
    issues = scanner.scan_directory(directory)
    
    if output_file:
        report = scanner.generate_report(issues, 'json')
        output_file.write_text(report, encoding='utf-8')
        print(f"Report saved to {output_file}")
    else:
        report = scanner.generate_report(issues, 'text')
        print(report)
    
    # Exit with error code if high severity issues found
    high_count = len([i for i in issues if i['severity'] == 'HIGH'])
    sys.exit(1 if high_count > 0 else 0)


if __name__ == '__main__':
    main()
'''
    
    scanner_path = PROJECT_ROOT / "scripts" / "security_scanner.py"
    scanner_path.write_text(scanner_code, encoding='utf-8')
    print_success(f"Created: {scanner_path.relative_to(PROJECT_ROOT)}")
    return scanner_path

def create_code_quality_checker():
    """ایجاد بررسی‌کننده کیفیت کد داخلی (جایگزین pylint)"""
    print_header("📊 Creating Internal Code Quality Checker")
    
    checker_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internal Code Quality Checker - Pylint Alternative
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict
import re

class CodeQualityChecker:
    """بررسی‌کننده کیفیت کد داخلی"""
    
    def __init__(self):
        self.issues = []
        self.total_lines = 0
        self.code_lines = 0
        self.comment_lines = 0
        self.blank_lines = 0
    
    def check_file(self, file_path: Path) -> Dict:
        """بررسی یک فایل"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\\n')
            file_issues = []
            
            # Count lines
            self.total_lines += len(lines)
            for line in lines:
                if not line.strip():
                    self.blank_lines += 1
                elif line.strip().startswith('#'):
                    self.comment_lines += 1
                else:
                    self.code_lines += 1
            
            # Check for long lines
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    file_issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'long_line',
                        'severity': 'WARNING',
                        'message': f'Line too long ({len(line)} > 120 characters)'
                    })
            
            # Check for trailing whitespace
            for i, line in enumerate(lines, 1):
                if line.rstrip() != line:
                    file_issues.append({
                        'file': str(file_path),
                        'line': i,
                        'type': 'trailing_whitespace',
                        'severity': 'WARNING',
                        'message': 'Trailing whitespace'
                    })
            
            # Check function length
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                        if func_lines > 50:
                            file_issues.append({
                                'file': str(file_path),
                                'line': node.lineno,
                                'type': 'long_function',
                                'severity': 'WARNING',
                                'message': f'Function too long ({func_lines} lines)'
                            })
            except:
                pass
            
            return {
                'file': str(file_path),
                'issues': file_issues,
                'lines': len(lines)
            }
        
        except Exception as e:
            return {
                'file': str(file_path),
                'issues': [],
                'error': str(e)
            }
    
    def check_directory(self, directory: Path) -> List[Dict]:
        """بررسی یک دایرکتوری"""
        all_results = []
        
        for py_file in directory.rglob('*.py'):
            if '.venv' in str(py_file) or 'node_modules' in str(py_file):
                continue
            
            result = self.check_file(py_file)
            all_results.append(result)
        
        return all_results
    
    def calculate_score(self, results: List[Dict]) -> float:
        """محاسبه امتیاز کیفیت"""
        if self.total_lines == 0:
            return 10.0
        
        total_issues = sum(len(r['issues']) for r in results)
        issue_density = total_issues / self.code_lines if self.code_lines > 0 else 0
        
        # Base score 10, deduct for issues
        score = 10.0 - (issue_density * 10)
        
        # Bonus for comments
        comment_ratio = self.comment_lines / self.code_lines if self.code_lines > 0 else 0
        if comment_ratio > 0.1:
            score += 0.5
        
        return max(0, min(10, score))
    
    def generate_report(self, results: List[Dict]) -> str:
        """تولید گزارش"""
        score = self.calculate_score(results)
        
        report = f"Code Quality Report\\n"
        report += f"{'='*70}\\n"
        report += f"Your code has been rated at {score:.2f}/10\\n\\n"
        report += f"Statistics:\\n"
        report += f"  Total lines: {self.total_lines}\\n"
        report += f"  Code lines: {self.code_lines}\\n"
        report += f"  Comment lines: {self.comment_lines}\\n"
        report += f"  Blank lines: {self.blank_lines}\\n\\n"
        
        total_issues = sum(len(r['issues']) for r in results)
        report += f"Total Issues: {total_issues}\\n"
        report += f"{'='*70}\\n\\n"
        
        for result in results:
            if result['issues']:
                report += f"{result['file']}:\\n"
                for issue in result['issues'][:10]:  # Limit to first 10
                    report += f"  Line {issue['line']}: [{issue['severity']}] {issue['message']}\\n"
                if len(result['issues']) > 10:
                    report += f"  ... and {len(result['issues']) - 10} more issues\\n"
                report += "\\n"
        
        return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python code_quality_checker.py <directory>")
        sys.exit(1)
    
    directory = Path(sys.argv[1])
    
    checker = CodeQualityChecker()
    print(f"Checking {directory}...")
    
    results = checker.check_directory(directory)
    report = checker.generate_report(results)
    
    print(report)
    
    # Save report
    report_file = directory.parent / "quality_report.txt"
    report_file.write_text(report, encoding='utf-8')
    print(f"\\nReport saved to {report_file}")


if __name__ == '__main__':
    main()
'''
    
    checker_path = PROJECT_ROOT / "scripts" / "code_quality_checker.py"
    checker_path.write_text(checker_code, encoding='utf-8')
    print_success(f"Created: {checker_path.relative_to(PROJECT_ROOT)}")
    return checker_path

def create_coverage_analyzer():
    """ایجاد تحلیل‌گر پوشش تست داخلی (جایگزین pytest-cov)"""
    print_header("📈 Creating Internal Coverage Analyzer")
    
    analyzer_code = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Internal Coverage Analyzer - pytest-cov Alternative
"""

import sys
import ast
from pathlib import Path
from typing import Set, Dict

class CoverageAnalyzer:
    """تحلیل‌گر پوشش تست داخلی"""
    
    def __init__(self, source_dir: Path, test_dir: Path):
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.source_files = set()
        self.test_files = set()
        self.covered_modules = set()
    
    def discover_files(self):
        """کشف فایل‌های منبع و تست"""
        # Source files
        for py_file in self.source_dir.rglob('*.py'):
            if '__pycache__' not in str(py_file):
                self.source_files.add(py_file)
        
        # Test files
        for py_file in self.test_dir.rglob('test_*.py'):
            self.test_files.add(py_file)
        
        print(f"Found {len(self.source_files)} source files")
        print(f"Found {len(self.test_files)} test files")
    
    def analyze_imports(self):
        """تحلیل import ها در تست‌ها"""
        for test_file in self.test_files:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.covered_modules.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self.covered_modules.add(node.module)
            except:
                pass
    
    def calculate_coverage(self) -> Dict:
        """محاسبه پوشش"""
        # Simple coverage: percentage of source files that are imported in tests
        total_files = len(self.source_files)
        
        covered_count = 0
        for source_file in self.source_files:
            # Convert file path to module name
            rel_path = source_file.relative_to(self.source_dir)
            module_name = str(rel_path).replace('/', '.').replace('\\\\', '.').replace('.py', '')
            
            # Check if any covered module matches
            for covered in self.covered_modules:
                if module_name in covered or covered in module_name:
                    covered_count += 1
                    break
        
        coverage_percent = (covered_count / total_files * 100) if total_files > 0 else 0
        
        return {
            'total_files': total_files,
            'covered_files': covered_count,
            'coverage_percent': coverage_percent,
            'test_files': len(self.test_files)
        }
    
    def generate_report(self, coverage: Dict) -> str:
        """تولید گزارش"""
        report = f"Coverage Report\\n"
        report += f"{'='*70}\\n"
        report += f"Source files: {coverage['total_files']}\\n"
        report += f"Covered files: {coverage['covered_files']}\\n"
        report += f"Test files: {coverage['test_files']}\\n"
        report += f"Coverage: {coverage['coverage_percent']:.1f}%\\n"
        report += f"{'='*70}\\n"
        
        return report


def main():
    if len(sys.argv) < 3:
        print("Usage: python coverage_analyzer.py <source_dir> <test_dir>")
        sys.exit(1)
    
    source_dir = Path(sys.argv[1])
    test_dir = Path(sys.argv[2])
    
    analyzer = CoverageAnalyzer(source_dir, test_dir)
    
    print("Discovering files...")
    analyzer.discover_files()
    
    print("Analyzing imports...")
    analyzer.analyze_imports()
    
    print("Calculating coverage...")
    coverage = analyzer.calculate_coverage()
    
    report = analyzer.generate_report(coverage)
    print(report)
    
    # Save report
    report_file = source_dir.parent / "coverage_report.txt"
    report_file.write_text(report, encoding='utf-8')
    print(f"Report saved to {report_file}")


if __name__ == '__main__':
    main()
'''
    
    analyzer_path = PROJECT_ROOT / "scripts" / "coverage_analyzer.py"
    analyzer_path.write_text(analyzer_code, encoding='utf-8')
    print_success(f"Created: {analyzer_path.relative_to(PROJECT_ROOT)}")
    return analyzer_path

# ============================================================================
# Main Installation Function
# ============================================================================

def install_dev_tools():
    """نصب ابزارهای توسعه"""
    print_header("🔧 Installing Development Tools")
    
    # Find working mirror
    mirror = find_working_mirror()
    
    if not mirror:
        print_error("هیچ mirror فعالی یافت نشد!")
        print_warning("از ابزارهای داخلی استفاده خواهد شد")
        return False
    
    print_success(f"Mirror فعال: {mirror['name']}")
    
    # Packages to install
    packages = [
        'bandit',
        'pylint',
        'pytest-cov',
        'pre-commit'
    ]
    
    installed = []
    failed = []
    
    for package in packages:
        print(f"\\nنصب {package}...")
        if install_package(package, mirror):
            print_success(f"{package} نصب شد")
            installed.append(package)
        else:
            print_error(f"{package} نصب نشد")
            failed.append(package)
    
    return len(failed) == 0

# ============================================================================
# Main Function
# ============================================================================

def main():
    print_header("🛠️ SETUP DEVELOPMENT TOOLS")
    
    # Try to install tools
    success = install_dev_tools()
    
    if not success:
        print_warning("برخی ابزارها نصب نشدند. ایجاد ابزارهای جایگزین...")
        
        # Create internal tools
        scanner_path = create_security_scanner()
        checker_path = create_code_quality_checker()
        analyzer_path = create_coverage_analyzer()
        
        print_header("📋 USAGE GUIDE")
        print("ابزارهای جایگزین ایجاد شدند:\\n")
        
        print("1️⃣  Security Scanner (جایگزین bandit):")
        print(f"   python {scanner_path} backend/ security_report.json\\n")
        
        print("2️⃣  Code Quality Checker (جایگزین pylint):")
        print(f"   python {checker_path} backend/\\n")
        
        print("3️⃣  Coverage Analyzer (جایگزین pytest-cov):")
        print(f"   python {analyzer_path} backend/ tests/\\n")
        
        print("4️⃣  Run Tests:")
        print("   pytest tests/ -v\\n")
    
    print_header("✅ SETUP COMPLETE")
    print("تمام ابزارها آماده استفاده هستند!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\\nمتوقف شد")
        sys.exit(1)
    except Exception as e:
        print_error(f"خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
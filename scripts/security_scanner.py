import json
#!/usr/bin/env python3
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
            lines = content.split('\n')
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
            report = f"Security Scan Report\n"
            report += f"{'='*70}\n"
            report += f"Total Issues: {len(issues)}\n"
            report += f"HIGH: {len([i for i in issues if i['severity'] == 'HIGH'])}\n"
            report += f"MEDIUM: {len([i for i in issues if i['severity'] == 'MEDIUM'])}\n"
            report += f"{'='*70}\n\n"
            
            for issue in issues:
                report += f"{issue['file']}:{issue['line']}\n"
                report += f"  [{issue['severity']}] {issue['type']}\n"
                report += f"  {issue['message']}\n\n"
            
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

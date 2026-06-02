#!/usr/bin/env python3
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
            
            lines = content.split('\n')
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
        
        report = f"Code Quality Report\n"
        report += f"{'='*70}\n"
        report += f"Your code has been rated at {score:.2f}/10\n\n"
        report += f"Statistics:\n"
        report += f"  Total lines: {self.total_lines}\n"
        report += f"  Code lines: {self.code_lines}\n"
        report += f"  Comment lines: {self.comment_lines}\n"
        report += f"  Blank lines: {self.blank_lines}\n\n"
        
        total_issues = sum(len(r['issues']) for r in results)
        report += f"Total Issues: {total_issues}\n"
        report += f"{'='*70}\n\n"
        
        for result in results:
            if result['issues']:
                report += f"{result['file']}:\n"
                for issue in result['issues'][:10]:  # Limit to first 10
                    report += f"  Line {issue['line']}: [{issue['severity']}] {issue['message']}\n"
                if len(result['issues']) > 10:
                    report += f"  ... and {len(result['issues']) - 10} more issues\n"
                report += "\n"
        
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
    print(f"\nReport saved to {report_file}")


if __name__ == '__main__':
    main()

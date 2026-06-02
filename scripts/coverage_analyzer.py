#!/usr/bin/env python3
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
            module_name = str(rel_path).replace('/', '.').replace('\\', '.').replace('.py', '')
            
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
        report = f"Coverage Report\n"
        report += f"{'='*70}\n"
        report += f"Source files: {coverage['total_files']}\n"
        report += f"Covered files: {coverage['covered_files']}\n"
        report += f"Test files: {coverage['test_files']}\n"
        report += f"Coverage: {coverage['coverage_percent']:.1f}%\n"
        report += f"{'='*70}\n"
        
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

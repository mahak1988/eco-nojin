#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apps_analyzer_v1.1.py
تحلیلگر جامع مسیر apps/ - نسخه چندفایلی با خروجی تفکیک‌شده
نسخه: 1.1.0 | تاریخ: 2026-06-22 | وابستگی‌ها: Python 3.8+ (Standard Library)
"""

import argparse
import ast
import json
import logging
import os
import sys
import hashlib
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ── پیکربندی encoding و لاگ ──
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    force=True
)

# ── ساختارهای داده ──
@dataclass
class CodeMetrics:
    file_path: str
    loc_total: int = 0
    loc_code: int = 0
    loc_comments: int = 0
    loc_blank: int = 0
    functions_count: int = 0
    classes_count: int = 0
    imports_count: int = 0
    complexity_hint: int = 0
    has_docstring: bool = False
    has_type_hints: bool = False

@dataclass
class QualityIssue:
    file_path: str
    line_no: Optional[int]
    issue_type: str
    severity: str
    description: str
    suggestion: str

@dataclass
class ModuleDependency:
    source_module: str
    target_module: str
    import_type: str
    symbols: List[str] = field(default_factory=list)


class AppsDirectoryAnalyzer:
    """تحلیلگر اصلی مسیر apps/"""
    
    def __init__(self, apps_root: str, project_root: Optional[str] = None):
        self.apps_root = Path(apps_root).resolve()
        self.project_root = Path(project_root).resolve() if project_root else self.apps_root.parent
        self.metrics: List[CodeMetrics] = []
        self.issues: List[QualityIssue] = []
        self.dependencies: List[ModuleDependency] = []
        self.audit_id = hashlib.sha256(str(self.apps_root).encode()).hexdigest()[:12]
        
    def scan_directory(self) -> List[Path]:
        py_files = []
        for root, dirs, files in os.walk(self.apps_root):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'node_modules'}]
            for f in files:
                if f.endswith('.py') and not f.startswith('.'):
                    py_files.append(Path(root) / f)
        logging.info(f"🔍 تعداد فایل‌های پایتون یافت‌شده: {len(py_files)}")
        return py_files
    
    def analyze_file_metrics(self, file_path: Path) -> CodeMetrics:
        metrics = CodeMetrics(file_path=str(file_path.relative_to(self.project_root)))
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            logging.warning(f"⚠️ خطا در خواندن {file_path}: {e}")
            return metrics
            
        metrics.loc_total = len(lines)
        metrics.loc_blank = sum(1 for l in lines if not l.strip())
        metrics.loc_comments = sum(1 for l in lines if l.strip().startswith('#'))
        metrics.loc_code = metrics.loc_total - metrics.loc_blank - metrics.loc_comments
        
        try:
            tree = ast.parse(content)
            metrics.functions_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
            metrics.classes_count = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
            metrics.imports_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom)))
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                    metrics.complexity_hint += 1
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
                if isinstance(tree.body[0].value.value, str):
                    metrics.has_docstring = True
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and (node.returns or any(a.annotation for a in node.args.args if a.annotation)):
                    metrics.has_type_hints = True
                    break
        except SyntaxError:
            logging.warning(f"⚠️ خطای سینتکس در {file_path}")
        return metrics
    
    def detect_quality_issues(self, file_path: Path, content: str) -> List[QualityIssue]:
        issues = []
        lines = content.splitlines()
        rel_path = str(file_path.relative_to(self.project_root))
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if 'password' in stripped.lower() and '=' in stripped and 'os.environ' not in stripped and 'os.getenv' not in stripped:
                issues.append(QualityIssue(rel_path, i, "security", "high",
                    "احتمال هاردکد کردن رمز عبور", "استفاده از متغیرهای محیطی یا secrets manager"))
            if 'SECRET_KEY' in stripped and '=' in stripped and 'os.getenv' not in stripped:
                issues.append(QualityIssue(rel_path, i, "security", "critical",
                    "هاردکد کردن SECRET_KEY", "مقدار را از environment variable بارگذاری کنید"))
            if 'eval(' in stripped or 'exec(' in stripped:
                issues.append(QualityIssue(rel_path, i, "security", "critical",
                    "استفاده از eval/exec خطرناک", "جایگزینی با ast.literal_eval یا روش‌های ایمن‌تر"))
            if stripped.startswith('# TODO') or '# FIXME' in stripped or '# HACK' in stripped:
                issues.append(QualityIssue(rel_path, i, "maintainability", "low",
                    f"کامنت {stripped.split()[0]} یافت شد", "بررسی و رفع یا مستندسازی در issue tracker"))
            if len(stripped) > 120 and not stripped.startswith('#'):
                issues.append(QualityIssue(rel_path, i, "style", "info",
                    "خط بیش از ۱۲۰ کاراکتر", "شکستن خط برای بهبود خوانایی (PEP 8)"))
        return issues
    
    def extract_dependencies(self, file_path: Path) -> List[ModuleDependency]:
        deps = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
        except:
            return deps
        source_module = self._path_to_module(file_path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    deps.append(ModuleDependency(source_module, alias.name.split('.')[0], "absolute", [alias.asname or alias.name]))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    import_type = "relative" if node.level > 0 else "absolute"
                    symbols = [a.asname or a.name for a in node.names]
                    deps.append(ModuleDependency(source_module, node.module.split('.')[0] if node.module else "", import_type, symbols))
        return deps
    
    def _path_to_module(self, path: Path) -> str:
        rel = path.relative_to(self.project_root)
        parts = list(rel.parts)
        if parts[-1] == '__init__.py':
            parts = parts[:-1]
        elif parts[-1].endswith('.py'):
            parts[-1] = parts[-1][:-3]
        return '.'.join(p for p in parts if p != '__init__')
    
    def run_full_analysis(self) -> Dict[str, Any]:
        logging.info(f"🚀 شروع تحلیل مسیر: {self.apps_root}")
        py_files = self.scan_directory()
        for file_path in py_files:
            self.metrics.append(self.analyze_file_metrics(file_path))
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.issues.extend(self.detect_quality_issues(file_path, content))
            except:
                pass
            self.dependencies.extend(self.extract_dependencies(file_path))
        
        summary = self._generate_summary()
        recommendations = self._generate_recommendations()
        
        # ساختار داده‌ها برای خروجی چندفایلی
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        return {
            "index": {
                "audit_id": self.audit_id,
                "timestamp": timestamp,
                "analysis_target": str(self.apps_root.relative_to(self.project_root)),
                "files_analyzed": len(self.metrics),
                "total_issues": len(self.issues),
                "total_dependencies": len(self.dependencies),
                "output_files": [
                    {"name": "summary.json", "description": "خلاصه آماری و پیشنهادات"},
                    {"name": "metrics.json", "description": "متریک‌های کمی تک‌تک فایل‌ها"},
                    {"name": "issues.json", "description": "مسائل کیفیت کد"},
                    {"name": "dependencies.json", "description": "گراف وابستگی‌های ماژول‌ها"}
                ]
            },
            "summary": {
                "audit_id": self.audit_id,
                "timestamp": timestamp,
                "analysis_target": str(self.apps_root.relative_to(self.project_root)),
                "statistics": summary,
                "recommendations": recommendations
            },
            "metrics": {
                "audit_id": self.audit_id,
                "timestamp": timestamp,
                "files_count": len(self.metrics),
                "data": [asdict(m) for m in self.metrics]
            },
            "issues": {
                "audit_id": self.audit_id,
                "timestamp": timestamp,
                "issues_count": len(self.issues),
                "data": [asdict(i) for i in self.issues]
            },
            "dependencies": {
                "audit_id": self.audit_id,
                "timestamp": timestamp,
                "dependencies_count": len(self.dependencies),
                "data": [asdict(d) for d in self.dependencies]
            }
        }
    
    def _generate_summary(self) -> Dict[str, Any]:
        total_loc = sum(m.loc_code for m in self.metrics)
        severity_counts = defaultdict(int)
        for issue in self.issues:
            severity_counts[issue.severity] += 1
        issue_type_counts = defaultdict(int)
        for issue in self.issues:
            issue_type_counts[issue.issue_type] += 1
        coupling_scores = defaultdict(int)
        for dep in self.dependencies:
            coupling_scores[dep.source_module] += 1
        high_coupling = [m for m, c in coupling_scores.items() if c > 5]
        return {
            "total_lines_of_code": total_loc,
            "total_functions": sum(m.functions_count for m in self.metrics),
            "total_classes": sum(m.classes_count for m in self.metrics),
            "average_file_size": round(total_loc / max(len(self.metrics), 1), 1),
            "files_with_docstrings": sum(1 for m in self.metrics if m.has_docstring),
            "files_with_type_hints": sum(1 for m in self.metrics if m.has_type_hints),
            "quality_issues_by_severity": dict(severity_counts),
            "quality_issues_by_type": dict(issue_type_counts),
            "high_coupling_modules": high_coupling,
            "total_dependencies": len(self.dependencies)
        }
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        critical_security = [i for i in self.issues if i.severity == "critical" and i.issue_type == "security"]
        if critical_security:
            recs.append({
                "priority": "P0", "category": "Security",
                "recommendation": f"رفع {len(critical_security)} مسئله امنیتی بحرانی قبل از استقرار",
                "affected_files": list(set(i.file_path for i in critical_security))[:10]
            })
        doc_ratio = sum(1 for m in self.metrics if m.has_docstring) / max(len(self.metrics), 1)
        if doc_ratio < 0.5:
            recs.append({
                "priority": "P2", "category": "Maintainability",
                "recommendation": f"افزایش پوشش docstring از {doc_ratio*100:.1f}% به حداقل ۸۰٪",
                "affected_files": [m.file_path for m in self.metrics if not m.has_docstring][:10]
            })
        if len([d for d in self.dependencies if d.import_type == "relative"]) > len(self.dependencies) * 0.7:
            recs.append({
                "priority": "P3", "category": "Architecture",
                "recommendation": "بررسی الگوی وابستگی‌های نسبی؛ احتمال نیاز به بازطراحی مرزهای ماژول",
                "affected_files": []
            })
        if not recs:
            recs.append({
                "priority": "P4", "category": "General",
                "recommendation": "ساختار کد در وضعیت قابل قبول است؛ تمرکز بر تست‌پذیری و مانیتورینگ پیشنهاد می‌شود",
                "affected_files": []
            })
        return recs


def _save_split_output(data: Dict[str, Any], output_dir: str) -> None:
    """ذخیره خروجی به صورت چند فایل مجزا"""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    file_sizes = {}
    for key, filename in [
        ("index", "index.json"),
        ("summary", "summary.json"),
        ("metrics", "metrics.json"),
        ("issues", "issues.json"),
        ("dependencies", "dependencies.json")
    ]:
        filepath = out_path / filename
        content = json.dumps(data[key], indent=2, ensure_ascii=False)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        size_bytes = os.path.getsize(filepath)
        file_sizes[filename] = size_bytes
        logging.info(f"✅ ذخیره شد: {filepath} ({size_bytes:,} bytes)")
    
    # گزارش حجم کل
    total_size = sum(file_sizes.values())
    logging.info(f"📊 حجم کل گزارش: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    logging.info(f"📁 مسیر خروجی: {out_path.resolve()}")


def main():
    parser = argparse.ArgumentParser(description="تحلیلگر جامع مسیر apps/ - نسخه چندفایلی")
    parser.add_argument("apps_path", type=str, nargs="?", default="apps", help="مسیر دایرکتوری apps")
    parser.add_argument("--project-root", type=str, default=".", help="مسیر ریشه پروژه")
    parser.add_argument("--output-dir", type=str, default="apps_analysis_report",
                        help="دایرکتوری خروجی برای فایل‌های تفکیک‌شده")
    parser.add_argument("--single-file", action="store_true",
                        help="خروجی تک‌فایلی (سازگار با نسخه قبل)")
    parser.add_argument("--filter-severity", type=str, choices=["critical", "high", "medium", "low", "info"],
                        help="فیلتر مسائل کیفیت بر اساس سطح اهمیت")
    args = parser.parse_args()

    if not os.path.isdir(args.apps_path):
        logging.error(f"❌ مسیر یافت نشد: {args.apps_path}")
        sys.exit(1)
        
    analyzer = AppsDirectoryAnalyzer(apps_root=args.apps_path, project_root=args.project_root)
    
    try:
        result = analyzer.run_full_analysis()
        
        if args.filter_severity:
            result["issues"]["data"] = [
                i for i in result["issues"]["data"] if i["severity"] == args.filter_severity
            ]
            result["issues"]["issues_count"] = len(result["issues"]["data"])
        
        if args.single_file:
            # حالت تک‌فایلی (سازگار با نسخه قبل)
            combined = {
                "audit_id": result["index"]["audit_id"],
                "analysis_target": result["index"]["analysis_target"],
                "timestamp": result["index"]["timestamp"],
                "summary": result["summary"],
                "files_analyzed": result["index"]["files_analyzed"],
                "metrics": result["metrics"]["data"],
                "quality_issues": result["issues"]["data"],
                "dependencies": result["dependencies"]["data"],
                "recommendations": result["summary"]["recommendations"]
            }
            print(json.dumps(combined, indent=2, ensure_ascii=False))
        else:
            # حالت چندفایلی (پیش‌فرض)
            _save_split_output(result, args.output_dir)
            
    except Exception as e:
        logging.error(f"❌ خطای اجرایی: {type(e).__name__} - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
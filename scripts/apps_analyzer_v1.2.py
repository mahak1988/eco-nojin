#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
apps_analyzer_v1.2.py
تحلیلگر جامع مسیر apps/ - نسخه chunked با کنترل دقیق حجم خروجی
نسخه: 1.2.0 | تاریخ: 2026-06-23 | وابستگی‌ها: Python 3.8+ (Standard Library)
"""

import argparse
import ast
import json
import logging
import os
import sys
import hashlib
import math
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
        
        # مرتب‌سازی مسائل بر اساس شدت (critical اول)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        self.issues.sort(key=lambda x: severity_order.get(x.severity, 5))
        
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        summary = self._generate_summary()
        recommendations = self._generate_recommendations()
        
        return {
            "audit_id": self.audit_id,
            "timestamp": timestamp,
            "analysis_target": str(self.apps_root.relative_to(self.project_root)),
            "summary": {
                "audit_id": self.audit_id,
                "timestamp": timestamp,
                "analysis_target": str(self.apps_root.relative_to(self.project_root)),
                "statistics": summary,
                "recommendations": recommendations
            },
            "metrics_data": [asdict(m) for m in self.metrics],
            "issues_data": [asdict(i) for i in self.issues],
            "dependencies_data": [asdict(d) for d in self.dependencies]
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


def _chunk_list(data: List, chunk_size: int) -> List[List]:
    """تقسیم یک لیست به زیرلیست‌های با اندازه مشخص"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def _save_chunked_output(data: Dict[str, Any], output_dir: str, 
                         metrics_chunk: int, issues_chunk: int, deps_chunk: int) -> None:
    """ذخیره خروجی به صورت فایل‌های chunked با حجم کنترل‌شده"""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = data["timestamp"]
    audit_id = data["audit_id"]
    
    # ۱. ذخیره index.json
    index_data = {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "analysis_target": data["analysis_target"],
        "total_files_analyzed": len(data["metrics_data"]),
        "total_issues": len(data["issues_data"]),
        "total_dependencies": len(data["dependencies_data"]),
        "chunking_config": {
            "metrics_per_file": metrics_chunk,
            "issues_per_file": issues_chunk,
            "dependencies_per_file": deps_chunk
        },
        "output_files": []
    }
    
    # ۲. ذخیره summary.json (همیشه یک فایل)
    summary_path = out_path / "summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(data["summary"], f, indent=2, ensure_ascii=False)
    index_data["output_files"].append({
        "name": "summary.json",
        "type": "summary",
        "part": 1,
        "total_parts": 1,
        "items_count": 1,
        "size_bytes": os.path.getsize(summary_path)
    })
    logging.info(f"✅ summary.json ({os.path.getsize(summary_path):,} bytes)")
    
    # ۳. ذخیره metrics در فایل‌های chunked
    metrics_chunks = _chunk_list(data["metrics_data"], metrics_chunk)
    for i, chunk in enumerate(metrics_chunks):
        filename = f"metrics_part_{i+1:03d}.json"
        filepath = out_path / filename
        chunk_data = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "part": i + 1,
            "total_parts": len(metrics_chunks),
            "items_count": len(chunk),
            "data": chunk
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        index_data["output_files"].append({
            "name": filename,
            "type": "metrics",
            "part": i + 1,
            "total_parts": len(metrics_chunks),
            "items_count": len(chunk),
            "size_bytes": os.path.getsize(filepath)
        })
    logging.info(f"✅ metrics: {len(metrics_chunks)} فایل (هر کدام حداکثر {metrics_chunk} آیتم)")
    
    # ۴. ذخیره issues در فایل‌های chunked
    issues_chunks = _chunk_list(data["issues_data"], issues_chunk)
    for i, chunk in enumerate(issues_chunks):
        filename = f"issues_part_{i+1:03d}.json"
        filepath = out_path / filename
        chunk_data = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "part": i + 1,
            "total_parts": len(issues_chunks),
            "items_count": len(chunk),
            "data": chunk
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        index_data["output_files"].append({
            "name": filename,
            "type": "issues",
            "part": i + 1,
            "total_parts": len(issues_chunks),
            "items_count": len(chunk),
            "size_bytes": os.path.getsize(filepath)
        })
    logging.info(f"✅ issues: {len(issues_chunks)} فایل (هر کدام حداکثر {issues_chunk} آیتم)")
    
    # ۵. ذخیره dependencies در فایل‌های chunked
    deps_chunks = _chunk_list(data["dependencies_data"], deps_chunk)
    for i, chunk in enumerate(deps_chunks):
        filename = f"dependencies_part_{i+1:03d}.json"
        filepath = out_path / filename
        chunk_data = {
            "audit_id": audit_id,
            "timestamp": timestamp,
            "part": i + 1,
            "total_parts": len(deps_chunks),
            "items_count": len(chunk),
            "data": chunk
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=2, ensure_ascii=False)
        index_data["output_files"].append({
            "name": filename,
            "type": "dependencies",
            "part": i + 1,
            "total_parts": len(deps_chunks),
            "items_count": len(chunk),
            "size_bytes": os.path.getsize(filepath)
        })
    logging.info(f"✅ dependencies: {len(deps_chunks)} فایل (هر کدام حداکثر {deps_chunk} آیتم)")
    
    # ۶. ذخیره index.json در انتها (با فهرست کامل فایل‌ها)
    index_path = out_path / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    # گزارش نهایی
    total_size = sum(f["size_bytes"] for f in index_data["output_files"])
    total_files = len(index_data["output_files"])
    logging.info(f"📊 گزارش نهایی:")
    logging.info(f"   📁 مسیر خروجی: {out_path.resolve()}")
    logging.info(f"   📄 تعداد کل فایل‌ها: {total_files}")
    logging.info(f"   💾 حجم کل گزارش: {total_size:,} bytes ({total_size/1024:.1f} KB)")
    logging.info(f"   📋 فایل index.json شامل فهرست کامل فایل‌های تولیدشده است")


def main():
    parser = argparse.ArgumentParser(
        description="تحلیلگر جامع مسیر apps/ - نسخه chunked با کنترل دقیق حجم",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
مثال‌های کاربردی:
  python apps_analyzer_v1.2.py apps
  python apps_analyzer_v1.2.py apps --output-dir .\report\
  python apps_analyzer_v1.2.py apps --metrics-chunk 40 --issues-chunk 60
  python apps_analyzer_v1.2.py apps --only-summary
        """
    )
    parser.add_argument("apps_path", type=str, nargs="?", default="apps", 
                        help="مسیر دایرکتوری apps (پیش‌فرض: apps)")
    parser.add_argument("--project-root", type=str, default=".", 
                        help="مسیر ریشه پروژه")
    parser.add_argument("--output-dir", type=str, default="apps_analysis_report",
                        help="دایرکتوری خروجی")
    
    # پارامترهای کنترل حجم
    parser.add_argument("--metrics-chunk", type=int, default=60,
                        help="تعداد آیتم‌های metrics در هر فایل (پیش‌فرض: 60 ≈ ۱۰۰۰ خط)")
    parser.add_argument("--issues-chunk", type=int, default=90,
                        help="تعداد آیتم‌های issues در هر فایل (پیش‌فرض: 90 ≈ ۱۰۰۰ خط)")
    parser.add_argument("--deps-chunk", type=int, default=110,
                        help="تعداد آیتم‌های dependencies در هر فایل (پیش‌فرض: 110 ≈ ۱۰۰۰ خط)")
    
    # حالت‌های ویژه
    parser.add_argument("--only-summary", action="store_true",
                        help="تولید فقط فایل summary.json (بدون chunked files)")
    parser.add_argument("--top-issues", type=int, default=0,
                        help="محدود کردن مسائل به N مورد اول (بر اساس شدت)")
    
    args = parser.parse_args()

    if not os.path.isdir(args.apps_path):
        logging.error(f"❌ مسیر یافت نشد: {args.apps_path}")
        sys.exit(1)
        
    analyzer = AppsDirectoryAnalyzer(apps_root=args.apps_path, project_root=args.project_root)
    
    try:
        result = analyzer.run_full_analysis()
        
        # محدودسازی مسائل در صورت درخواست
        if args.top_issues > 0:
            result["issues_data"] = result["issues_data"][:args.top_issues]
            logging.info(f"⚠️ مسائل به {args.top_issues} مورد اول محدود شد")
        
        out_path = Path(args.output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        if args.only_summary:
            # حالت فقط خلاصه
            summary_path = out_path / "summary.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(result["summary"], f, indent=2, ensure_ascii=False)
            logging.info(f"✅ فقط summary.json تولید شد ({os.path.getsize(summary_path):,} bytes)")
        else:
            # حالت chunked کامل
            _save_chunked_output(
                result, 
                args.output_dir,
                metrics_chunk=args.metrics_chunk,
                issues_chunk=args.issues_chunk,
                deps_chunk=args.deps_chunk
            )
            
    except Exception as e:
        logging.error(f"❌ خطای اجرایی: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
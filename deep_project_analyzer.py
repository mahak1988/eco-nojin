#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔬 Econojin Deep Project Analyzer v2.0
آنالیزور جامع پروژه از ۸ بُعد مختلف
"""
import ast
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ========== تنظیمات ==========
ROOT = Path(__file__).parent.resolve()
REPORT_DIR = ROOT / "analysis_reports"
REPORT_DIR.mkdir(exist_ok=True)

IGNORE_DIRS = {
    ".git",
    "node_modules",
    ".next",
    ".venv",
    "__pycache__",
    "tutorial_env",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
}
SENSITIVE_PATTERNS = ["password", "secret", "api_key", "token", "private_key"]
SENSITIVE_EXTENSIONS = {".pem", ".key", ".p12", ".pfx", ".env", ".env.local"}

# ========== کلاس‌های آنالیزور ==========


class BaseAnalyzer:
    """کلاس پایه برای همه آنالیزورها"""

    def __init__(self, root: Path):
        self.root = root
        self.findings = []
        self.stats = {}

    def add_finding(
        self, severity: str, category: str, message: str, path: str = "", suggestion: str = ""
    ):
        self.findings.append(
            {
                "severity": severity,  # critical, warning, info, success
                "category": category,
                "message": message,
                "path": path,
                "suggestion": suggestion,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def should_ignore(self, path: Path) -> bool:
        return any(ign in path.parts for ign in IGNORE_DIRS)


class StructureAnalyzer(BaseAnalyzer):
    """آنالیزور ساختار پروژه"""

    name = "📁 Structure Analyzer"

    def analyze(self):
        file_count = 0
        dir_count = 0
        total_size = 0
        ext_counter = Counter()
        large_files = []
        deep_paths = []

        for path in self.root.rglob("*"):
            if self.should_ignore(path):
                continue
            try:
                if path.is_file():
                    file_count += 1
                    size = path.stat().st_size
                    total_size += size
                    ext_counter[path.suffix.lower() or "no_ext"] += 1

                    if size > 500_000:  # > 500KB
                        large_files.append(
                            {
                                "path": str(path.relative_to(self.root)),
                                "size_mb": round(size / 1_048_576, 2),
                            }
                        )
                        self.add_finding(
                            "warning",
                            "size",
                            f"فایل بزرگ: {size/1_048_576:.2f} MB",
                            str(path.relative_to(self.root)),
                            "بررسی و بهینه‌سازی فایل",
                        )

                    depth = len(path.relative_to(self.root).parts)
                    if depth > 8:
                        deep_paths.append(
                            {"path": str(path.relative_to(self.root)), "depth": depth}
                        )
                elif path.is_dir():
                    dir_count += 1
            except:
                continue

        self.stats = {
            "total_files": file_count,
            "total_dirs": dir_count,
            "total_size_mb": round(total_size / 1_048_576, 2),
            "file_types": dict(ext_counter.most_common(15)),
            "large_files_count": len(large_files),
            "deep_paths_count": len(deep_paths),
            "large_files": large_files[:10],
            "deep_paths": deep_paths[:5],
        }

        if file_count > 0:
            self.add_finding(
                "success", "structure", f"پروژه شامل {file_count} فایل در {dir_count} پوشه است"
            )
        if large_files:
            self.add_finding("warning", "size", f"{len(large_files)} فایل بزرگ (>500KB) یافت شد")
        if deep_paths:
            self.add_finding(
                "info",
                "structure",
                f"{len(deep_paths)} مسیر عمیق (>8 سطح) یافت شد",
                suggestion="ساختار پوشه‌ها را ساده‌تر کنید",
            )


class DependencyAnalyzer(BaseAnalyzer):
    """آنالیزور وابستگی‌ها"""

    name = "📦 Dependency Analyzer"

    def analyze(self):
        # بک‌اند
        backend_deps = self._analyze_python_deps()
        # فرانت‌اند
        frontend_deps = self._analyze_node_deps()

        self.stats = {"backend": backend_deps, "frontend": frontend_deps}

        if backend_deps.get("packages"):
            self.add_finding(
                "success", "backend", f"{len(backend_deps['packages'])} پکیج پایتون نصب شده"
            )
        if frontend_deps.get("packages"):
            self.add_finding(
                "success", "frontend", f"{len(frontend_deps['packages'])} پکیج Node.js نصب شده"
            )

    def _analyze_python_deps(self) -> dict:
        result = {"packages": {}, "requirements_files": []}

        # بررسی requirements.txt
        for req_file in self.root.rglob("requirements*.txt"):
            if self.should_ignore(req_file):
                continue
            try:
                content = req_file.read_text(encoding="utf-8")
                packages = [
                    line.strip().split("==")[0].split(">=")[0].split("<")[0].strip()
                    for line in content.split("\n")
                    if line.strip() and not line.startswith("#")
                ]
                result["requirements_files"].append(
                    {"path": str(req_file.relative_to(self.root)), "packages": packages}
                )
                for pkg in packages:
                    if pkg:
                        result["packages"][pkg] = "requirements"
            except:
                pass

        # بررسی pyproject.toml
        pyproject = self.root / "pyproject.toml"
        if pyproject.exists():
            result["has_pyproject"] = True

        return result

    def _analyze_node_deps(self) -> dict:
        result = {"packages": {}, "package_jsons": []}

        for pkg_file in self.root.rglob("package.json"):
            if self.should_ignore(pkg_file) or "node_modules" in pkg_file.parts:
                continue
            try:
                data = json.loads(pkg_file.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                result["package_jsons"].append(
                    {
                        "path": str(pkg_file.relative_to(self.root)),
                        "name": data.get("name", "unknown"),
                        "deps_count": len(deps),
                        "deps": list(deps.keys())[:20],
                    }
                )
                result["packages"].update(deps)
            except:
                pass

        return result


class CodeQualityAnalyzer(BaseAnalyzer):
    """آنالیزور کیفیت کد"""

    name = "✨ Code Quality Analyzer"

    def analyze(self):
        python_stats = self._analyze_python()
        typescript_stats = self._analyze_typescript()

        self.stats = {
            "python": python_stats,
            "typescript": typescript_stats,
            "total_lines": python_stats["total_lines"] + typescript_stats["total_lines"],
        }

    def _analyze_python(self) -> dict:
        stats = {
            "files": 0,
            "total_lines": 0,
            "empty_lines": 0,
            "comment_lines": 0,
            "functions": 0,
            "classes": 0,
            "complex_files": [],
        }

        for py_file in self.root.rglob("*.py"):
            if self.should_ignore(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")
                stats["files"] += 1
                stats["total_lines"] += len(lines)
                stats["empty_lines"] += sum(1 for l in lines if not l.strip())
                stats["comment_lines"] += sum(1 for l in lines if l.strip().startswith("#"))

                # آنالیز AST برای توابع و کلاس‌ها
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            stats["functions"] += 1
                        elif isinstance(node, ast.ClassDef):
                            stats["classes"] += 1
                except:
                    pass

                # فایل‌های خیلی بزرگ
                if len(lines) > 500:
                    stats["complex_files"].append(
                        {"path": str(py_file.relative_to(self.root)), "lines": len(lines)}
                    )
            except:
                pass

        if stats["complex_files"]:
            self.add_finding(
                "warning",
                "complexity",
                f"{len(stats['complex_files'])} فایل پایتون بزرگ (>500 خط)",
                suggestion="فایل‌ها را به ماژول‌های کوچکتر تقسیم کنید",
            )

        return stats

    def _analyze_typescript(self) -> dict:
        stats = {"files": 0, "total_lines": 0, "components": 0, "hooks": 0}

        for ts_file in self.root.rglob("*.tsx"):
            if self.should_ignore(ts_file):
                continue
            try:
                content = ts_file.read_text(encoding="utf-8")
                lines = content.split("\n")
                stats["files"] += 1
                stats["total_lines"] += len(lines)

                if "export default function" in content or "export function" in content:
                    stats["components"] += 1
                if ts_file.name.startswith("use") or "use" in ts_file.parent.name:
                    stats["hooks"] += 1
            except:
                pass

        for ts_file in self.root.rglob("*.ts"):
            if self.should_ignore(ts_file) or ts_file.suffix == ".tsx":
                continue
            try:
                content = ts_file.read_text(encoding="utf-8")
                stats["files"] += 1
                stats["total_lines"] += len(content.split("\n"))
            except:
                pass

        return stats


class SecurityAnalyzer(BaseAnalyzer):
    """آنالیزور امنیتی"""

    name = "🔒 Security Analyzer"

    def analyze(self):
        exposed_secrets = []
        sensitive_files = []
        env_files = []

        for path in self.root.rglob("*"):
            if self.should_ignore(path) or not path.is_file():
                continue

            rel_path = str(path.relative_to(self.root))

            # بررسی فایل‌های حساس
            if path.suffix.lower() in SENSITIVE_EXTENSIONS:
                sensitive_files.append(rel_path)
                self.add_finding(
                    "warning",
                    "security",
                    f"فایل حساس: {path.suffix}",
                    rel_path,
                    "اطمینان حاصل کنید در .gitignore است",
                )

            # بررسی فایل‌های .env
            if path.name.startswith(".env") and path.suffix != ".example":
                env_files.append(rel_path)

            # بررسی محتوای فایل‌های متنی برای secrets
            if path.suffix.lower() in {
                ".py",
                ".ts",
                ".tsx",
                ".js",
                ".json",
                ".env",
                ".yml",
                ".yaml",
            }:
                try:
                    content = path.read_text(encoding="utf-8", errors="ignore")
                    for pattern in SENSITIVE_PATTERNS:
                        # الگوهای مشکوک
                        if re.search(
                            rf'{pattern}\s*[:=]\s*["\'][^"\']{{8,}}["\']', content, re.IGNORECASE
                        ):
                            exposed_secrets.append({"file": rel_path, "pattern": pattern})
                            self.add_finding(
                                "critical",
                                "security",
                                f"احتمال وجود secret: {pattern}",
                                rel_path,
                                "از متغیرهای محیطی استفاده کنید",
                            )
                            break
                except:
                    pass

        self.stats = {
            "sensitive_files": sensitive_files,
            "env_files": env_files,
            "exposed_secrets": exposed_secrets,
            "security_score": max(0, 100 - len(exposed_secrets) * 20 - len(sensitive_files) * 5),
        }

        if not exposed_secrets:
            self.add_finding("success", "security", "هیچ secret آشکاری یافت نشد ✅")


class BackendAnalyzer(BaseAnalyzer):
    """آنالیزور بک‌اند FastAPI"""

    name = "🛰️ Backend Analyzer"

    def analyze(self):
        endpoints = []
        models = []
        routers = []

        api_dir = self.root / "api"
        if not api_dir.exists():
            self.add_finding("warning", "backend", "پوشه api/ یافت نشد")
            self.stats = {"status": "missing"}
            return

        for py_file in api_dir.rglob("*.py"):
            if self.should_ignore(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
                rel_path = str(py_file.relative_to(self.root))

                # شناسایی endpointها
                for match in re.finditer(
                    r'@app\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content
                ):
                    endpoints.append(
                        {"method": match.group(1).upper(), "path": match.group(2), "file": rel_path}
                    )

                # شناسایی routerها
                for match in re.finditer(
                    r'@router\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']', content
                ):
                    endpoints.append(
                        {"method": match.group(1).upper(), "path": match.group(2), "file": rel_path}
                    )

                # شناسایی مدل‌ها
                for match in re.finditer(r"class\s+(\w+)\s*\(\s*Base\s*\)", content):
                    models.append({"name": match.group(1), "file": rel_path})

                # شناسایی routerهای ماژول
                if "APIRouter" in content:
                    routers.append(rel_path)
            except:
                pass

        self.stats = {
            "endpoints": endpoints,
            "endpoints_count": len(endpoints),
            "models": models,
            "models_count": len(models),
            "routers": routers,
            "routers_count": len(routers),
        }

        self.add_finding(
            "success" if endpoints else "warning",
            "backend",
            f"{len(endpoints)} endpoint، {len(models)} مدل، {len(routers)} router",
        )


class FrontendAnalyzer(BaseAnalyzer):
    """آنالیزور فرانت‌اند Next.js"""

    name = "🎨 Frontend Analyzer"

    def analyze(self):
        pages = []
        components = []
        hooks = []

        # یافتن پوشه web
        web_dirs = [
            self.root / "apps" / "web" / "src",
            self.root / "web" / "src",
            self.root / "src",
        ]
        web_src = next((d for d in web_dirs if d.exists()), None)

        if not web_src:
            self.add_finding("warning", "frontend", "پوشه src فرانت‌اند یافت نشد")
            self.stats = {"status": "missing"}
            return

        app_dir = web_src / "app"
        components_dir = web_src / "components"
        hooks_dir = web_src / "hooks"

        # آنالیز صفحات
        if app_dir.exists():
            for page_file in app_dir.rglob("page.tsx"):
                rel = str(page_file.relative_to(app_dir))
                route = "/" + str(Path(rel).parent).replace("\\", "/").replace("(.)", "")
                if route == "/.":
                    route = "/"
                pages.append({"route": route, "file": str(page_file.relative_to(self.root))})

        # آنالیز کامپوننت‌ها
        if components_dir.exists():
            for comp_file in components_dir.rglob("*.tsx"):
                components.append(str(comp_file.relative_to(self.root)))

        # آنالیز هوک‌ها
        if hooks_dir.exists():
            for hook_file in hooks_dir.glob("*.ts"):
                hooks.append(hook_file.stem)

        self.stats = {
            "pages": pages,
            "pages_count": len(pages),
            "components": components,
            "components_count": len(components),
            "hooks": hooks,
            "hooks_count": len(hooks),
        }

        self.add_finding(
            "success" if pages else "warning",
            "frontend",
            f"{len(pages)} صفحه، {len(components)} کامپوننت، {len(hooks)} هوک",
        )


class HealthCheckAnalyzer(BaseAnalyzer):
    """آنالیزور سلامت کلی"""

    name = "💊 Health Check Analyzer"

    def analyze(self):
        checks = {}

        # بررسی فایل‌های حیاتی
        critical_files = {
            "package.json": self.root / "package.json",
            "requirements.txt": self.root / "requirements.txt",
            "README.md": self.root / "README.md",
            ".env": self.root / ".env",
            "api/main.py": self.root / "api" / "main.py",
        }

        for name, path in critical_files.items():
            checks[name] = path.exists()

        # بررسی پوشه‌های حیاتی
        critical_dirs = {
            "api": self.root / "api",
            "web": self.root / "apps" / "web",
            "docs": self.root / "docs",
        }

        for name, path in critical_dirs.items():
            checks[f"dir_{name}"] = path.exists()

        # محاسبه امتیاز سلامت
        total = len(checks)
        passed = sum(1 for v in checks.values() if v)
        health_score = round((passed / total) * 100, 1) if total > 0 else 0

        self.stats = {
            "checks": checks,
            "passed": passed,
            "total": total,
            "health_score": health_score,
        }

        if health_score >= 80:
            self.add_finding("success", "health", f"امتیاز سلامت: {health_score}% ✅")
        elif health_score >= 50:
            self.add_finding("warning", "health", f"امتیاز سلامت: {health_score}% ⚠️")
        else:
            self.add_finding("critical", "health", f"امتیاز سلامت: {health_score}% ❌")


class ReportGenerator:
    """تولیدکننده گزارش نهایی"""

    def __init__(self, analyzers: List[BaseAnalyzer]):
        self.analyzers = analyzers

    def generate_text_report(self) -> str:
        lines = [
            "=" * 70,
            "🔬 Econojin Deep Project Analysis Report",
            f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📁 Root: {ROOT}",
            "=" * 70,
        ]

        # خلاصه کلی
        all_findings = []
        for analyzer in self.analyzers:
            all_findings.extend(analyzer.findings)

        critical = sum(1 for f in all_findings if f["severity"] == "critical")
        warnings = sum(1 for f in all_findings if f["severity"] == "warning")
        successes = sum(1 for f in all_findings if f["severity"] == "success")

        lines.extend(
            [
                "",
                "📊 خلاصه کلی:",
                f"   🔴 Critical: {critical}",
                f"   🟡 Warning:  {warnings}",
                f"   🟢 Success:  {successes}",
                f"   📝 Total:    {len(all_findings)}",
                "",
                "=" * 70,
            ]
        )

        # گزارش هر آنالیزور
        for analyzer in self.analyzers:
            lines.extend(
                [
                    "",
                    f"{'='*70}",
                    f"{analyzer.name}",
                    "=" * 70,
                ]
            )

            # آمار
            if analyzer.stats:
                lines.append("📈 آمار:")
                for key, value in analyzer.stats.items():
                    if isinstance(value, (int, float, str, bool)):
                        lines.append(f"   • {key}: {value}")
                    elif isinstance(value, dict) and len(value) < 10:
                        lines.append(f"   • {key}:")
                        for k, v in list(value.items())[:5]:
                            lines.append(f"       - {k}: {v}")

            # یافته‌ها
            if analyzer.findings:
                lines.append("\n🔍 یافته‌ها:")
                for f in analyzer.findings[:15]:
                    icon = {"critical": "🔴", "warning": "🟡", "info": "🔵", "success": "🟢"}.get(
                        f["severity"], "⚪"
                    )
                    lines.append(f"   {icon} [{f['category']}] {f['message']}")
                    if f.get("path"):
                        lines.append(f"      📄 {f['path']}")
                    if f.get("suggestion"):
                        lines.append(f"      💡 {f['suggestion']}")
                if len(analyzer.findings) > 15:
                    lines.append(f"   ... و {len(analyzer.findings) - 15} مورد دیگر")

        lines.extend(["", "=" * 70, "✅ تحلیل کامل شد", "=" * 70])
        return "\n".join(lines)

    def generate_json_report(self) -> dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "root": str(ROOT),
            "summary": {
                "critical": sum(
                    1 for a in self.analyzers for f in a.findings if f["severity"] == "critical"
                ),
                "warning": sum(
                    1 for a in self.analyzers for f in a.findings if f["severity"] == "warning"
                ),
                "success": sum(
                    1 for a in self.analyzers for f in a.findings if f["severity"] == "success"
                ),
            },
            "analyzers": {
                analyzer.name: {"stats": analyzer.stats, "findings": analyzer.findings}
                for analyzer in self.analyzers
            },
        }


def main():
    print("🔬 Econojin Deep Project Analyzer v2.0")
    print("=" * 60)
    print(f"📁 Root: {ROOT}")
    print()

    # ایجاد آنالیزورها
    analyzers = [
        StructureAnalyzer(ROOT),
        DependencyAnalyzer(ROOT),
        CodeQualityAnalyzer(ROOT),
        SecurityAnalyzer(ROOT),
        BackendAnalyzer(ROOT),
        FrontendAnalyzer(ROOT),
        HealthCheckAnalyzer(ROOT),
    ]

    # اجرای آنالیز
    for i, analyzer in enumerate(analyzers, 1):
        print(f"[{i}/{len(analyzers)}] Running {analyzer.name}...")
        try:
            analyzer.analyze()
        except Exception as e:
            print(f"   ⚠️ Error: {e}")

    # تولید گزارش
    print("\n📝 Generating reports...")
    generator = ReportGenerator(analyzers)

    # گزارش متنی
    text_report = generator.generate_text_report()
    text_path = REPORT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    text_path.write_text(text_report, encoding="utf-8")
    print(f"✅ Text report: {text_path}")

    # گزارش JSON
    json_report = generator.generate_json_report()
    json_path = REPORT_DIR / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    json_path.write_text(
        json.dumps(json_report, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    print(f"✅ JSON report: {json_path}")

    # نمایش گزارش متنی
    print("\n" + text_report)

    return 0


if __name__ == "__main__":
    sys.exit(main())

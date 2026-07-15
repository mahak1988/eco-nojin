#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - اسکریپت شناسایی، آنالیز و یکپارچه‌سازی (نسخه نهایی)
بر اساس ساختار واقعی پروژه

این اسکریپت:
- تمام ماژول‌های apps را شناسایی می‌کند
- وابستگی‌های بین ماژول‌ها را آنالیز می‌کند
- نقاط ورود (entrypoints) را شناسایی می‌کند
- گزارش کامل از معماری پروژه تولید می‌کند
- یکپارچه‌سازی بین ماژول‌ها را بررسی می‌کند
- فایل‌های گم‌شده را شناسایی می‌کند
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict
import ast

# ============================================================
# مسیرهای پروژه (بر اساس ساختار واقعی)
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = PROJECT_ROOT / "apps"

# ماژول‌های شناسایی‌شده در apps
MODULES = {
    "ai_agents": APPS_DIR / "ai_agents",
    "cms": APPS_DIR / "cms",
    "library": APPS_DIR / "library",
    "shared": APPS_DIR / "shared",
    "simulation": APPS_DIR / "simulation",
    "users": APPS_DIR / "users",
    "web": APPS_DIR / "web",
}

# حوزه‌های شبیه‌سازی
SIMULATION_DOMAINS = [
    "agriculture", "biodiversity", "carbon_cycle", "economics",
    "ecosystem_services", "energy", "hydrology", "soil", "water_quality"
]

# زیرماژول‌های shared
SHARED_SUBMODULES = ["ai", "database", "knowledge"]

# ============================================================
# ابزارهای کمکی
# ============================================================

def log(message: str, level: str = "INFO"):
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "HEADER": "\033[95m",
        "BOLD": "\033[1m",
        "END": "\033[0m",
    }
    print(f"{colors.get(level, '')}[{level}]{colors.get('END', '')} {message}")

def get_python_files(directory: Path) -> List[Path]:
    """دریافت تمام فایل‌های پایتون در یک پوشه"""
    if not directory.exists():
        return []
    return [f for f in directory.rglob("*.py") if "__pycache__" not in str(f)]

def get_js_files(directory: Path) -> List[Path]:
    """دریافت تمام فایل‌های جاوااسکریپت/TypeScript در یک پوشه"""
    if not directory.exists():
        return []
    exts = {".ts", ".tsx", ".js", ".jsx"}
    return [f for f in directory.rglob("*") if f.suffix in exts and "node_modules" not in str(f)]

def get_json_files(directory: Path) -> List[Path]:
    """دریافت تمام فایل‌های JSON در یک پوشه"""
    if not directory.exists():
        return []
    return [f for f in directory.rglob("*.json") if "node_modules" not in str(f)]

# ============================================================
# کلاس اصلی آنالیزور
# ============================================================

class EcoNojinAnalyzer:
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "project": "Eco Nojin",
            "modules": {},
            "statistics": {},
            "dependencies": {},
            "issues": [],
            "recommendations": []
        }
        self.module_stats = {}
        self.all_imports = defaultdict(list)

    # ------------------------------------------------------------
    # شناسایی ماژول‌ها
    # ------------------------------------------------------------
    def discover_modules(self):
        log("\n🔍 شناسایی ماژول‌های پروژه", "HEADER")
        log("=" * 70, "HEADER")

        for name, path in MODULES.items():
            if path.exists():
                py_files = get_python_files(path)
                js_files = get_js_files(path)
                json_files = get_json_files(path)

                self.module_stats[name] = {
                    "path": str(path),
                    "python_files": len(py_files),
                    "js_files": len(js_files),
                    "json_files": len(json_files),
                    "total_files": len(py_files) + len(js_files) + len(json_files),
                    "has_package_json": (path / "package.json").exists(),
                    "has_requirements": (path / "requirements.txt").exists(),
                    "has_main": (path / "main.py").exists() or (path / "index.ts").exists() or (path / "index.js").exists(),
                }
                log(f"   ✅ {name}: {self.module_stats[name]['total_files']} فایل", "SUCCESS")
            else:
                log(f"   ❌ {name}: وجود ندارد", "ERROR")
                self.module_stats[name] = {"exists": False}

    # ------------------------------------------------------------
    # تحلیل وابستگی‌ها
    # ------------------------------------------------------------
    def analyze_dependencies(self):
        log("\n🔗 تحلیل وابستگی‌های بین ماژول‌ها", "HEADER")
        log("=" * 70, "HEADER")

        # تحلیل importهای پایتون
        for name, path in MODULES.items():
            if not path.exists():
                continue

            for py_file in get_python_files(path):
                try:
                    with open(py_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                self._add_import(name, alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                self._add_import(name, node.module)
                except Exception as e:
                    pass

        # نمایش وابستگی‌ها
        for module, imports in self.all_imports.items():
            if imports:
                unique_imports = list(set(imports))
                # تشخیص وابستگی به ماژول‌های دیگر
                deps = []
                for other in MODULES.keys():
                    if other != module and any(other in imp for imp in unique_imports):
                        deps.append(other)
                if deps:
                    log(f"   {module} ← وابسته به: {', '.join(deps)}", "INFO")

    def _add_import(self, module: str, import_name: str):
        """افزودن یک import به لیست"""
        if module not in self.all_imports:
            self.all_imports[module] = []
        self.all_imports[module].append(import_name)

    # ------------------------------------------------------------
    # تحلیل فایل‌های پیکربندی
    # ------------------------------------------------------------
    def analyze_config_files(self):
        log("\n⚙️ تحلیل فایل‌های پیکربندی", "HEADER")
        log("=" * 70, "HEADER")

        # package.json
        for name, path in MODULES.items():
            pkg_file = path / "package.json"
            if pkg_file.exists():
                try:
                    with open(pkg_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    deps = data.get("dependencies", {})
                    dev_deps = data.get("devDependencies", {})
                    scripts = data.get("scripts", {})
                    log(f"   📦 {name}: {len(deps)} deps, {len(dev_deps)} devDeps", "SUCCESS")
                except:
                    pass

        # requirements.txt
        req_files = list(PROJECT_ROOT.glob("**/requirements.txt"))
        for req in req_files:
            try:
                with open(req, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f.readlines() if l.strip() and not l.startswith("#")]
                    parent = req.parent.name
                    log(f"   📄 {parent}/requirements.txt: {len(lines)} کتابخانه", "SUCCESS")
            except:
                pass

    # ------------------------------------------------------------
    # تحلیل ساختار فرانت‌اند
    # ------------------------------------------------------------
    def analyze_frontend(self):
        log("\n🌐 تحلیل ساختار فرانت‌اند", "HEADER")
        log("=" * 70, "HEADER")

        web_path = MODULES["web"]
        if not web_path.exists():
            log("   ❌ پوشه web وجود ندارد", "ERROR")
            return

        src_path = web_path / "src"
        if src_path.exists():
            # پوشه‌های اصلی
            subdirs = [d for d in src_path.iterdir() if d.is_dir()]
            log(f"   📁 پوشه‌های src: {', '.join([d.name for d in subdirs])}", "INFO")

            # صفحات
            pages_path = src_path / "pages"
            if pages_path.exists():
                pages = [d.name for d in pages_path.iterdir() if d.is_dir() and not d.name.startswith("_")]
                log(f"   📄 صفحات: {len(pages)} ماژول", "SUCCESS")

            # i18n
            i18n_path = src_path / "i18n" / "locales"
            if i18n_path.exists():
                langs = [f.stem for f in i18n_path.glob("*.json")]
                log(f"   🌍 زبان‌های پشتیبانی‌شده: {', '.join(langs)}", "SUCCESS")

            # سرویس‌ها
            services_path = src_path / "services"
            if services_path.exists():
                svcs = [f.stem for f in services_path.glob("*.ts")]
                log(f"   🔧 سرویس‌ها: {', '.join(svcs)}", "INFO")

            # شبیه‌سازها
            sim_path = src_path / "simulators"
            if sim_path.exists():
                sims = [d.name for d in sim_path.iterdir() if d.is_dir()]
                log(f"   🧪 شبیه‌سازهای فرانت‌اند: {', '.join(sims) if sims else 'هیچ‌کدام'}", "INFO")

    # ------------------------------------------------------------
    # تحلیل شبیه‌سازها
    # ------------------------------------------------------------
    def analyze_simulators(self):
        log("\n🧪 تحلیل شبیه‌سازهای علمی", "HEADER")
        log("=" * 70, "HEADER")

        sim_path = MODULES["simulation"]
        if not sim_path.exists():
            log("   ❌ پوشه simulation وجود ندارد", "ERROR")
            return

        for domain in SIMULATION_DOMAINS:
            domain_path = sim_path / domain
            if domain_path.exists():
                py_files = get_python_files(domain_path)
                subdirs = [d.name for d in domain_path.iterdir() if d.is_dir()]
                log(f"   ✅ {domain}: {len(py_files)} فایل, زیرماژول‌ها: {', '.join(subdirs) if subdirs else 'هیچ‌کدام'}", "SUCCESS")
            else:
                log(f"   ❌ {domain}: وجود ندارد", "ERROR")

    # ------------------------------------------------------------
    # تحلیل AI Agents
    # ------------------------------------------------------------
    def analyze_ai_agents(self):
        log("\n🤖 تحلیل عامل‌های هوش مصنوعی", "HEADER")
        log("=" * 70, "HEADER")

        ai_path = MODULES["ai_agents"]
        if not ai_path.exists():
            log("   ❌ پوشه ai_agents وجود ندارد", "ERROR")
            return

        agents_path = ai_path / "agents"
        if agents_path.exists():
            agents = [d.name for d in agents_path.iterdir() if d.is_dir()]
            for agent in agents:
                agent_files = get_python_files(agents_path / agent)
                log(f"   🤖 {agent}: {len(agent_files)} فایل", "SUCCESS")

        # بررسی shared/ai
        shared_ai = MODULES["shared"] / "ai"
        if shared_ai.exists():
            ai_subdirs = [d.name for d in shared_ai.iterdir() if d.is_dir()]
            log(f"\n   🔗 shared/ai: {', '.join(ai_subdirs)}", "INFO")

    # ------------------------------------------------------------
    # بررسی یکپارچگی
    # ------------------------------------------------------------
    def check_integration(self):
        log("\n🔗 بررسی یکپارچگی بین ماژول‌ها", "HEADER")
        log("=" * 70, "HEADER")

        issues = []
        recommendations = []

        # 1. بررسی وجود فایل main
        main_files = []
        for name, path in MODULES.items():
            if path.exists():
                for mf in path.glob("main.py"):
                    main_files.append((name, mf))
                for mf in path.glob("index.ts"):
                    main_files.append((name, mf))

        if main_files:
            log(f"   📌 نقاط ورود: {', '.join([f'{n}: {p.name}' for n, p in main_files])}", "INFO")
        else:
            issues.append("هیچ فایل main یا index در ماژول‌ها پیدا نشد")
            recommendations.append("برای هر ماژول یک نقطه ورود تعریف کنید")

        # 2. بررسی وجود package.json در web
        if not (MODULES["web"] / "package.json").exists():
            issues.append("فایل package.json در web وجود ندارد")
            recommendations.append("در پوشه web یک package.json ایجاد کنید")

        # 3. بررسی وجود requirements
        has_req = False
        for name, path in MODULES.items():
            if path.exists() and (path / "requirements.txt").exists():
                has_req = True
                break
        if not has_req:
            recommendations.append("برای ماژول‌های پایتون فایل requirements.txt ایجاد کنید")

        # 4. بررسی زبان‌های i18n
        locales_path = MODULES["web"] / "src" / "i18n" / "locales"
        if locales_path.exists():
            langs = [f.stem for f in locales_path.glob("*.json")]
            if "fa" in langs and "en" in langs:
                log("   ✅ پشتیبانی از فارسی و انگلیسی", "SUCCESS")
            else:
                issues.append("پشتیبانی از زبان فارسی یا انگلیسی کامل نیست")
        else:
            issues.append("پوشه locales برای i18n وجود ندارد")

        # ثبت مشکلات و توصیه‌ها
        for issue in issues:
            log(f"   ⚠️ {issue}", "WARNING")
        for rec in recommendations:
            log(f"   💡 {rec}", "INFO")

        self.results["issues"] = issues
        self.results["recommendations"] = recommendations

    # ------------------------------------------------------------
    # تولید گزارش نهایی
    # ------------------------------------------------------------
    def generate_report(self):
        log("\n📊 تولید گزارش نهایی", "HEADER")
        log("=" * 70, "HEADER")

        self.results["statistics"] = self.module_stats
        self.results["dependencies"] = dict(self.all_imports)

        # خلاصه
        total_files = sum(s.get("total_files", 0) for s in self.module_stats.values())
        total_py = sum(s.get("python_files", 0) for s in self.module_stats.values())
        total_js = sum(s.get("js_files", 0) for s in self.module_stats.values())

        log(f"\n📈 خلاصه آماری:", "BOLD")
        log(f"   مجموع فایل‌ها: {total_files}")
        log(f"   فایل‌های پایتون: {total_py}")
        log(f"   فایل‌های جاوااسکریپت: {total_js}")
        log(f"   ماژول‌های فعال: {len([m for m in self.module_stats.values() if m.get('total_files', 0) > 0])}")

        # ذخیره گزارش
        report_file = PROJECT_ROOT / "eco_nojin_analysis_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        log(f"\n✅ گزارش در {report_file} ذخیره شد", "SUCCESS")

    # ------------------------------------------------------------
    # اجرای کامل
    # ------------------------------------------------------------
    def run(self):
        log("🌱 Eco Nojin - اسکریپت شناسایی و آنالیز نهایی", "HEADER")
        log("=" * 70, "HEADER")

        self.discover_modules()
        self.analyze_dependencies()
        self.analyze_config_files()
        self.analyze_frontend()
        self.analyze_simulators()
        self.analyze_ai_agents()
        self.check_integration()
        self.generate_report()

        log("\n✅ آنالیز کامل شد!", "SUCCESS")

# ============================================================
# نقطه ورود
# ============================================================

if __name__ == "__main__":
    try:
        analyzer = EcoNojinAnalyzer()
        analyzer.run()
    except KeyboardInterrupt:
        log("\n⏹️ متوقف شد.", "WARNING")
        sys.exit(0)
    except Exception as e:
        log(f"❌ خطا: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
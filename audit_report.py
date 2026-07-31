import ast
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List


class CodebaseAuditor:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.report = {
            "stack_identification": {},
            "database_and_orm": {},
            "async_and_caching": {},
            "security_mechanisms": {},
            "devops_maturity": {},
            "critical_findings": [],
        }

    def _read_file_safe(self, file_path: Path) -> str:
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return ""

    def analyze_dependencies(self):
        """تحلیل پشته فناوری از طریق فایل‌های وابستگی"""
        print("[*] Analyzing Dependencies...")
        deps = {"python": [], "node": [], "other": []}

        for req_file in self.root_dir.glob("*requirements*.txt"):
            content = self._read_file_safe(req_file)
            deps["python"].extend(
                [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.startswith("#")
                ]
            )

        pipfile = self.root_dir / "Pipfile"
        if pipfile.exists():
            content = self._read_file_safe(pipfile)
            deps["python"].extend(re.findall(r'"([^"]+)"', content))

        pkg_json = self.root_dir / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(self._read_file_safe(pkg_json))
                deps["node"].extend(list(data.get("dependencies", {}).keys()))
                deps["node"].extend(list(data.get("devDependencies", {}).keys()))
            except json.JSONDecodeError:
                pass

        self.report["stack_identification"] = deps

    def analyze_python_ast(self, file_path: Path):
        """تحلیل فایل‌های پایتون با استفاده از AST"""
        content = self._read_file_safe(file_path)
        if not content:
            return None

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return None

        imports = []
        functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
            elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)

        return imports, functions

    def analyze_database_and_performance(self):
        """تحلیل لایه دیتابیس، ORM و Pagination"""
        print("[*] Analyzing Database & Performance Patterns...")
        orm_indicators = defaultdict(list)
        pagination_patterns = {"cursor": [], "offset": []}
        n_plus_one_risks = []

        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in str(py_file) or ".git" in str(py_file) or "__pycache__" in str(py_file):
                continue

            result = self.analyze_python_ast(py_file)
            if not result:
                continue
            imports, functions = result

            for imp in imports:
                if "sqlalchemy" in imp:
                    orm_indicators["SQLAlchemy"].append(str(py_file))
                if "django.db" in imp:
                    orm_indicators["Django ORM"].append(str(py_file))
                if "prisma" in imp:
                    orm_indicators["Prisma"].append(str(py_file))

            content = self._read_file_safe(py_file)
            if re.search(r"\.offset\(|\.limit\(", content):
                pagination_patterns["offset"].append(str(py_file))
            if re.search(r"cursor|after_cursor|before_cursor", content, re.IGNORECASE):
                pagination_patterns["cursor"].append(str(py_file))

            if re.search(r"for\s+\w+\s+in\s+\w+:.*\.(query|get|filter|all)\(", content, re.DOTALL):
                n_plus_one_risks.append(str(py_file))

        # اصلاح نام کلید برای هماهنگی کامل
        self.report["database_and_orm"] = {
            "detected_orms": dict(orm_indicators),
            "pagination_type": pagination_patterns,
            "potential_n_plus_one_risks": list(set(n_plus_one_risks)),
        }

    def analyze_async_and_caching(self):
        """تحلیل پردازش ناهمگام و مکانیزم‌های کش"""
        print("[*] Analyzing Async & Caching...")
        async_indicators = {"message_broker": [], "background_tasks": [], "caching": []}

        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in str(py_file) or ".git" in str(py_file) or "__pycache__" in str(py_file):
                continue
            content = self._read_file_safe(py_file)

            if re.search(r"celery|kombu|rabbitmq|kafka|redis\.from_url", content, re.IGNORECASE):
                async_indicators["message_broker"].append(str(py_file))
            if re.search(r"BackgroundTasks|asyncio\.create_task|threading\.Thread", content):
                async_indicators["background_tasks"].append(str(py_file))
            if re.search(
                r"redis\.|cachetools|@cached|cache\.set|cache\.get", content, re.IGNORECASE
            ):
                async_indicators["caching"].append(str(py_file))

        self.report["async_and_caching"] = async_indicators

    def analyze_security(self):
        """تحلیل مکانیزم‌های امنیتی"""
        print("[*] Analyzing Security Mechanisms...")
        security_findings = {
            "self_deletion_protection": False,
            "rate_limiting": False,
            "sensitive_data_exposure_risk": [],
        }

        for py_file in self.root_dir.rglob("*.py"):
            if "venv" in str(py_file) or ".git" in str(py_file) or "__pycache__" in str(py_file):
                continue
            content = self._read_file_safe(py_file)

            if re.search(
                r"if\s+.*user\.id\s*==\s*.*current_user\.id|if\s+.*id\s*==\s*.*request\.user\.id",
                content,
            ):
                security_findings["self_deletion_protection"] = True

            if re.search(r"@limiter\.limit|@throttle|RateLimitMiddleware", content):
                security_findings["rate_limiting"] = True

            if re.search(r"return\s+.*password|\.dict\(.*password", content):
                security_findings["sensitive_data_exposure_risk"].append(str(py_file))

        self.report["security_mechanisms"] = security_findings

    def analyze_devops(self):
        """تحلیل بلوغ DevOps و CI/CD"""
        print("[*] Analyzing DevOps & CI/CD...")
        devops = {"ci_cd": [], "containerization": [], "testing": []}

        if (self.root_dir / ".github" / "workflows").exists():
            devops["ci_cd"].append("GitHub Actions")
        if (self.root_dir / ".gitlab-ci.yml").exists():
            devops["ci_cd"].append("GitLab CI")

        if (self.root_dir / "Dockerfile").exists():
            devops["containerization"].append("Dockerfile")
        if (self.root_dir / "docker-compose.yml").exists() or (
            self.root_dir / "docker-compose.yaml"
        ).exists():
            devops["containerization"].append("Docker Compose")

        test_files = list(self.root_dir.rglob("test_*.py")) + list(self.root_dir.rglob("*_test.py"))
        if test_files:
            devops["testing"].append(f"Found {len(test_files)} test files")

        self.report["devops_maturity"] = devops

    def generate_critical_findings(self):
        """تولید یافته‌های بحرانی بر اساس داده‌های جمع‌آوری شده"""
        print("[*] Generating Critical Findings...")

        if not self.report["async_and_caching"]["message_broker"]:
            self.report["critical_findings"].append(
                "CRITICAL: No Message Broker detected. Report generation might be blocking the main thread."
            )

        if (
            self.report["database_and_orm"]["pagination_type"]["offset"]
            and not self.report["database_and_orm"]["pagination_type"]["cursor"]
        ):
            self.report["critical_findings"].append(
                "WARNING: Using Offset-based pagination. Consider migrating to Cursor-based for large datasets."
            )

        if self.report["database_and_orm"]["potential_n_plus_one_risks"]:
            self.report["critical_findings"].append(
                f"WARNING: Potential N+1 query issues detected in: {self.report['database_and_orm']['potential_n_plus_one_risks']}"
            )

        if not self.report["security_mechanisms"]["rate_limiting"]:
            self.report["critical_findings"].append(
                "CRITICAL: No Rate Limiting detected on API endpoints. Vulnerable to DDoS/Brute-force."
            )

    def run(self):
        print(f"🚀 Starting Econojin Codebase Audit in: {self.root_dir}\n")
        self.analyze_dependencies()
        self.analyze_database_and_performance()
        self.analyze_async_and_caching()
        self.analyze_security()
        self.analyze_devops()
        self.generate_critical_findings()

        with open("audit_report.json", "w", encoding="utf-8") as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)

        print("\n✅ Audit Complete. Report saved to 'audit_report.json'")
        print("\n--- CRITICAL FINDINGS ---")
        for finding in self.report["critical_findings"]:
            print(f"⚠️ {finding}")


if __name__ == "__main__":
    auditor = CodebaseAuditor(root_dir=".")
    auditor.run()

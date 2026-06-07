# ⚠️ SECURITY WARNING: This file contains dynamic code execution
# Review all exec/eval usage for security implications
# Consider replacing with safer alternatives
"""
توابع امنیتی مشترک برای جایگزینی exec و subprocess
نسخه اصلاح شده برای Windows و رفع circular import
"""

import ast
import importlib
import importlib.util
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class SafetyCheck:
    """نتیجه بررسی امنیتی"""

    safe: bool
    reason: str
    suggestion: str = ""


class SafeModuleLoader:
    """
    جایگزین امن برای exec() در import های پویا
    """

    ALLOWED_MODULES: Set[str] = {
        "scripts.models.soil_carbon.aquacrop",
        "scripts.models.soil_carbon.rothc",
        "scripts.models.hydrology.swat_plus",
        "scripts.models.base_model",
        "scripts.api.services.simulation_service",
        "scripts.utils.daily_report",
    }

    @classmethod
    def load_module(cls, module_path: str) -> Any:
        """بارگذاری امن ماژول بدون exec"""
        if not isinstance(module_path, str):
            raise ValueError(f"Module path must be string, got {type(module_path)}")

        if module_path not in cls.ALLOWED_MODULES:
            raise ValueError(
                f"Module '{module_path}' not in allowed list. " f"Allowed: {cls.ALLOWED_MODULES}"
            )

        if not re.match(r"^[a-zA-Z0-9_.]+$", module_path):
            raise ValueError(f"Invalid characters in module path: {module_path}")

        try:
            return importlib.import_module(module_path)
        except ImportError as e:
            raise ImportError(f"Cannot import '{module_path}': {e}")

    @classmethod
    def load_class(cls, module_path: str, class_name: str) -> Any:
        """بارگذاری امن کلاس از ماژول"""
        module = cls.load_module(module_path)

        if not hasattr(module, class_name):
            raise AttributeError(f"Class '{class_name}' not found in module '{module_path}'")

        return getattr(module, class_name)


class SafeSubprocess:
    """
    جایگزین امن برای subprocess با shell=True
    سازگار با Windows, Linux, macOS
    """

    ALLOWED_COMMANDS: Set[str] = {
        "pip",
        "python",
        "pytest",
        "black",
        "isort",
        "flake8",
        "mypy",
        "ruff",
        "git",
        "node",
        "npm",
        "pnpm",
    }

    @classmethod
    def _get_command_name(cls, command_path: str) -> str:
        """استخراج نام دستور از مسیر کامل (سازگار با Windows)"""
        try:
            # Path.stem نام فایل را بدون extension برمی‌گرداند
            # مثال: 'D:\\path\\python.exe' -> 'python'
            # مثال: '/usr/bin/python3' -> 'python3'
            cmd_stem = Path(command_path).stem.lower()

            # حذف نسخه از نام (python3 -> python)
            if cmd_stem.startswith("python") and cmd_stem != "python":
                return "python"

            return cmd_stem
        except Exception:
            return str(command_path).lower()

    @classmethod
    def run(
        cls,
        command: List[str],
        timeout: int = 300,
        check: bool = True,
        capture_output: bool = True,
        cwd: Optional[Path] = None,
    ) -> subprocess.CompletedProcess:
        """اجرای امن دستور بدون shell"""
        if not command or not isinstance(command, list):
            raise ValueError("Command must be a non-empty list")

        base_command = command[0]
        cmd_name = cls._get_command_name(base_command)

        allowed_lower = {c.lower() for c in cls.ALLOWED_COMMANDS}
        if cmd_name not in allowed_lower:
            raise ValueError(
                f"Command '{base_command}' (resolved: '{cmd_name}') not allowed. "
                f"Allowed: {cls.ALLOWED_COMMANDS}"
            )

        # بررسی آرگومان‌ها برای کاراکترهای خطرناک
        dangerous_chars = {";", "&", "|", "`", "$", ">", "<"}
        for arg in command[1:]:
            if any(char in str(arg) for char in dangerous_chars):
                raise ValueError(f"Dangerous character found in argument: {arg}")

        try:
            result = subprocess.run(
                command,
                timeout=timeout,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=cwd,
            )
            return result
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out after {timeout}s")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed with code {e.returncode}: {e.stderr}")

    @classmethod
    def pip_install(
        cls, package: str, version: Optional[str] = None, upgrade: bool = False
    ) -> subprocess.CompletedProcess:
        """نصب امن پکیج pip"""
        command = ["pip", "install"]

        if upgrade:
            command.append("--upgrade")

        if version:
            command.append(f"{package}=={version}")
        else:
            command.append(package)

        return cls.run(command)


class CodeAnalyzer:
    """تحلیل‌گر کد برای یافتن الگوهای خطرناک"""

    DANGEROUS_PATTERNS = {
        "exec(": "استفاده از exec",
        # SECURITY WARNING: Review eval usage for security implications
        "eval(": "استفاده از eval",
        "compile(": "استفاده از compile",
        "shell=True": "subprocess با shell=True",
        "__import__": "import پویا",
        "globals()": "دسترسی به globals",
        "locals()": "دسترسی به locals",
        "pickle.load": "deserialization ناامن",
        "yaml.load(": "yaml.load بدون Loader",
        "os.system": "استفاده از os.system",
    }

    @classmethod
    def scan_file(cls, file_path: Path) -> List[Dict]:
        """اسکن فایل برای یافتن الگوهای خطرناک"""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")

            for line_num, line in enumerate(content.splitlines(), 1):
                for pattern, description in cls.DANGEROUS_PATTERNS.items():
                    if pattern in line:
                        issues.append(
                            {
                                "file": str(file_path),
                                "line": line_num,
                                "pattern": pattern,
                                "description": description,
                                "code": line.strip(),
                            }
                        )
        except Exception as e:
            issues.append({"file": str(file_path), "error": str(e)})

        return issues

    @classmethod
    def scan_directory(cls, directory: Path) -> List[Dict]:
        """اسکن دایرکتوری"""
        all_issues = []

        for py_file in directory.rglob("*.py"):
            if any(part in str(py_file) for part in [".venv", "node_modules", "__pycache__"]):
                continue

            issues = cls.scan_file(py_file)
            all_issues.extend(issues)

        return all_issues

    @classmethod
    def check_syntax(cls, file_path: Path) -> SafetyCheck:
        """بررسی syntax فایل"""
        try:
            content = file_path.read_text(encoding="utf-8")
            ast.parse(content)
            return SafetyCheck(safe=True, reason="Syntax valid")
        except SyntaxError as e:
            return SafetyCheck(
                safe=False,
                reason=f"Syntax error at line {e.lineno}: {e.msg}",
                suggestion=f"Fix syntax error before processing",
            )

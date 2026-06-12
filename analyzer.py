import os
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Any


# ==============================
# تنظیمات و ثابت‌ها
# ==============================

IGNORE_DIRS: Set[str] = {
    ".git",
    "node_modules",
    "venv",
    "env",
    "__pycache__",
    "build",
    "dist",
    ".next",
    "coverage",
    ".turbo",
    ".parcel-cache",
}

IGNORE_FILES: Set[str] = {
    ".DS_Store",
    "package-lock.json",
    "yarn.lock",
    "Pipfile.lock",
}

CODE_EXTENSIONS: Set[str] = {
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".py",
    ".html",
    ".css",
    ".vue",
    ".svelte",
}

LARGE_FILE_THRESHOLD_BYTES: int = 2 * 1024 * 1024  # 2MB


# ==============================
# ساختار داده گزارش
# ==============================

@dataclass
class ProjectReport:
    total_files: int = 0
    file_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_lines_of_code: int = 0
    dependencies: Dict[str, List[str]] = field(
        default_factory=lambda: {"frontend": [], "backend": [], "infra": []}
    )
    code_smells: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    architecture_notes: List[str] = field(default_factory=list)
    large_files: List[Tuple[str, int]] = field(default_factory=list)
    root_dir: str = "."
    monorepo_signals: List[str] = field(default_factory=list)


# ==============================
# توابع کمکی
# ==============================

def normalize_path(path: str) -> str:
    """یک مسیر را به فرم استاندارد (با /) تبدیل می‌کند."""
    return path.replace(os.sep, "/")


def safe_read_lines(filepath: str) -> List[str]:
    """خواندن امن خطوط یک فایل متنی."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.readlines()
    except UnicodeDecodeError:
        return []
    except Exception:
        return []


def detect_large_file(filepath: str, report: ProjectReport) -> None:
    """شناسایی فایل‌های بزرگ (مثلاً تصاویر یا باینری‌ها)."""
    try:
        size = os.path.getsize(filepath)
        if size >= LARGE_FILE_THRESHOLD_BYTES:
            report.large_files.append((normalize_path(filepath), size))
    except OSError:
        pass


def analyze_package_json(filepath: str, report: ProjectReport) -> None:
    """تحلیل فایل package.json برای شناسایی وابستگی‌ها و نوع پروژه."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        deps = list(data.get("dependencies", {}).keys())
        dev_deps = list(data.get("devDependencies", {}).keys())
        all_deps = deps + dev_deps
        report.dependencies["frontend"].extend(all_deps)

        report.architecture_notes.append(
            f"پروژه فرانت‌اند/Node.js شناسایی شد (package.json در {normalize_path(filepath)})."
        )

        # سیگنال‌های ساده برای تشخیص Next.js / React و غیره
        if "next" in deps or "next" in dev_deps:
            report.architecture_notes.append("فریم‌ورک Next.js شناسایی شد.")
        if "react" in deps or "react" in dev_deps:
            report.architecture_notes.append("کتابخانه React شناسایی شد.")
        if "typescript" in deps or "typescript" in dev_deps:
            report.architecture_notes.append("TypeScript در پروژه استفاده شده است.")

    except Exception:
        report.architecture_notes.append(
            f"خطا در خواندن package.json در {normalize_path(filepath)}."
        )


def analyze_python_deps(filepath: str, report: ProjectReport) -> None:
    """تحلیل فایل‌های وابستگی پایتون (requirements.txt, Pipfile, pyproject.toml)."""
    report.architecture_notes.append(
        f"پروژه بک‌اند پایتون شناسایی شد ({os.path.basename(filepath)})."
    )
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [
                line.split("==")[0].strip()
                for line in f
                if line.strip() and not line.strip().startswith("#")
            ]
        report.dependencies["backend"].extend(lines)
    except Exception:
        report.architecture_notes.append(
            f"خطا در خواندن وابستگی‌های پایتون ({normalize_path(filepath)})."
        )


def analyze_infra_files(filepath: str, report: ProjectReport) -> None:
    """تحلیل فایل‌های زیرساخت (Docker, Terraform, CI)."""
    name = os.path.basename(filepath)
    if name in {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"}:
        report.dependencies["infra"].append("docker")
        report.architecture_notes.append("استفاده از Docker شناسایی شد.")
    if name.endswith(".tf"):
        report.dependencies["infra"].append("terraform")
        report.architecture_notes.append("استفاده از Terraform شناسایی شد.")
    if ".github/workflows" in filepath or name.endswith(".yml") or name.endswith(".yaml"):
        # خیلی کلی است، صرفاً یک نوت عمومی اضافه می‌کنیم
        if ".github/workflows" in normalize_path(filepath):
            report.architecture_notes.append("وجود GitHub Actions CI/CD شناسایی شد.")


def analyze_code_file(filepath: str, ext: str, report: ProjectReport) -> None:
    """تحلیل فایل‌های کد برای شمارش خطوط و شناسایی code smell ها."""
    lines = safe_read_lines(filepath)
    if not lines:
        return

    report.total_lines_of_code += len(lines)
    norm_path = normalize_path(filepath)

    for line_num, line in enumerate(lines, 1):
        # TODO / FIXME / HACK / XXX
        if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", line, re.IGNORECASE):
            report.code_smells["TODOs/FIXMEs"].append(f"{norm_path}:{line_num}")

        # console.log در فایل‌های جاوااسکریپت/تایپ‌اسکریپت
        if ext in {".js", ".jsx", ".ts", ".tsx"} and "console.log" in line:
            report.code_smells["Console Logs"].append(f"{norm_path}:{line_num}")

        # print در فایل‌های پایتون
        if ext == ".py" and re.search(r"\bprint\s*\(", line):
            report.code_smells["Print Statements"].append(f"{norm_path}:{line_num}")

        # طول خطوط خیلی بلند (مثلاً > 120 کاراکتر)
        if len(line.rstrip("\n")) > 120:
            report.code_smells["Long Lines (>120 chars)"].append(f"{norm_path}:{line_num}")


def detect_monorepo_signals(report: ProjectReport) -> None:
    """تحلیل ساده برای تشخیص ساختار مونو‌ریپو."""
    frontend_markers = {"next", "react"}
    backend_markers = {"django", "fastapi", "flask", "sqlalchemy"}
    infra_markers = {"docker", "terraform"}

    deps = {
        "frontend": set(report.dependencies["frontend"]),
        "backend": set(report.dependencies["backend"]),
        "infra": set(report.dependencies["infra"]),
    }

    # سیگنال‌های خیلی ساده و تقریبی
    if deps["frontend"] and deps["backend"]:
        report.monorepo_signals.append("ترکیب فرانت‌اند و بک‌اند در یک ریپو شناسایی شد.")
    if deps["frontend"] and deps["infra"]:
        report.monorepo_signals.append("وجود زیرساخت (Docker/Terraform) در کنار فرانت‌اند.")

    if any(marker in deps["frontend"] for marker in frontend_markers) and any(
        marker in deps["backend"] for marker in backend_markers
    ):
        report.monorepo_signals.append(
            "ترکیب Frontend (React/Next) و Backend (Django/FastAPI/...) در یک ریپو محتمل است."
        )


# ==============================
# تابع اصلی تحلیل پروژه
# ==============================

def analyze_project(root_dir: str = ".") -> ProjectReport:
    report = ProjectReport(root_dir=root_dir)

    print("در حال اسکن پروژه... لطفاً صبر کنید.")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # فیلتر کردن پوشه‌ها
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for file in filenames:
            if file in IGNORE_FILES:
                continue

            filepath = os.path.join(dirpath, file)
            ext = os.path.splitext(file)[1].lower()

            # شمارش نوع فایل‌ها
            if ext:
                report.file_types[ext] += 1
                report.total_files += 1

            # شناسایی فایل‌های بزرگ
            detect_large_file(filepath, report)

            # وابستگی‌ها
            if file == "package.json":
                analyze_package_json(filepath, report)

            elif file in {"requirements.txt", "Pipfile", "pyproject.toml"}:
                analyze_python_deps(filepath, report)

            # زیرساخت / CI
            analyze_infra_files(filepath, report)

            # تحلیل فایل‌های کد
            if ext in CODE_EXTENSIONS:
                analyze_code_file(filepath, ext, report)

    # تحلیل کلی برای ساختار مونو‌ریپو
    detect_monorepo_signals(report)

    return report


# ==============================
# تولید گزارش Markdown
# ==============================

def generate_markdown_report(report: ProjectReport, output_file: str = "project_analysis.md") -> None:
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# گزارش آنالیز خودکار پروژه\n\n")
        f.write(f"- ریشه پروژه: `{normalize_path(os.path.abspath(report.root_dir))}`\n\n")

        # آمار کلی
        f.write("## 📊 آمار کلی\n")
        f.write(f"- **تعداد کل فایل‌ها:** {report.total_files}\n")
        f.write(f"- **تعداد کل خطوط کد:** {report.total_lines_of_code:,}\n\n")

        # توزیع فرمت‌ها
        f.write("## 🛠 تکنولوژی‌ها و توزیع فرمت فایل‌ها\n")
        if report.file_types:
            f.write("### توزیع فرمت فایل‌ها (۱۰ مورد پرتکرار):\n")
            for ext, count in sorted(
                report.file_types.items(), key=lambda x: x[1], reverse=True
            )[:10]:
                f.write(f"- `{ext}`: {count} فایل\n")
        else:
            f.write("- هیچ فایل قابل تحلیلی یافت نشد.\n")

        # وابستگی‌ها
        if report.dependencies["frontend"]:
            unique_frontend = sorted(set(report.dependencies["frontend"]))
            f.write("\n### وابستگی‌های فرانت‌اند / Node.js (نمونه):\n")
            f.write(", ".join(unique_frontend[:20]))
            if len(unique_frontend) > 20:
                f.write(f" ... و {len(unique_frontend) - 20} وابستگی دیگر\n")

        if report.dependencies["backend"]:
            unique_backend = sorted(set(report.dependencies["backend"]))
            f.write("\n### وابستگی‌های بک‌اند (نمونه):\n")
            f.write(", ".join(unique_backend[:20]))
            if len(unique_backend) > 20:
                f.write(f" ... و {len(unique_backend) - 20} وابستگی دیگر\n")

        if report.dependencies["infra"]:
            unique_infra = sorted(set(report.dependencies["infra"]))
            f.write("\n### ابزارهای زیرساختی شناسایی‌شده:\n")
            f.write(", ".join(unique_infra) + "\n")

        # یادداشت‌های معماری
        f.write("\n## 🏗 یادداشت‌های معماری\n")
        notes = sorted(set(report.architecture_notes))
        if notes:
            for note in notes:
                f.write(f"- {note}\n")
        else:
            f.write("- نکته معماری خاصی شناسایی نشد.\n")

        # ساختار مونو‌ریپو
        if report.monorepo_signals:
            f.write("\n## 🧩 نشانه‌های ساختار مونو‌ریپو\n")
            for sig in report.monorepo_signals:
                f.write(f"- {sig}\n")

        # فایل‌های بزرگ
        if report.large_files:
            f.write("\n## 📦 فایل‌های بزرگ (بیش از ۲ مگابایت)\n")
            for path, size in sorted(report.large_files, key=lambda x: x[1], reverse=True)[:20]:
                size_mb = size / (1024 * 1024)
                f.write(f"- `{path}`: {size_mb:.2f} MB\n")
            if len(report.large_files) > 20:
                f.write(f"- ... و {len(report.large_files) - 20} فایل بزرگ دیگر\n")

        # Code Smells
        f.write("\n## ⚠️ نقاط ضعف کد (Code Smells)\n")
        if not report.code_smells:
            f.write("- مورد قابل‌ذکری یافت نشد.\n")
        else:
            for smell_type, locations in report.code_smells.items():
                f.write(f"### {smell_type} ({len(locations)} مورد)\n")
                for loc in locations[:15]:
                    f.write(f"- {loc}\n")
                if len(locations) > 15:
                    f.write(f"- *... و {len(locations) - 15} مورد دیگر*\n")
                f.write("\n")

    print(f"✅ گزارش Markdown با موفقیت در فایل '{output_file}' ذخیره شد.")


# ==============================
# تولید گزارش JSON برای استفاده ماشینی / چندزبانه
# ==============================

def generate_json_report(report: ProjectReport, output_file: str = "project_analysis.json") -> None:
    """تولید نسخه JSON از گزارش برای استفاده در داشبورد، API، یا i18n."""
    data: Dict[str, Any] = {
        "root_dir": os.path.abspath(report.root_dir),
        "total_files": report.total_files,
        "total_lines_of_code": report.total_lines_of_code,
        "file_types": dict(report.file_types),
        "dependencies": {
            k: sorted(set(v)) for k, v in report.dependencies.items()
        },
        "code_smells": {k: v for k, v in report.code_smells.items()},
        "architecture_notes": sorted(set(report.architecture_notes)),
        "large_files": [
            {"path": path, "size_bytes": size} for path, size in report.large_files
        ],
        "monorepo_signals": report.monorepo_signals,
    }

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ گزارش JSON با موفقیت در فایل '{output_file}' ذخیره شد.")


# ==============================
# نقطه شروع اسکریپت
# ==============================

if __name__ == "__main__":
    ROOT = "."
    result = analyze_project(ROOT)
    generate_markdown_report(result, "project_analysis.md")
    generate_json_report(result, "project_analysis.json")
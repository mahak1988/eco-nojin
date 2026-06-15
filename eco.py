#!/usr/bin/env python3
"""
تحلیل‌گر حرفه‌ای پروژه (نسخه ۲)
- تنها فایل‌های اصلی (حذف پوشه‌های زائد)
- سنجش کیفیت کد (طول خط، اسرار، TODO)
- تفسیر معماری پروژه و ذخیره گزارش Markdown
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

# ------------------------------
# تنظیمات
# ------------------------------
# پوشه‌هایی که کلاً نادیده گرفته می‌شوند (حتی زیرشاخه‌هایشان)
FULL_IGNORE_DIRS = {
    # مدیریت بسته‌ها و کش
    ".pnpm-store", "node_modules", ".next", ".turbo", "__pycache__",
    ".venv", "venv", ".mypy_cache", ".pytest_cache", ".tox",
    # خروجی و داده‌های حجیم
    "output", "models", "data", "uploads",
    # نسخه‌های پشتیبان و قرنطینه
    "_QUARANTINE", "_backup_*", "backups", "local_backups",
    "redundant_backups", "zzz_legacy_*", "temp_reports",
    # Docker و زیرساخت (در صورت نیاز)
    ".git", ".github", "infrastructure", "docker", "infra",
    # گزارش‌ها و مستندات قدیمی (اختیاری)
    "analysis_reports", "structure_reports", "reports",
}

# پسوند فایل‌هایی که به عنوان کد منبع تحلیل می‌شوند
SOURCE_EXTENSIONS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs",
    ".sol", ".css", ".scss", ".less",
    ".html", ".htm", ".md", ".mdx",
    ".json", ".yaml", ".yml", ".toml", ".xml",
    ".sh", ".bash", ".ps1", ".sql", ".tf", ".hcl",
}

# الگوی جستجوی TODO/FIXME
TODO_PATTERN = re.compile(
    r'(TODO|FIXME|HACK|XXX|OPTIMIZE|BUG|WORKAROUND)(\b|[:]|[\s\-])',
    re.IGNORECASE
)

# الگوی تقریبی اسرار سخت‌افزاری (در کد)
SECRET_PATTERNS = [
    re.compile(r'(password|passwd|secret|token|api_key|apikey|auth_key)\s*[:=]\s*["\'][^"\'\s]{8,}', re.IGNORECASE),
    re.compile(r'["\'](password|secret|token)["\']\s*[:=]\s*["\']\S+["\']', re.IGNORECASE),
]

MAX_LINE_LENGTH = 120

# ------------------------------
# کمک‌ها
# ------------------------------
def should_ignore_dir(dirname: str) -> bool:
    """بررسی اینکه نام پوشه در لیست نادیده‌گرفته‌شده باشد (پشتیبانی از wildcard با *)"""
    for pattern in FULL_IGNORE_DIRS:
        if pattern.endswith("*"):
            if dirname.startswith(pattern[:-1]):
                return True
        else:
            if dirname == pattern:
                return True
    return False


def is_source_file(filepath: Path) -> bool:
    """فایل‌هایی که پسوند آن‌ها در لیست SOURCE_EXTENSIONS باشد."""
    return filepath.suffix.lower() in SOURCE_EXTENSIONS


def count_lines(path: Path):
    """شمارش خطوط کل، خالی و طول خطوط کد برای یک فایل متنی."""
    total = 0
    blank = 0
    long_lines = 0
    line_lengths = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for raw_line in f:
                total += 1
                line = raw_line.rstrip('\n\r')
                if not line.strip():
                    blank += 1
                else:
                    line_len = len(line)
                    line_lengths.append(line_len)
                    if line_len > MAX_LINE_LENGTH:
                        long_lines += 1
    except Exception:
        pass
    avg_line_len = (sum(line_lengths) / len(line_lengths)) if line_lengths else 0
    return total, blank, long_lines, avg_line_len


def search_todos(path: Path) -> int:
    """تعداد TODO/FIXME در فایل."""
    count = 0
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if TODO_PATTERN.search(line):
                    count += 1
    except Exception:
        pass
    return count


def search_secrets(path: Path) -> list:
    """بررسی الگوهای اسرار و بازگرداندن خطوط مشکوک."""
    findings = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            for idx, line in enumerate(lines, start=1):
                for pat in SECRET_PATTERNS:
                    if pat.search(line):
                        findings.append((idx, line.strip()))
                        break
    except Exception:
        pass
    return findings


# ------------------------------
# تحلیل‌گر اصلی
# ------------------------------
class ProjectAnalyzerV2:
    def __init__(self, root_path):
        self.root = Path(root_path).resolve()
        if not self.root.is_dir():
            raise NotADirectoryError(f"مسیر پوشه نیست: {self.root}")

        # فیلتر پوشه‌های سطح بالا برای نمایش ساختار درختی ساده
        self.top_level_items = []

        # داده‌های جمع‌آوری‌شده
        self.files = []               # Path
        self.ext_counter = Counter()
        self.lang_stats = defaultdict(lambda: {
            "files": 0, "total": 0, "blank": 0, "code": 0
        })
        self.large_files = []         # (path, size)
        self.todo_files = Counter()
        self.secret_files = []        # (path, list of (line, content))
        self.quality_issues = []      # (path, issue description)
        self.module_summary = {}      # مسیر → نقش

        self.total_files = 0
        self.total_source_files = 0

    def collect_and_analyze(self):
        """پیمایش هوشمند: رد شدن از پوشه‌های ناخواسته و جمع‌آوری فایل‌ها."""
        print(f"🔍 شروع تحلیل هوشمند: {self.root}")

        for dirpath, dirnames, filenames in os.walk(self.root, topdown=True):
            # فیلتر کردن پوشه‌های جاری
            dirnames[:] = [
                d for d in dirnames if not should_ignore_dir(d)
            ]

            for fname in filenames:
                full_path = Path(dirpath) / fname
                if not full_path.is_file():
                    continue
                self.files.append(full_path)

        print(f"📁 کل فایل‌های اصلی پیدا شده: {len(self.files)}")
        print("📊 تحلیل فایل‌ها...")

        for idx, fpath in enumerate(self.files, start=1):
            if idx % 200 == 0:
                print(f"   ... {idx}/{len(self.files)}")

            # آمار پایه
            ext = fpath.suffix.lower()
            self.ext_counter[ext] += 1

            is_src = is_source_file(fpath)

            if is_src:
                self.total_source_files += 1
                total, blank, long_lines, avg_len = count_lines(fpath)
                self.lang_stats[ext]["files"] += 1
                self.lang_stats[ext]["total"] += total
                self.lang_stats[ext]["blank"] += blank
                self.lang_stats[ext]["code"] += (total - blank)

                # کیفیت
                if long_lines > 0:
                    self.quality_issues.append(
                        (fpath, f"⚠️ {long_lines} خط بلندتر از {MAX_LINE_LENGTH} کاراکتر")
                    )

                # بررسی اسرار
                secrets = search_secrets(fpath)
                if secrets:
                    self.secret_files.append((fpath, secrets))
                    self.quality_issues.append(
                        (fpath, f"🔐 الگوی اسرار سخت‌افزاری در {len(secrets)} خط")
                    )

                # TODO
                todo_count = search_todos(fpath)
                if todo_count > 0:
                    self.todo_files[str(fpath)] = todo_count

                # فایل‌های بزرگ (>1000 خط کد)
                if total - blank > 1000:
                    self.large_files.append((fpath, total - blank))
            # فایل‌های غیرمنبع (مانند تصاویر) را نادیده می‌گیریم

        # مرتب‌سازی
        self.large_files.sort(key=lambda x: x[1], reverse=True)

    def generate_summary(self):
        """تفسیر ساختار پروژه با نگاه به پوشه‌های اصلی."""
        entries = list(self.root.iterdir())
        self.top_level_items = [e.name for e in entries if e.is_dir() and not should_ignore_dir(e.name)]

        summary = []
        # تشخیص نوع پروژه
        if "api" in self.top_level_items or "apps/api" in str(self.root):
            summary.append("• **backend (Python/FastAPI)**")
        if "apps/web" in self.top_level_items:
            summary.append("• **frontend (Next.js/React)**")
        if "contracts" in self.top_level_items:
            summary.append("• **قراردادهای هوشمند (Solidity/Hardhat)**")
        if "packages" in self.top_level_items:
            summary.append("• **کتابخانه‌های اشتراکی (monorepo)**")
        if "agents" in self.top_level_items:
            summary.append("• **عامل‌های هوش مصنوعی (AI agents)**")
        if "models" in self.top_level_items:
            summary.append("• **مدل‌های یادگیری ماشین (ML models)**")
        if "docs" in self.top_level_items:
            summary.append("• **مستندات**")
        if not summary:
            summary.append("• پروژه عمومی (بدون ساختار مشخص)")

        # تشخیص ابزارهای مورد استفاده
        tools = []
        if (self.root / "pnpm-lock.yaml").exists():
            tools.append("pnpm")
        if (self.root / "package.json").exists():
            tools.append("Node.js")
        if (self.root / "pyproject.toml").exists() or (self.root / "setup.py").exists():
            tools.append("Python/pip")
        if (self.root / "foundry.toml").exists() or (self.root / "hardhat.config.js").exists():
            tools.append("Solidity/Foundry")
        if (self.root / "docker-compose.yml").exists():
            tools.append("Docker Compose")

        self.module_summary["اجزای اصلی"] = summary
        self.module_summary["ابزارها"] = tools if tools else ["نامشخص"]

    def write_report(self, output_path):
        """نوشتن گزارش جامع به فرمت Markdown."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report = []
        report.append(f"# 📊 تحلیل هوشمند پروژه\n")
        report.append(f"**مسیر:** `{self.root}`  ")
        report.append(f"**تاریخ:** {now}  ")
        report.append(f"**فایل‌های اصلی بررسی‌شده:** {len(self.files)} (منبع: {self.total_source_files})  \n")

        # ---------------------------
        # تفسیر معماری
        # ---------------------------
        report.append("## 🏗️ تفسیر معماری پروژه\n")
        report.append("### اجزای اصلی\n")
        for line in self.module_summary.get("اجزای اصلی", []):
            report.append(f"{line}  ")
        report.append("\n### ابزارهای کلیدی\n")
        for tool in self.module_summary.get("ابزارها", []):
            report.append(f"- {tool}  ")

        # ---------------------------
        # توزیع پسوندها
        # ---------------------------
        report.append("\n## 📁 توزیع پسوند فایل‌ها (کد منبع)\n")
        report.append("| پسوند | تعداد فایل |")
        report.append("|-------|------------|")
        for ext, cnt in self.ext_counter.most_common():
            if ext in SOURCE_EXTENSIONS:
                report.append(f"| {ext} | {cnt} |")
        report.append("")

        # ---------------------------
        # آمار خطوط
        # ---------------------------
        report.append("## 📏 آمار خطوط کد (فقط فایل‌های منبع)\n")
        report.append("| پسوند | تعداد فایل | کل خطوط | خطوط خالی | خطوط کد |")
        report.append("|--------|------------|----------|------------|----------|")
        total_code_all = 0
        for ext, stats in sorted(self.lang_stats.items(), key=lambda x: x[1]["code"], reverse=True):
            report.append(f"| {ext} | {stats['files']} | {stats['total']} | {stats['blank']} | {stats['code']} |")
            total_code_all += stats['code']
        report.append(f"| **مجموع** | **{self.total_source_files}** | ... | ... | **{total_code_all}** |\n")

        # ---------------------------
        # فایل‌های حجیم (از نظر خطوط کد)
        # ---------------------------
        if self.large_files:
            report.append(f"## 🐘 ۱۰ فایل پرخط کد (بیش از ۱۰۰۰ خط)\n")
            report.append("| رتبه | مسیر نسبی | خطوط کد |")
            report.append("|------|-----------|---------|")
            for rank, (fpath, lines) in enumerate(self.large_files[:10], 1):
                rel = fpath.relative_to(self.root)
                report.append(f"| {rank} | `{rel}` | {lines} |")
            report.append("")

        # ---------------------------
        # مشکلات کیفیت
        # ---------------------------
        if self.quality_issues:
            report.append(f"## 🚨 مشکلات کیفیت کد\n")
            report.append(f"| مسیر نسبی | شرح مشکل |")
            report.append(f"|-----------|-----------|")
            for fpath, desc in self.quality_issues[:30]:  # حداکثر ۳۰ مورد
                rel = fpath.relative_to(self.root)
                report.append(f"| `{rel}` | {desc} |")
            report.append("")

        # TODO
        if self.todo_files:
            report.append(f"## 📝 TODO/FIXME های پرتعداد (فقط فایل‌های اصلی)\n")
            report.append("| فایل | تعداد |")
            report.append("|------|-------|")
            for fname, cnt in self.todo_files.most_common(15):
                rel = Path(fname).relative_to(self.root)
                report.append(f"| `{rel}` | {cnt} |")
            report.append("")

        # اسرار
        if self.secret_files:
            report.append(f"## 🔐 هشدار امنیتی: الگوهای شبیه اسرار\n")
            report.append("| فایل | خط | محتوا (خلاصه) |")
            report.append("|------|-----|----------------|")
            for fpath, secrets in self.secret_files[:20]:
                rel = fpath.relative_to(self.root)
                for line_no, line_text in secrets[:3]:  # حداکثر ۳ خط از هر فایل
                    # خلاصه‌سازی محتوا
                    if len(line_text) > 60:
                        line_text = line_text[:57] + "..."
                    report.append(f"| `{rel}` | {line_no} | `{line_text}` |")
            report.append("")

        # ---------------------------
        # خلاصه نهایی
        # ---------------------------
        report.append("## 📌 خلاصه\n")
        report.append(f"- **کل فایل‌های اصلی:** {len(self.files)}")
        report.append(f"- **فایل‌های کد منبع:** {self.total_source_files}")
        report.append(f"- **کل خطوط کد خالص:** {total_code_all}")
        report.append(f"- **فایل‌های بزرگ (>۱۰۰۰ خط):** {len(self.large_files)}")
        report.append(f"- **مشکلات کیفیت شناسایی‌شده:** {len(self.quality_issues)}")
        report.append(f"- **هشدارهای امنیتی:** {len(self.secret_files)}")
        report.append(f"- **تعداد TODO/FIXME:** {sum(self.todo_files.values())}")

        # نوشتن در فایل
        content = "\n".join(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"\n✅ گزارش با موفقیت در {output_path} ذخیره شد.")


# ------------------------------
# ورودی
# ------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="تحلیل‌گر پروژه نسخه ۲ - تحلیل فایل‌های اصلی، کیفیت کد و تفسیر معماری"
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="مسیر پوشه پروژه (پیش‌فرض: دایرکتوری جاری)"
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="مسیر فایل خروجی Markdown (پیش‌فرض: project_insight_<timestamp>.md)"
    )
    args = parser.parse_args()

    try:
        analyzer = ProjectAnalyzerV2(args.project)
    except NotADirectoryError as e:
        print(f"❌ خطا: {e}")
        return

    analyzer.collect_and_analyze()
    analyzer.generate_summary()

    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = analyzer.root / f"project_insight_{timestamp}.md"
    else:
        output_path = Path(args.output)

    analyzer.write_report(output_path)


if __name__ == "__main__":
    main()
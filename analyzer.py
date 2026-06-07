import os
import json
import re
from collections import defaultdict

# لیست پوشه‌هایی که باید نادیده گرفته شوند
IGNORE_DIRS = {'.git', 'node_modules', 'venv', 'env', '__pycache__', 'build', 'dist', '.next', 'coverage'}
# لیست فایل‌هایی که باید نادیده گرفته شوند
IGNORE_FILES = {'.DS_Store', 'package-lock.json', 'yarn.lock', 'Pipfile.lock'}

def analyze_project(root_dir='.'):
    report = {
        "total_files": 0,
        "file_types": defaultdict(int),
        "total_lines_of_code": 0,
        "dependencies": {"frontend": [], "backend": []},
        "code_smells": defaultdict(list),
        "architecture_notes": []
    }

    print("در حال اسکن پروژه... لطفاً صبر کنید.")

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # حذف پوشه‌های نادیده گرفته شونده از اسکن
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for file in filenames:
            if file in IGNORE_FILES:
                continue

            filepath = os.path.join(dirpath, file)
            ext = os.path.splitext(file)[1].lower()
            
            if ext:
                report["file_types"][ext] += 1
                report["total_files"] += 1

            # آنالیز وابستگی‌ها
            if file == 'package.json':
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        deps = list(data.get('dependencies', {}).keys()) + list(data.get('devDependencies', {}).keys())
                        report["dependencies"]["frontend"].extend(deps)
                        report["architecture_notes"].append("پروژه فرانت‌اند/Node.js شناسایی شد (package.json).")
                except Exception:
                    pass
            
            elif file in ['requirements.txt', 'Pipfile', 'pyproject.toml']:
                report["architecture_notes"].append("پروژه بک‌اند پایتون شناسایی شد.")
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = [line.split('==')[0].strip() for line in f if line.strip() and not line.startswith('#')]
                        report["dependencies"]["backend"].extend(lines)
                except Exception:
                    pass

            # آنالیز محتوای فایل‌های کد برای پیدا کردن Code Smells
            if ext in ['.js', '.jsx', '.ts', '.tsx', '.py', '.html', '.css', '.vue', '.svelte']:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        report["total_lines_of_code"] += len(lines)
                        
                        for line_num, line in enumerate(lines, 1):
                            # جستجوی TODO و FIXME
                            if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line, re.IGNORECASE):
                                report["code_smells"]["TODOs/FIXMEs"].append(f"{filepath}:{line_num}")
                            
                            # جستجوی console.log در فرانت‌اند
                            if ext in ['.js', '.jsx', '.ts', '.tsx'] and 'console.log' in line:
                                report["code_smells"]["Console Logs"].append(f"{filepath}:{line_num}")
                                
                            # جستجوی print در بک‌اند پایتون
                            if ext == '.py' and re.search(r'\bprint\s*\(', line):
                                report["code_smells"]["Print Statements"].append(f"{filepath}:{line_num}")

                except UnicodeDecodeError:
                    pass # رد کردن فایل‌های باینری

    return report

def generate_markdown_report(report, output_file="project_analysis.md"):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# گزارش آنالیز خودکار پروژه\n\n")
        
        f.write("## 📊 آمار کلی\n")
        f.write(f"- **تعداد کل فایل‌ها:** {report['total_files']}\n")
        f.write(f"- **تعداد کل خطوط کد:** {report['total_lines_of_code']:,}\n\n")
        
        f.write("## 🛠 تکنولوژی‌ها و وابستگی‌ها\n")
        f.write("### توزیع فرمت فایل‌ها:\n")
        for ext, count in sorted(report['file_types'].items(), key=lambda x: x[1], reverse=True)[:10]:
            f.write(f"- `{ext}`: {count} فایل\n")
        
        if report['dependencies']['frontend']:
            f.write("\n### وابستگی‌های فرانت‌اند/Node (نمونه):\n")
            f.write(", ".join(report['dependencies']['frontend'][:15]) + "...\n")
            
        if report['dependencies']['backend']:
            f.write("\n### وابستگی‌های بک‌اند (نمونه):\n")
            f.write(", ".join(report['dependencies']['backend'][:15]) + "...\n")

        f.write("\n## 🏗 یادداشت‌های معماری\n")
        for note in set(report['architecture_notes']):
            f.write(f"- {note}\n")

        f.write("\n## ⚠️ نقاط ضعف کد (Code Smells)\n")
        for smell_type, locations in report['code_smells'].items():
            f.write(f"### {smell_type} ({len(locations)} مورد)\n")
            for loc in locations[:10]: # نمایش حداکثر ۱۰ مورد برای جلوگیری از شلوغی
                f.write(f"- {loc}\n")
            if len(locations) > 10:
                f.write(f"- *... و {len(locations) - 10} مورد دیگر*\n")
            f.write("\n")

    print(f"✅ گزارش با موفقیت در فایل '{output_file}' ذخیره شد.")

if __name__ == "__main__":
    # اجرای آنالیز
    result = analyze_project('.')
    # تولید گزارش
    generate_markdown_report(result)
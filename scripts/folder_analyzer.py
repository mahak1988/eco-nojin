import os
import sys
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime

class FolderStructureAnalyzer:
    # لیست پوشه‌هایی که باید نادیده گرفته شوند (حجیم یا غیرمفید)
    IGNORE_FOLDERS = {
        'node_modules', 'venv', 'env', '.venv', '.env', 'virtualenv',
        '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
        '.git', '.svn', '.hg',
        'build', 'dist', 'target', 'out', 'bin', 'obj',
        '.next', '.nuxt', '.svelte-kit',
        'coverage', '.nyc_output',
        '.idea', '.vscode', '.vs',
        'temp', 'tmp', 'cache',
        'reports',  # پوشه گزارش‌های خودمان
    }
    
    # الگوهای دسته‌بندی پوشه‌ها
    FOLDER_PATTERNS = {
        '🧪 Tests': ['test', 'tests', 'testing', 'spec', 'specs', '__tests__'],
        '📚 Documentation': ['doc', 'docs', 'documentation', 'guide', 'guides', 'wiki'],
        '⚙️ Config': ['config', 'configs', 'conf', 'settings', 'etc'],
        '🔧 Scripts': ['script', 'scripts', 'tools', 'utils', 'utilities', 'helpers'],
        '📦 Core/Source': ['core', 'src', 'source', 'lib', 'library', 'app', 'application'],
        '🌐 API': ['api', 'apis', 'rest', 'graphql', 'endpoints', 'routes'],
        '🗄️ Database': ['db', 'database', 'models', 'migrations', 'schema'],
        '🔐 Security': ['security', 'auth', 'authentication', 'permissions'],
        '🎨 Frontend/Assets': ['assets', 'static', 'public', 'frontend', 'ui', 'components', 'pages', 'views'],
        '🤖 Integrations': ['integrations', 'clients', 'services', 'adapters', 'connectors'],
        '📊 Analytics/Research': ['analytics', 'research', 'reports', 'analysis', 'ml', 'ai', 'models'],
        '🚀 DevOps/Deployment': ['devops', 'deploy', 'deployment', 'docker', 'k8s', 'ci', 'cd', 'infra'],
        '📝 Logs': ['logs', 'log'],
    }

    def __init__(self, project_path, output_file=None):
        self.project_path = Path(project_path).resolve()
        self.output_file = output_file
        self.log_buffer = []
        
        self.stats = {
            'total_folders': 0,
            'total_files': 0,
            'max_depth': 0,
            'deepest_folder': None,
            'empty_folders': [],
            'folder_categories': defaultdict(lambda: {'count': 0, 'files': 0, 'folders': []}),
            'uncategorized_folders': [],
            'file_extensions': Counter(),
            'depth_distribution': Counter(),
            'folder_size_distribution': Counter(),  # تعداد فایل در هر پوشه
            'large_folders': [],  # پوشه‌هایی با تعداد فایل زیاد
        }

    def _log(self, message=""):
        print(message)
        self.log_buffer.append(message)

    def _should_ignore(self, folder_name):
        """بررسی اینکه آیا پوشه باید نادیده گرفته شود"""
        folder_lower = folder_name.lower()
        return folder_lower in {f.lower() for f in self.IGNORE_FOLDERS} or folder_lower.startswith('.')

    def _categorize_folder(self, folder_name):
        """دسته‌بندی پوشه بر اساس نام آن"""
        folder_lower = folder_name.lower()
        for category, patterns in self.FOLDER_PATTERNS.items():
            for pattern in patterns:
                if pattern in folder_lower or folder_lower == pattern:
                    return category
        return None

    def _get_depth(self, path):
        """محاسبه عمق یک مسیر نسبت به ریشه پروژه"""
        try:
            return len(path.relative_to(self.project_path).parts)
        except ValueError:
            return 0

    def analyze(self):
        """تحلیل اصلی ساختار پوشه‌ها"""
        if not self.project_path.exists():
            self._log(f"❌ مسیر پروژه یافت نشد: {self.project_path}")
            return

        self._log(f"# 📊 گزارش تحلیل ساختار پوشه‌های پروژه")
        self._log(f"**پروژه:** `{self.project_path.name}`")
        self._log(f"**زمان اجرا:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self._log("")

        self._scan_directory(self.project_path)
        self._generate_report()
        self._save_report()

    def _scan_directory(self, current_path, depth=0):
        """پیمایش بازگشتی پوشه‌ها"""
        try:
            items = list(current_path.iterdir())
        except PermissionError:
            return

        folders = [i for i in items if i.is_dir() and not self._should_ignore(i.name)]
        files = [i for i in items if i.is_file()]
        
        # به‌روزرسانی آمار کلی
        self.stats['total_folders'] += len(folders)
        self.stats['total_files'] += len(files)
        
        # ثبت عمق
        self.stats['depth_distribution'][depth] += 1
        if depth > self.stats['max_depth']:
            self.stats['max_depth'] = depth
            self.stats['deepest_folder'] = str(current_path.relative_to(self.project_path))
        
        # بررسی پوشه خالی
        if not folders and not files and current_path != self.project_path:
            rel_path = str(current_path.relative_to(self.project_path))
            self.stats['empty_folders'].append(rel_path)
        
        # تحلیل فایل‌ها
        for file in files:
            ext = file.suffix.lower() if file.suffix else '(no extension)'
            self.stats['file_extensions'][ext] += 1
        
        # دسته‌بندی پوشه فعلی
        if current_path != self.project_path:
            folder_name = current_path.name
            category = self._categorize_folder(folder_name)
            
            if category:
                self.stats['folder_categories'][category]['count'] += 1
                self.stats['folder_categories'][category]['files'] += len(files)
                self.stats['folder_categories'][category]['folders'].append(
                    str(current_path.relative_to(self.project_path))
                )
            else:
                # اگر دسته‌بندی نشد، بر اساس مسیر کامل بررسی شود
                rel_path = str(current_path.relative_to(self.project_path))
                matched = False
                for parent in current_path.parents:
                    if parent == self.project_path:
                        break
                    parent_cat = self._categorize_folder(parent.name)
                    if parent_cat:
                        self.stats['folder_categories'][parent_cat]['count'] += 1
                        self.stats['folder_categories'][parent_cat]['files'] += len(files)
                        matched = True
                        break
                if not matched:
                    self.stats['uncategorized_folders'].append({
                        'path': rel_path,
                        'files': len(files)
                    })
        
        # ثبت توزیع اندازه پوشه‌ها
        if files:
            size_category = self._get_size_category(len(files))
            self.stats['folder_size_distribution'][size_category] += 1
            if len(files) > 20:
                self.stats['large_folders'].append({
                    'path': str(current_path.relative_to(self.project_path)),
                    'files': len(files)
                })
        
        # پیمایش بازگشتی پوشه‌های فرعی
        for folder in folders:
            self._scan_directory(folder, depth + 1)

    def _get_size_category(self, file_count):
        """دسته‌بندی پوشه بر اساس تعداد فایل"""
        if file_count == 0:
            return "خالی (0)"
        elif file_count <= 5:
            return "کوچک (1-5)"
        elif file_count <= 15:
            return "متوسط (6-15)"
        elif file_count <= 30:
            return "بزرگ (16-30)"
        else:
            return "خیلی بزرگ (30+)"

    def _generate_report(self):
        """تولید گزارش نهایی"""
        self._log("=" * 70)
        self._log("## 📈 آمار کلی ساختار")
        self._log("=" * 70)
        self._log(f"| معیار | مقدار |")
        self._log(f"|---|---|")
        self._log(f"| 📁 تعداد کل پوشه‌ها (بدون node_modules و...) | **{self.stats['total_folders']}** |")
        self._log(f"| 📄 تعداد کل فایل‌ها | **{self.stats['total_files']}** |")
        self._log(f"| 📏 حداکثر عمق درخت پوشه‌ها | **{self.stats['max_depth']}** لایه |")
        self._log(f"| 📂 عمیق‌ترین پوشه | `{self.stats['deepest_folder']}` |")
        self._log(f"| ⚠️ تعداد پوشه‌های خالی | **{len(self.stats['empty_folders'])}** |")
        
        # دسته‌بندی پوشه‌ها
        self._log("")
        self._log("=" * 70)
        self._log("## 🏷️ دسته‌بندی پوشه‌ها بر اساس نوع")
        self._log("=" * 70)
        
        sorted_categories = sorted(
            self.stats['folder_categories'].items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        for category, data in sorted_categories:
            self._log(f"\n### {category}")
            self._log(f"- **تعداد پوشه‌ها:** {data['count']}")
            self._log(f"- **تعداد کل فایل‌ها در این دسته:** {data['files']}")
            if data['folders'][:5]:
                self._log(f"- **نمونه پوشه‌ها:**")
                for folder in data['folders'][:5]:
                    self._log(f"  - `{folder}`")
                if len(data['folders']) > 5:
                    self._log(f"  - *... و {len(data['folders']) - 5} پوشه دیگر*")
        
        # پوشه‌های دسته‌بندی نشده
        if self.stats['uncategorized_folders']:
            self._log(f"\n### ❓ پوشه‌های دسته‌بندی نشده ({len(self.stats['uncategorized_folders'])} پوشه)")
            for item in self.stats['uncategorized_folders'][:10]:
                self._log(f"- `{item['path']}` ({item['files']} فایل)")
        
        # تحلیل عمق
        self._log("")
        self._log("=" * 70)
        self._log("## 📊 توزیع عمق پوشه‌ها")
        self._log("=" * 70)
        for depth in sorted(self.stats['depth_distribution'].keys()):
            count = self.stats['depth_distribution'][depth]
            bar = '█' * min(count, 50)
            self._log(f"- عمق {depth}: {count} پوشه {bar}")
        
        # پوشه‌های خالی
        if self.stats['empty_folders']:
            self._log("")
            self._log("=" * 70)
            self._log("## ⚠️ پوشه‌های خالی (نیاز به بررسی)")
            self._log("=" * 70)
            for folder in self.stats['empty_folders'][:15]:
                self._log(f"- `{folder}`")
            if len(self.stats['empty_folders']) > 15:
                self._log(f"- *... و {len(self.stats['empty_folders']) - 15} پوشه خالی دیگر*")
        
        # پوشه‌های حجیم
        if self.stats['large_folders']:
            self._log("")
            self._log("=" * 70)
            self._log("## 📦 پوشه‌های با تعداد فایل زیاد (> 20 فایل)")
            self._log("=" * 70)
            sorted_large = sorted(self.stats['large_folders'], key=lambda x: x['files'], reverse=True)
            for folder in sorted_large[:10]:
                self._log(f"- `{folder['path']}` - **{folder['files']} فایل**")
        
        # توزیع پسوندهای فایل
        self._log("")
        self._log("=" * 70)
        self._log("## 📋 توزیع انواع فایل‌ها در پروژه")
        self._log("=" * 70)
        sorted_extensions = self.stats['file_extensions'].most_common(15)
        for ext, count in sorted_extensions:
            percentage = (count / self.stats['total_files'] * 100) if self.stats['total_files'] > 0 else 0
            bar = '█' * int(percentage / 2)
            self._log(f"- `{ext}` : **{count}** فایل ({percentage:.1f}%) {bar}")
        
        # توصیه‌ها
        self._log("")
        self._log("=" * 70)
        self._log("## 💡 توصیه‌های ساختاری")
        self._log("=" * 70)
        
        recommendations = []
        if len(self.stats['empty_folders']) > 5:
            recommendations.append(f"- 🧹 **پاکسازی:** {len(self.stats['empty_folders'])} پوشه خالی وجود دارد که می‌توان حذف کرد.")
        if self.stats['max_depth'] > 7:
            recommendations.append(f"- 📐 **بازسازی:** عمق ساختار ({self.stats['max_depth']} لایه) زیاد است. پیشنهاد می‌شود ساختار را مسطح‌تر کنید.")
        if len(self.stats['uncategorized_folders']) > 10:
            recommendations.append(f"- 🏷️ **سازماندهی:** {len(self.stats['uncategorized_folders'])} پوشه بدون دسته‌بندی مشخص وجود دارد. بررسی ساختار نام‌گذاری توصیه می‌شود.")
        
        large_folder_count = sum(1 for x in self.stats['large_folders'] if x['files'] > 50)
        if large_folder_count > 0:
            recommendations.append(f"- 📦 **تفکیک:** {large_folder_count} پوشه با بیش از ۵۰ فایل وجود دارد. پیشنهاد می‌شود آن‌ها را به زیرپوشه‌های کوچک‌تر تقسیم کنید.")
        
        if not recommendations:
            recommendations.append("- ✅ ساختار پروژه منظم و استاندارد به نظر می‌رسد!")
        
        for rec in recommendations:
            self._log(rec)

    def _save_report(self):
        """ذخیره گزارش در فایل"""
        if self.output_file is None:
            reports_dir = self.project_path / 'structure_reports'
            reports_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_file = reports_dir / f"folder_structure_{timestamp}.md"
        else:
            self.output_file = Path(self.output_file)
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.log_buffer))
            print(f"\n✅ گزارش در فایل زیر ذخیره شد:")
            print(f"📄 {self.output_file.resolve()}")
        except Exception as e:
            print(f"❌ خطا در ذخیره گزارش: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="تحلیلگر ساختار پوشه‌های پروژه (بدون اسکن node_modules و...)"
    )
    parser.add_argument('project_path', nargs='?', default='.', 
                       help='مسیر ریشه پروژه (پیش‌فرض: مسیر فعلی)')
    parser.add_argument('-o', '--output', 
                       help='مسیر فایل خروجی گزارش')
    args = parser.parse_args()
    
    print("🔍 در حال تحلیل ساختار پوشه‌ها...")
    print("⏭️  پوشه‌های حجیم (node_modules, venv, ...) نادیده گرفته می‌شوند.\n")
    
    analyzer = FolderStructureAnalyzer(args.project_path, args.output)
    analyzer.analyze()
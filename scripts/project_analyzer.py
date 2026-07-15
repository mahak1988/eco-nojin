#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
  Project Analyzer v1.2.0 - تحلیلگر جامع پروژه
  سازنده: Super Z (Z.ai)
============================================================

اسکریپت پایتون مستقل برای تحلیل پروژه‌های نرم‌افزاری

تغییرات نسخه 1.2.0:
  + عدم اسکن گزارش‌های قبلی خود اسکریپت (analysis_reports/)
  + نادیده گرفتن پوشه‌های _COLD_STORAGE و models (آرشیو و مدل‌های ML)
  + کاهش False Positive در "Hardcoded Token" (تشخیص اسم کلید از توکن واقعی)
  + کاهش False Positive در "Suspicious TODO" (فقط داخل کامنت‌های واقعی)
  + کاهش False Positive در "AWS Secret Key" (فقط رشته‌های داخل کوتیشن)
  + خواندن package.json از تمام زیرپوشه‌ها (نه فقط ریشه)

تغییرات نسخه 1.1.0:
  + تشخیص هوشمند پوشه‌های پشتیبان (.cleanup_backup, apps_backup_*, etc.)
  + نادیده گرفتن .pnpm-store, .venv-1, .venv-2 و سایر محیط‌های مجازی
  + کاهش False Positive در تشخیص AWS Secret Key
  + نمایش پوشه‌های نادیده گرفته شده در گزارش

نحوه اجرا:
  python project_analyzer.py
  python project_analyzer.py D:\\my-project
  python project_analyzer.py "D:/econojin.com" --output ./reports

نیاز به نصب هیچ کتابخانه خارجی ندارد!
فقط پایتون 3.6+ نیاز است.

خروجی‌ها:
  - گزارش کنسول رنگی
  - فایل گزارش متنی (TXT)
  - فایل گزارش JSON
  - گزارش HTML (اختیاری)

بخش‌های تحلیل:
  ۱. ساختار فایل
  ۲. کیفیت کد
  ۳. امنیت
  ۴. معماری
  ۵. کتابخانه‌ها
  ۶. بک‌اند / فرانت‌اند
"""

import os
import sys
import re
import json
import time
import hashlib
import argparse
import platform
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter


# ============================================================
#  تنظیمات رنگ برای خروجی کنسول
# ============================================================
class Color:
    RESET    = "\033[0m"
    BOLD     = "\033[1m"
    RED      = "\033[91m"
    GREEN    = "\033[92m"
    YELLOW   = "\033[93m"
    BLUE     = "\033[94m"
    MAGENTA  = "\033[95m"
    CYAN     = "\033[96m"
    GRAY     = "\033[90m"
    WHITE    = "\033[97m"

    @staticmethod
    def enable_windows():
        """فعال‌سازی ANSI colors در ویندوز."""
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except:
                pass

    @staticmethod
    def disable():
        for attr in dir(Color):
            if attr.isupper():
                setattr(Color, attr, "")


# ============================================================
#  تنظیمات پیش‌فرض
# ============================================================

# پوشه‌های نادیده گرفته شده (نام دقیق)
IGNORE_DIRS = {
    # Build & dependencies
    'node_modules', '.git', '__pycache__', '.next', '.nuxt', 'dist',
    'build', '.cache', '.pytest_cache', '.mypy_cache', '.tox',
    '.venv', 'venv', 'env', '.env', '.idea', '.vscode', 'coverage',
    '.gradle', 'target', 'bin', 'obj', '.angular', '.svelte-kit',
    'vendor', 'bower_components', '.turbo', '.parcel-cache',
    'out', '.output', 'tmp', 'temp', 'logs', 'log',
    # Package stores & caches
    '.pnpm-store', '.yarn', '.pnpm', '.cache-loader',
    # Editor / OS
    '.DS_Store',
    # Self-output (گزارش‌های قبلی خود اسکریپت)
    'analysis_reports',
    # ML models / binaries (مدل‌های ML و فایل‌های باینری بزرگ)
    'models', 'model', 'weights', 'checkpoints',
    # Archive / cold storage
    '_COLD_STORAGE', 'cold_storage', 'archive',
}

# الگوی نام پوشه‌ها که باید نادیده گرفته شوند (با regex)
IGNORE_DIR_PATTERNS = [
    r'^\..*backup.*$',          # .cleanup_backup, .migration_backup
    r'^.*_backup.*$',            # apps_backup_20260711_*
    r'^backup.*$',               # backup_xxx
    r'^.*_QUARANTINE.*$',        # _QUARANTINE
    r'^redundant_backups$',      # redundant_backups
    r'^.*_archive$',             # _legacy_frontends_archive
    r'^\.venv.*$',               # .venv-1, .venv-2
    r'^venv.*$',                 # venv-1, venv-2
    r'^env.*$',                  # env-1, env-2
    r'^\.tmp.*$',                # .tmp
    r'^temp_.*$',                # temp_xxx
    r'^.*_temp$',                # xxx_temp
    r'^\.old.*$',                # .old, .old_xxx
    r'^.*\.bak$',                # xxx.bak
    r'^.*~$',                    # xxx~ (backup files)
    r'^__pycache__.*$',
]

IGNORE_FILES = {
    '.DS_Store', 'Thumbs.db', '.gitignore', '.npmrc', '.yarnrc',
    'yarn.lock', 'package-lock.json', 'pnpm-lock.yaml', 'Pipfile.lock',
    'poetry.lock', 'composer.lock', 'Cargo.lock', 'go.sum',
    # Self-output files
    'report.json', 'files.txt',
}

# الگوی نام فایل‌هایی که باید نادیده گرفته شوند (با regex)
IGNORE_FILE_PATTERNS = [
    r'^project_analysis.*\.(json|txt|html)$',
    r'^.*_analysis.*\.(json|txt|html)$',
    r'^apps_analyzer.*\.py$',
    r'^deep_secret_scanner.*\.py$',
    r'^dependency_analyzer.*\.py$',
    r'^project_analyzer.*\.py$',
    r'^analyze_project.*\.py$',
    r'^.*\.safetensors$',
    r'^.*\.tar\.gz$',
    r'^.*\.tar$',
    r'^.*\.zip$',
    r'^.*\.7z$',
    r'^.*\.rar$',
    r'^.*\.exe$',
    r'^.*\.dll$',
    r'^.*\.so$',
    r'^.*\.dylib$',
    r'^.*\.nc$',
    r'^.*\.db$',
    r'^.*\.sqlite$',
    r'^.*\.sqlite3$',
]

# پسوندهای فایل‌های کد به تفکیک زبان
CODE_EXTENSIONS = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.jsx': 'JavaScript (React)',
    '.ts': 'TypeScript',
    '.tsx': 'TypeScript (React)',
    '.vue': 'Vue',
    '.svelte': 'Svelte',
    '.java': 'Java',
    '.kt': 'Kotlin',
    '.kts': 'Kotlin',
    '.go': 'Go',
    '.rs': 'Rust',
    '.c': 'C',
    '.cpp': 'C++',
    '.cc': 'C++',
    '.cxx': 'C++',
    '.h': 'C/C++ Header',
    '.hpp': 'C++ Header',
    '.cs': 'C#',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.swift': 'Swift',
    '.m': 'Objective-C',
    '.scala': 'Scala',
    '.sh': 'Shell',
    '.bash': 'Shell',
    '.zsh': 'Shell',
    '.ps1': 'PowerShell',
    '.sql': 'SQL',
    '.html': 'HTML',
    '.htm': 'HTML',
    '.css': 'CSS',
    '.scss': 'SCSS',
    '.sass': 'SASS',
    '.less': 'LESS',
    '.lua': 'Lua',
    '.dart': 'Dart',
    '.r': 'R',
    '.pl': 'Perl',
    '.ex': 'Elixir',
    '.exs': 'Elixir',
    '.erl': 'Erlang',
    '.clj': 'Clojure',
    '.hs': 'Haskell',
    '.ml': 'OCaml',
    '.fs': 'F#',
}

CONFIG_FILES = {
    'package.json', 'requirements.txt', 'Pipfile', 'pyproject.toml',
    'setup.py', 'setup.cfg', 'go.mod', 'go.sum', 'Cargo.toml',
    'pom.xml', 'build.gradle', 'build.gradle.kts', 'Gemfile',
    'composer.json', 'mix.exs', 'rebar.config', 'CMakeLists.txt',
    'Makefile', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
    '.env.example', 'tsconfig.json', 'webpack.config.js', 'vite.config.js',
    'vite.config.ts', 'next.config.js', 'next.config.mjs', 'nuxt.config.js',
    'nuxt.config.ts', 'angular.json', 'vue.config.js', 'svelte.config.js',
    '.eslintrc.js', '.eslintrc.json', '.eslintrc.yml', '.prettierrc',
    'babel.config.js', 'jest.config.js', 'vitest.config.ts',
}

# الگوهای امنیتی خطرناک
# هر الگو یک tuple است: (regex, name, severity, validator_fn)
# validator_fn: تابع اختیاری برای اعتبارسنجی نهایی (برای کاهش false positive)
#               ورودی: خط کامل + تطبیق regex
#               خروجی: True اگر واقعی است، False اگر false positive
SECURITY_PATTERNS = [
    # --- Hardcoded credentials ---
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']{4,})["\']', 'Hardcoded Password', 'HIGH',
     lambda line, m: not any(x in m.group(2).lower() for x in ['your_', 'example', 'placeholder', 'xxx', 'change_me', '<', '>', '${', '$(', 'process.env', 'os.environ', 'getenv'])),

    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']{10,})["\']', 'Hardcoded API Key', 'HIGH',
     lambda line, m: not any(x in m.group(2).lower() for x in ['your_', 'example', 'placeholder', 'xxx', 'your-api', 'api_key_here', '<', '>', '${', '$(', 'process.env'])),

    (r'(?i)(secret|token)\s*[=:]\s*["\']([^"\']{10,})["\']', 'Hardcoded Secret/Token', 'HIGH',
     # فیلتر کردن اسم کلیدها مثل 'access_token', 'refresh_token'
     lambda line, m: not (
         m.group(2).lower() in ['access_token', 'refresh_token', 'auth_token', 'session_token', 'csrf_token', 'bearer_token']
         or any(x in m.group(2).lower() for x in ['your_', 'example', 'placeholder', 'xxx', '<', '>', '${', '$(', 'process.env', 'os.environ', 'getenv', 'token_key', 'token_name'])
     )),

    (r'(?i)aws[_-]?(access|secret)[__-]?(key|id)\s*[=:]\s*["\'][^"\']+["\']', 'AWS Credentials', 'CRITICAL', None),

    # AWS Secret Key - فقط رشته‌های واقعی داخل کوتیشن
    (r'["\']([A-Za-z0-9+/]{40})["\']', 'Possible AWS Secret Key', 'MEDIUM',
     lambda line, m: not any(x in line.lower() for x in ['path', 'url', 'route', '/api/', '/pages/', '/app/', 'import', 'from', 'require'])),

    (r'(?i)\b(sk|pk)_[a-zA-Z0-9]{20,}\b', 'Stripe/Secret Key Pattern', 'HIGH', None),
    (r'(?i)\bgh[pousr]_[A-Za-z0-9]{36}\b', 'GitHub Token', 'HIGH', None),
    (r'(?i)\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b', 'JWT Token', 'HIGH', None),

    # --- Dangerous functions ---
    # eval/exec: فقط وقتی واقعاً استفاده شده، نه داخل string یا regex
    (r'\beval\s*\(', 'Use of eval()', 'HIGH',
     lambda line, m: not any(x in line for x in ["'", '"', '#', 'r\'', 'r"', 'pattern', 'regex', 'search', 'findall', 'comment', '//'])),

    (r'\bexec\s*\(', 'Use of exec()', 'HIGH',
     lambda line, m: not any(x in line for x in ["'", '"', '#', 'r\'', 'r"', 'pattern', 'regex', 'search', 'findall', 'comment', '//', 'execScript', 'execSync'])),

    (r'(?i)os\.system\s*\(', 'os.system() call', 'MEDIUM', None),
    (r'(?i)subprocess\.call\s*\(\s*shell\s*=\s*True', 'Subprocess with shell=True', 'HIGH', None),
    (r'(?i)innerHTML\s*=', 'innerHTML assignment (XSS risk)', 'MEDIUM', None),
    (r'(?i)document\.write\s*\(', 'document.write() (XSS risk)', 'MEDIUM', None),

    # --- SQL Injection ---
    (r'(?i)SELECT\s+.*\s+FROM\s+.*\+.*', 'SQL String Concatenation', 'HIGH', None),
    (r'(?i)mysql_query\s*\(', 'Deprecated mysql_query()', 'HIGH', None),

    # --- Weak crypto ---
    (r'(?i)md5\s*\(', 'MD5 hash usage (weak)', 'MEDIUM',
     lambda line, m: 'md5' in line.lower() and not any(x in line.lower() for x in ['md5sum', 'md5_file', 'comment', '#', '//', "'md5'", '"md5"'])),
    (r'(?i)sha1\s*\(', 'SHA1 hash usage (weak)', 'MEDIUM', None),

    # --- Network security ---
    (r'(?i)http://(?!localhost|127\.0\.0\.1|0\.0\.0\.0)', 'Insecure HTTP URL', 'MEDIUM',
     lambda line, m: not any(x in line.lower() for x in ['schema://', '://schema', 'xml', 'xmlns', 'w3.org', 'example.com', 'schemas.', '://www.w3'])),

    (r'(?i)verify\s*=\s*False', 'SSL Verification Disabled', 'HIGH', None),
    (r'(?i)check_hostname\s*=\s*False', 'SSL Hostname Check Disabled', 'HIGH', None),

    # --- Suspicious TODO ---
    (r'(?i)\bTODO\b.*(?:password|secret|key|hack|bypass)', 'Suspicious TODO', 'LOW',
     lambda line, m: line.strip().startswith(('#', '//', '/*', '*')) and not any(x in line for x in ["'", '"', 'pattern', 'regex'])),
]

# نشانه‌های فریم‌ورک‌ها
FRAMEWORK_SIGNATURES = {
    'Django':           ['django', 'manage.py', 'settings.py', 'wsgi.py'],
    'Flask':            ['flask', 'app = Flask'],
    'FastAPI':          ['fastapi', 'app = FastAPI'],
    'Express.js':       ['express', 'app.listen'],
    'NestJS':           ['@nestjs', '@Module', '@Controller'],
    'Spring Boot':      ['@SpringBootApplication', 'org.springframework'],
    'Gin':              ['gin-gonic', 'gin.Engine'],
    'Rails':            ['Rails', 'config/routes.rb'],
    'Laravel':          ['laravel', 'artisan'],
    'ASP.NET':          ['Microsoft.AspNetCore', 'Startup.cs'],
    'Next.js':          ['next/', 'next.config'],
    'Nuxt.js':          ['nuxt', 'nuxt.config'],
    'Remix':            ['@remix-run'],
    'React':            ['react', 'useState', 'useEffect', 'jsx'],
    'Vue.js':           ['vue', 'createApp', '<template>'],
    'Angular':          ['@angular', '@Component'],
    'Svelte':           ['svelte', '<script>'],
    'Solid.js':         ['solid-js', 'createSignal'],
    'SQLAlchemy':       ['sqlalchemy', 'Session', 'declarative_base'],
    'Prisma':           ['prisma', '@prisma/client'],
    'Mongoose':         ['mongoose', 'Schema'],
    'TypeORM':          ['typeorm', '@Entity'],
    'Sequelize':        ['sequelize', 'Sequelize'],
    'Jest':             ['jest', 'describe(', 'it('],
    'Pytest':           ['pytest', 'def test_'],
    'Vitest':           ['vitest'],
    'JUnit':            ['@Test', 'org.junit'],
}


# ============================================================
#  کلاس اصلی تحلیلگر
# ============================================================
class ProjectAnalyzer:
    def __init__(self, project_path: str, output_dir: str = None):
        self.project_path = Path(project_path).resolve()
        if output_dir:
            self.output_dir = Path(output_dir).resolve()
        else:
            self.output_dir = self.project_path / "analysis_reports"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.results = {
            "meta": {
                "project_path": str(self.project_path),
                "analyzed_at": datetime.now().isoformat(),
                "analyzer_version": "1.2.0",
                "platform": platform.system(),
                "python_version": sys.version.split()[0],
            },
            "file_structure": {},
            "code_quality": {},
            "security": {},
            "architecture": {},
            "libraries": {},
            "backend_frontend": {},
            "summary": {},
        }

        self.start_time = time.time()
        self.scanned_files = 0
        self.scanned_lines = 0
        self.ignored_dirs = set()  # پوشه‌های نادیده گرفته شده

    # ----------------------------------------------------------
    def _should_ignore_dir(self, dir_name: str) -> bool:
        """بررسی اینکه آیا نام پوشه باید نادیده گرفته شود (exact + regex)."""
        if dir_name in IGNORE_DIRS:
            self.ignored_dirs.add(dir_name)
            return True
        for pattern in IGNORE_DIR_PATTERNS:
            if re.match(pattern, dir_name, re.IGNORECASE):
                self.ignored_dirs.add(dir_name)
                return True
        return False

    def _should_ignore_file(self, file_name: str) -> bool:
        """بررسی اینکه آیا نام فایل باید نادیده گرفته شود (exact + regex)."""
        if file_name in IGNORE_FILES:
            return True
        for pattern in IGNORE_FILE_PATTERNS:
            if re.match(pattern, file_name, re.IGNORECASE):
                return True
        return False

    def _should_ignore(self, path: Path) -> bool:
        """بررسی اینکه آیا مسیر باید نادیده گرفته شود (فقط نام خود فایل/پوشه)."""
        if path.name in IGNORE_DIRS:
            return True
        if path.name in IGNORE_FILES:
            return True
        for pattern in IGNORE_DIR_PATTERNS:
            if re.match(pattern, path.name, re.IGNORECASE):
                return True
        for pattern in IGNORE_FILE_PATTERNS:
            if re.match(pattern, path.name, re.IGNORECASE):
                return True
        return False

    def _read_file_lines(self, path: Path) -> list:
        """خواندن خطوط فایل با انکودینگ‌های مختلف."""
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'gbk']:
            try:
                with open(path, 'r', encoding=encoding, errors='ignore') as f:
                    return f.readlines()
            except:
                continue
        return []

    def _human_size(self, size_bytes: int) -> str:
        """تبدیل بایت به واحد قابل خواندن."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"

    def _print_section(self, number, title):
        """چاپ هدر بخش."""
        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}  {number}. {title}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")

    # ============================================================
    #  بخش ۱: تحلیل ساختار فایل
    # ============================================================
    def analyze_file_structure(self):
        self._print_section(1, "تحلیل ساختار فایل")

        all_files = []
        all_dirs = []
        extensions_count = Counter()
        total_size = 0
        max_depth = 0
        files_by_type = defaultdict(list)

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]

            rel_path = root_path.relative_to(self.project_path)
            depth = len(rel_path.parts) if str(rel_path) != '.' else 0
            if depth > max_depth:
                max_depth = depth
            all_dirs.append(root)

            for file in files:
                file_path = root_path / file
                if self._should_ignore(file_path):
                    continue
                try:
                    size = file_path.stat().st_size
                except:
                    size = 0
                total_size += size
                all_files.append(file_path)

                ext = file_path.suffix.lower() if file_path.suffix else '(no ext)'
                extensions_count[ext] += 1

                if ext in CODE_EXTENSIONS:
                    files_by_type[CODE_EXTENSIONS[ext]].append(str(file_path.relative_to(self.project_path)))
                elif ext in ['.json', '.yml', '.yaml', '.toml', '.ini', '.cfg']:
                    files_by_type['Config'].append(str(file_path.relative_to(self.project_path)))
                elif ext in ['.md', '.rst', '.txt']:
                    files_by_type['Documentation'].append(str(file_path.relative_to(self.project_path)))

        # بزرگترین فایل‌ها
        largest_files = []
        for f in all_files:
            try:
                size = f.stat().st_size
                largest_files.append((str(f.relative_to(self.project_path)), size))
            except:
                pass
        largest_files.sort(key=lambda x: x[1], reverse=True)
        top_largest = largest_files[:10]

        self.results['file_structure'] = {
            "total_files": len(all_files),
            "total_directories": len(all_dirs),
            "total_size_bytes": total_size,
            "total_size_human": self._human_size(total_size),
            "max_depth": max_depth,
            "extensions": dict(extensions_count.most_common(20)),
            "files_by_language": {k: len(v) for k, v in files_by_type.items()},
            "top_largest_files": [{"file": f, "size": self._human_size(s)} for f, s in top_largest],
        }

        # نمایش
        print(f"  {Color.GREEN}تعداد کل فایل‌ها:{Color.RESET} {len(all_files):,}")
        print(f"  {Color.GREEN}تعداد کل پوشه‌ها:{Color.RESET} {len(all_dirs):,}")
        print(f"  {Color.GREEN}حجم کل:{Color.RESET} {self._human_size(total_size)}")
        print(f"  {Color.GREEN}حداکثر عمق:{Color.RESET} {max_depth} سطح")

        print(f"\n  {Color.YELLOW}پسوندهای پرکاربرد:{Color.RESET}")
        max_count = max(extensions_count.values()) if extensions_count else 1
        for ext, count in extensions_count.most_common(10):
            bar_len = int((count / max_count) * 30)
            bar = '█' * bar_len
            print(f"    {ext:15} {count:>5}  {Color.BLUE}{bar}{Color.RESET}")

        print(f"\n  {Color.YELLOW}زبان‌های برنامه‌نویسی:{Color.RESET}")
        for lang, files in sorted(files_by_type.items(), key=lambda x: len(x[1]), reverse=True):
            if lang in ['Config', 'Documentation']:
                continue
            print(f"    {lang:25} {Color.GREEN}{len(files)}{Color.RESET} فایل")

        print(f"\n  {Color.YELLOW}بزرگ‌ترین فایل‌ها:{Color.RESET}")
        for f, s in top_largest[:5]:
            print(f"    {self._human_size(s):>12}  {f}")

        if self.ignored_dirs:
            print(f"\n  {Color.GRAY}پوشه‌های نادیده گرفته شده ({len(self.ignored_dirs)}):{Color.RESET}")
            print(f"    {Color.GRAY}{', '.join(sorted(self.ignored_dirs)[:15])}{Color.RESET}")
            if len(self.ignored_dirs) > 15:
                print(f"    {Color.GRAY}... و {len(self.ignored_dirs)-15} مورد دیگر{Color.RESET}")

    # ============================================================
    #  بخش ۲: تحلیل کیفیت کد
    # ============================================================
    def analyze_code_quality(self):
        self._print_section(2, "تحلیل کیفیت کد")

        large_files = []
        long_functions = []
        todo_count = 0
        fixme_count = 0
        total_code_lines = 0
        total_comment_lines = 0
        total_blank_lines = 0
        files_stats = []
        duplicate_blocks = []

        function_patterns = [
            (r'def\s+(\w+)\s*\(', 'Python'),
            (r'function\s+(\w+)\s*\(', 'JavaScript'),
            (r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', 'JS Arrow'),
            (r'func\s+(\w+)\s*\(', 'Go'),
            (r'fn\s+(\w+)\s*\(', 'Rust'),
            (r'def\s+(\w+)\s*\([^)]*\)\s*do', 'Ruby'),
            (r'func\s+(\w+)\s*\([^)]*\)', 'Swift'),
        ]

        file_count = 0
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            for file in files:
                file_path = Path(root) / file
                if self._should_ignore(file_path):
                    continue
                if file_path.suffix.lower() not in CODE_EXTENSIONS:
                    continue

                lines = self._read_file_lines(file_path)
                if not lines:
                    continue

                self.scanned_files += 1
                self.scanned_lines += len(lines)
                file_count += 1

                line_count = len(lines)
                code_lines = 0
                comment_lines = 0
                blank_lines = 0
                in_block_comment = False

                for line in lines:
                    stripped = line.strip()
                    if not stripped:
                        blank_lines += 1
                        continue
                    if '/*' in stripped and '*/' not in stripped:
                        in_block_comment = True
                        comment_lines += 1
                        continue
                    if in_block_comment:
                        comment_lines += 1
                        if '*/' in stripped or '-->' in stripped:
                            in_block_comment = False
                        continue
                    if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('*'):
                        comment_lines += 1
                        if 'TODO' in stripped.upper():
                            todo_count += 1
                        if 'FIXME' in stripped.upper():
                            fixme_count += 1
                        continue
                    code_lines += 1

                total_code_lines += code_lines
                total_comment_lines += comment_lines
                total_blank_lines += blank_lines

                rel_path = str(file_path.relative_to(self.project_path))

                if line_count > 500:
                    large_files.append({"file": rel_path, "lines": line_count})

                files_stats.append({
                    "file": rel_path,
                    "total_lines": line_count,
                    "code_lines": code_lines,
                    "comment_lines": comment_lines,
                    "blank_lines": blank_lines,
                })

                # توابع طولانی
                content = ''.join(lines)
                for pattern, lang in function_patterns:
                    for match in re.finditer(pattern, content):
                        func_start = match.start()
                        func_line_start = content[:func_start].count('\n')

                        if lang == 'Python':
                            end = min(func_line_start + 100, len(lines))
                            for i in range(func_line_start + 1, min(func_line_start + 100, len(lines))):
                                line_stripped = lines[i].rstrip()
                                if line_stripped and not line_stripped.startswith(' ') and not line_stripped.startswith('\t'):
                                    end = i
                                    break
                            else:
                                end = min(func_line_start + 100, len(lines))
                            func_length = end - func_line_start
                        else:
                            brace_count = 0
                            found_open = False
                            end = func_line_start
                            for i in range(func_line_start, min(func_line_start + 500, len(lines))):
                                brace_count += lines[i].count('{') - lines[i].count('}')
                                if '{' in lines[i]:
                                    found_open = True
                                if found_open and brace_count <= 0:
                                    end = i
                                    break
                            func_length = end - func_line_start

                        if func_length > 80:
                            func_name = match.group(1)
                            long_functions.append({
                                "file": rel_path,
                                "function": func_name,
                                "lines": func_length,
                                "language": lang,
                            })

                # بلوک‌های تکراری
                if line_count > 20:
                    block_size = 6
                    for i in range(0, line_count - block_size, block_size):
                        block = ''.join(lines[i:i+block_size]).strip()
                        if block and len(block) > 30:
                            block_hash = hashlib.md5(block.encode(errors='ignore')).hexdigest()
                            duplicate_blocks.append(block_hash)

        block_counter = Counter(duplicate_blocks)
        duplicates = [(h, c) for h, c in block_counter.items() if c > 1]
        top_duplicates = sorted(duplicates, key=lambda x: x[1], reverse=True)[:5]

        comment_ratio = (total_comment_lines / max(1, total_code_lines + total_comment_lines)) * 100

        self.results['code_quality'] = {
            "total_code_lines": total_code_lines,
            "total_comment_lines": total_comment_lines,
            "total_blank_lines": total_blank_lines,
            "comment_ratio_percent": round(comment_ratio, 2),
            "todo_count": todo_count,
            "fixme_count": fixme_count,
            "large_files_count": len(large_files),
            "long_functions_count": len(long_functions),
            "duplicate_blocks_count": len(duplicates),
            "large_files": large_files[:20],
            "long_functions": sorted(long_functions, key=lambda x: x['lines'], reverse=True)[:20],
            "top_duplicate_blocks": [{"hash": h[:8], "occurrences": c} for h, c in top_duplicates],
        }

        # نمایش
        print(f"  {Color.GREEN}کل خطوط کد:{Color.RESET} {total_code_lines:,}")
        print(f"  {Color.GREEN}کل خطوط کامنت:{Color.RESET} {total_comment_lines:,}")
        print(f"  {Color.GREEN}کل خطوط خالی:{Color.RESET} {total_blank_lines:,}")
        print(f"  {Color.GREEN}نسبت کامنت:{Color.RESET} {comment_ratio:.2f}%")
        print(f"  {Color.YELLOW}TODO:{Color.RESET} {todo_count}  |  {Color.RED}FIXME:{Color.RESET} {fixme_count}")
        print(f"  {Color.RED}فایل‌های بزرگ (>۵۰۰ خط):{Color.RESET} {len(large_files)}")
        print(f"  {Color.RED}توابع طولانی (>۸۰ خط):{Color.RESET} {len(long_functions)}")
        print(f"  {Color.YELLOW}بلوک‌های تکراری مشکوک:{Color.RESET} {len(duplicates)}")

        if long_functions:
            print(f"\n  {Color.YELLOW}بزرگ‌ترین توابع:{Color.RESET}")
            for func in sorted(long_functions, key=lambda x: x['lines'], reverse=True)[:5]:
                print(f"    {Color.RED}{func['lines']:>4}{Color.RESET} خط  {func['function']:30}  {Color.GRAY}{func['file']}{Color.RESET}")

    # ============================================================
    #  بخش ۳: تحلیل امنیت
    # ============================================================
    def analyze_security(self):
        self._print_section(3, "تحلیل امنیت")

        findings = []
        severity_counts = defaultdict(int)
        scanned_count = 0

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            for file in files:
                file_path = Path(root) / file
                if self._should_ignore(file_path):
                    continue
                if file_path.suffix.lower() not in CODE_EXTENSIONS and file_path.name not in CONFIG_FILES:
                    continue

                lines = self._read_file_lines(file_path)
                if not lines:
                    continue

                scanned_count += 1
                rel_path = str(file_path.relative_to(self.project_path))
                content = ''.join(lines)

                for pattern_data in SECURITY_PATTERNS:
                    # پشتیبانی از هر دو فرمت قدیم (3-tuple) و جدید (4-tuple)
                    if len(pattern_data) == 4:
                        pattern, name, severity, validator = pattern_data
                    else:
                        pattern, name, severity = pattern_data
                        validator = None

                    for match in re.finditer(pattern, content):
                        # محاسبه شماره خط و استخراج خط کامل
                        line_num = content[:match.start()].count('\n') + 1
                        # استخراج خط کامل
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(content)
                        full_line = content[line_start:line_end]

                        # اعتبارسنجی با validator_fn (برای کاهش false positive)
                        if validator is not None:
                            try:
                                if not validator(full_line, match):
                                    continue  # false positive - رد کردن
                            except:
                                pass  # در صورت خطا، یافته رو نگه دار

                        findings.append({
                            "file": rel_path,
                            "line": line_num,
                            "type": name,
                            "severity": severity,
                            "match": match.group()[:80],
                            "code_snippet": full_line.strip()[:120],
                        })
                        severity_counts[severity] += 1

        self.results['security'] = {
            "scanned_files": scanned_count,
            "total_findings": len(findings),
            "by_severity": dict(severity_counts),
            "findings": findings[:100],
        }

        severity_colors = {
            'CRITICAL': Color.RED + Color.BOLD,
            'HIGH': Color.RED,
            'MEDIUM': Color.YELLOW,
            'LOW': Color.GRAY,
        }

        print(f"  {Color.GREEN}فایل‌های اسکن شده:{Color.RESET} {scanned_count}")
        print(f"  {Color.RED}کل یافته‌های امنیتی:{Color.RESET} {len(findings)}")

        if severity_counts:
            print(f"\n  {Color.YELLOW}به تفکیک شدت:{Color.RESET}")
            for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
                if severity_counts[sev]:
                    color = severity_colors[sev]
                    print(f"    {color}{sev:10}{Color.RESET} {severity_counts[sev]}")

        if findings:
            print(f"\n  {Color.YELLOW}نمونه یافته‌ها (۱۰ مورد اول):{Color.RESET}")
            for f in findings[:10]:
                color = severity_colors.get(f['severity'], Color.WHITE)
                print(f"    {color}[{f['severity']:8}]{Color.RESET} {f['type']:35} {Color.GRAY}{f['file']}:{f['line']}{Color.RESET}")
        else:
            print(f"\n  {Color.GREEN}✓ مشکلی امنیتی یافت نشد!{Color.RESET}")

    # ============================================================
    #  بخش ۴: تحلیل معماری
    # ============================================================
    def analyze_architecture(self):
        self._print_section(4, "تحلیل معماری")

        detected_frameworks = defaultdict(lambda: {"count": 0, "files": []})
        entry_points = []
        config_files_found = []
        patterns = {
            'MVC': False,
            'MVVM': False,
            'Microservices': False,
            'Monolith': False,
            'Layered': False,
            'Component-based': False,
        }

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            for file in files:
                file_path = Path(root) / file
                if self._should_ignore(file_path):
                    continue
                if file in CONFIG_FILES:
                    config_files_found.append(str(file_path.relative_to(self.project_path)))

                if file in ['main.py', 'app.py', 'index.js', 'index.ts', 'server.js',
                            'main.go', 'main.rs', 'Main.java', 'Program.cs', 'index.html',
                            '__main__.py', 'manage.py', 'wsgi.py', 'asgi.py',
                            'app.ts', 'app.tsx', 'main.ts', 'main.tsx']:
                    entry_points.append(str(file_path.relative_to(self.project_path)))

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            for file in files:
                file_path = Path(root) / file
                if self._should_ignore(file_path):
                    continue
                if file_path.suffix.lower() not in CODE_EXTENSIONS and file_path.name not in CONFIG_FILES:
                    continue

                lines = self._read_file_lines(file_path)
                if not lines:
                    continue
                content = ''.join(lines)
                rel_path = str(file_path.relative_to(self.project_path))

                for framework, signatures in FRAMEWORK_SIGNATURES.items():
                    for sig in signatures:
                        if sig in content:
                            detected_frameworks[framework]["count"] += 1
                            if rel_path not in detected_frameworks[framework]["files"]:
                                detected_frameworks[framework]["files"].append(rel_path)
                            break

        # الگوهای معماری
        for root, dirs, _ in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            dir_names = [d.lower() for d in dirs]
            if any('model' in d for d in dir_names) and any('view' in d for d in dir_names):
                patterns['MVC'] = True
            if any('controller' in d for d in dir_names):
                patterns['MVC'] = True

        dockerfile_count = 0
        for root, _, files in os.walk(self.project_path):
            if 'Dockerfile' in files:
                dockerfile_count += 1
        if dockerfile_count > 1:
            patterns['Microservices'] = True

        for root, dirs, _ in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            if 'components' in [d.lower() for d in dirs]:
                patterns['Component-based'] = True
                break

        if len(entry_points) <= 2:
            patterns['Monolith'] = True

        layered_dirs = ['service', 'services', 'repository', 'repositories', 'controller', 'controllers']
        found_layered = 0
        for root, dirs, _ in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            for d in dirs:
                if d.lower() in layered_dirs:
                    found_layered += 1
        if found_layered >= 2:
            patterns['Layered'] = True

        active_patterns = [k for k, v in patterns.items() if v]

        self.results['architecture'] = {
            "detected_frameworks": {k: {"count": v["count"], "sample_files": v["files"][:3]} for k, v in detected_frameworks.items() if v["count"] > 0},
            "entry_points": entry_points,
            "config_files": config_files_found,
            "architectural_patterns": active_patterns,
            "dockerfile_count": dockerfile_count,
        }

        # نمایش
        print(f"  {Color.YELLOW}فریم‌ورک‌ها/کتابخانه‌های شناسایی‌شده:{Color.RESET}")
        for fw, data in sorted(detected_frameworks.items(), key=lambda x: x[1]["count"], reverse=True):
            if data["count"] > 0:
                print(f"    {Color.GREEN}{fw:20}{Color.RESET} ({data['count']} ارجاع)")

        print(f"\n  {Color.YELLOW}نقاط ورود:{Color.RESET}")
        if entry_points:
            for ep in entry_points[:10]:
                print(f"    {Color.GREEN}→{Color.RESET} {ep}")
        else:
            print(f"    {Color.GRAY}(نقطه ورود استاندارد یافت نشد){Color.RESET}")

        print(f"\n  {Color.YELLOW}الگوهای معماری شناسایی‌شده:{Color.RESET}")
        for pattern, active in patterns.items():
            icon = f"{Color.GREEN}✓{Color.RESET}" if active else f"{Color.GRAY}✗{Color.RESET}"
            print(f"    {icon} {pattern}")

        print(f"\n  {Color.YELLOW}فایل‌های کانفیگ ({len(config_files_found)}):{Color.RESET}")
        for cf in config_files_found[:8]:
            print(f"    {Color.GRAY}{cf}{Color.RESET}")

        if dockerfile_count:
            print(f"\n  {Color.BLUE}Dockerfile ها:{Color.RESET} {dockerfile_count}")

    # ============================================================
    #  بخش ۵: تحلیل کتابخانه‌ها و وابستگی‌ها
    # ============================================================
    def analyze_libraries(self):
        self._print_section(5, "تحلیل کتابخانه‌ها و وابستگی‌ها")

        dependencies = {
            "python": [],
            "node": [],
            "go": [],
            "rust": [],
            "ruby": [],
            "php": [],
        }

        # Python — جستجوی همه فایل‌های requirements*.txt و pyproject.toml در پروژه
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            for fname in files:
                if fname in ['requirements.txt', 'requirements-dev.txt', 'dev-requirements.txt']:
                    req_path = Path(root) / fname
                    lines = self._read_file_lines(req_path)
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            pkg = re.split(r'[=<>!~\[]', line)[0].strip()
                            if pkg and pkg not in dependencies['python']:
                                dependencies['python'].append(pkg)
                elif fname == 'pyproject.toml':
                    pyproject_path = Path(root) / fname
                    content = ''.join(self._read_file_lines(pyproject_path))
                    deps_section = re.search(r'\[project\.dependencies\](.*?)(\[|$)', content, re.DOTALL)
                    if deps_section:
                        for line in deps_section.group(1).strip().split('\n'):
                            line = line.strip().strip('"').strip("'")
                            if line and not line.startswith('#'):
                                pkg = re.split(r'[=<>!~\[ ]', line)[0].strip()
                                if pkg and pkg not in dependencies['python']:
                                    dependencies['python'].append(pkg)

        pipfile = self.project_path / 'Pipfile'
        if pipfile.exists():
            content = ''.join(self._read_file_lines(pipfile))
            packages_section = re.search(r'\[packages\](.*?)(\[|$)', content, re.DOTALL)
            if packages_section:
                for line in packages_section.group(1).strip().split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        pkg = line.split('=')[0].strip()
                        if pkg:
                            dependencies['python'].append(pkg)

        # Node.js — جستجوی همه فایل‌های package.json در پروژه (به جز node_modules)
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            if 'package.json' in files:
                pkg_json_path = Path(root) / 'package.json'
                try:
                    with open(pkg_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    deps = data.get('dependencies', {})
                    dev_deps = data.get('devDependencies', {})
                    peer_deps = data.get('peerDependencies', {})
                    for dep in list(deps.keys()) + list(dev_deps.keys()) + list(peer_deps.keys()):
                        if dep not in dependencies['node']:
                            dependencies['node'].append(dep)
                except:
                    pass

        # Go
        go_mod = self.project_path / 'go.mod'
        if go_mod.exists():
            lines = self._read_file_lines(go_mod)
            for line in lines:
                line = line.strip()
                if line.startswith('require') or line.startswith(')') or line.startswith('//'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    dependencies['go'].append(parts[0])

        # Rust
        cargo = self.project_path / 'Cargo.toml'
        if cargo.exists():
            content = ''.join(self._read_file_lines(cargo))
            deps_section = re.search(r'\[dependencies\](.*?)(\[|$)', content, re.DOTALL)
            if deps_section:
                for line in deps_section.group(1).strip().split('\n'):
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        pkg = line.split('=')[0].strip()
                        if pkg:
                            dependencies['rust'].append(pkg)

        # Ruby
        gemfile = self.project_path / 'Gemfile'
        if gemfile.exists():
            lines = self._read_file_lines(gemfile)
            for line in lines:
                line = line.strip()
                match = re.match(r"gem\s+['\"]([^'\"]+)['\"]", line)
                if match:
                    dependencies['ruby'].append(match.group(1))

        # PHP
        composer = self.project_path / 'composer.json'
        if composer.exists():
            try:
                with open(composer, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                deps = data.get('require', {})
                for dep in deps.keys():
                    if not dep.startswith('php'):
                        dependencies['php'].append(dep)
            except:
                pass

        for lang in dependencies:
            dependencies[lang] = list(set(dependencies[lang]))

        total_deps = sum(len(d) for d in dependencies.values())

        self.results['libraries'] = {
            "total_dependencies": total_deps,
            "by_language": {k: v for k, v in dependencies.items() if v},
        }

        # نمایش
        print(f"  {Color.GREEN}کل وابستگی‌ها:{Color.RESET} {total_deps}")

        lang_names = {
            'python': 'Python',
            'node': 'Node.js',
            'go': 'Go',
            'rust': 'Rust',
            'ruby': 'Ruby',
            'php': 'PHP',
        }

        for lang_key, lang_name in lang_names.items():
            deps = dependencies[lang_key]
            if deps:
                print(f"\n  {Color.YELLOW}{lang_name} ({len(deps)} وابستگی):{Color.RESET}")
                for dep in sorted(deps)[:20]:
                    print(f"    {Color.GREEN}•{Color.RESET} {dep}")
                if len(deps) > 20:
                    print(f"    {Color.GRAY}... و {len(deps)-20} مورد دیگر{Color.RESET}")

    # ============================================================
    #  بخش ۶: تحلیل بک‌اند و فرانت‌اند
    # ============================================================
    def analyze_backend_frontend(self):
        self._print_section(6, "تحلیل بک‌اند و فرانت‌اند")

        backend_files = []
        backend_languages = set()
        backend_frameworks = []
        api_route_files = []
        database_files = []

        frontend_files = []
        frontend_languages = set()
        frontend_frameworks = []
        frontend_assets = []
        entry_html = []

        backend_extensions = {'.py', '.go', '.rs', '.java', '.rb', '.php', '.cs', '.kt'}
        frontend_extensions = {'.jsx', '.tsx', '.vue', '.svelte', '.html', '.css', '.scss', '.sass'}
        api_indicators = ['@app.route', '@router', 'app.get(', 'app.post(', 'router.get(',
                          'router.post(', '@GetMapping', '@PostMapping', '@RequestMapping',
                          'gin.GET', 'gin.POST']

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not self._should_ignore_dir(d)]
            root_path = Path(root)

            for file in files:
                file_path = root_path / file
                if self._should_ignore(file_path):
                    continue
                ext = file_path.suffix.lower()
                rel_path = str(file_path.relative_to(self.project_path))

                if file == 'index.html':
                    entry_html.append(rel_path)

                if ext in ['.css', '.scss', '.sass', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2']:
                    frontend_assets.append(rel_path)

                if ext in ['.db', '.sqlite', '.sqlite3'] or file in ['schema.sql', 'migration.sql']:
                    database_files.append(rel_path)

                if ext in backend_extensions:
                    backend_languages.add(CODE_EXTENSIONS.get(ext, ext))
                    backend_files.append(rel_path)
                    lines = self._read_file_lines(file_path)
                    content = ''.join(lines)
                    for indicator in api_indicators:
                        if indicator in content:
                            api_route_files.append(rel_path)
                            break

                if ext in frontend_extensions or ext in ['.js', '.ts']:
                    if file_path.parent.name.lower() in ['public', 'static', 'assets', 'components', 'pages', 'views']:
                        frontend_languages.add(CODE_EXTENSIONS.get(ext, ext))
                        frontend_files.append(rel_path)
                    elif ext in frontend_extensions:
                        frontend_languages.add(CODE_EXTENSIONS.get(ext, ext))
                        frontend_files.append(rel_path)

        arch_fw = self.results.get('architecture', {}).get('detected_frameworks', {})
        backend_fw_names = ['Django', 'Flask', 'FastAPI', 'Express.js', 'NestJS', 'Spring Boot', 'Gin', 'Rails', 'Laravel', 'ASP.NET']
        frontend_fw_names = ['React', 'Vue.js', 'Angular', 'Svelte', 'Solid.js', 'Next.js', 'Nuxt.js', 'Remix']

        for fw in backend_fw_names:
            if fw in arch_fw:
                backend_frameworks.append(fw)
        for fw in frontend_fw_names:
            if fw in arch_fw:
                frontend_frameworks.append(fw)

        has_backend = bool(backend_files or backend_frameworks)
        has_frontend = bool(frontend_files or frontend_frameworks or entry_html)

        project_type = "نامشخص"
        if has_backend and has_frontend:
            project_type = "Full-Stack"
        elif has_backend:
            project_type = "Backend"
        elif has_frontend:
            project_type = "Frontend"

        self.results['backend_frontend'] = {
            "project_type": project_type,
            "has_backend": has_backend,
            "has_frontend": has_frontend,
            "backend": {
                "languages": list(backend_languages),
                "frameworks": backend_frameworks,
                "file_count": len(backend_files),
                "api_route_files": len(api_route_files),
                "database_files": database_files,
            },
            "frontend": {
                "languages": list(frontend_languages),
                "frameworks": frontend_frameworks,
                "file_count": len(frontend_files),
                "asset_count": len(frontend_assets),
                "entry_html_files": entry_html,
            },
        }

        # نمایش
        print(f"  {Color.MAGENTA}{Color.BOLD}نوع پروژه:{Color.RESET} {Color.YELLOW}{project_type}{Color.RESET}")

        print(f"\n  {Color.BLUE}{Color.BOLD}بک‌اند:{Color.RESET}")
        if has_backend:
            print(f"    {Color.GREEN}زبان‌ها:{Color.RESET} {', '.join(backend_languages) or '—'}")
            print(f"    {Color.GREEN}فریم‌ورک‌ها:{Color.RESET} {', '.join(backend_frameworks) or '—'}")
            print(f"    {Color.GREEN}فایل‌های بک‌اند:{Color.RESET} {len(backend_files)}")
            print(f"    {Color.GREEN}فایل‌های API:{Color.RESET} {len(api_route_files)}")
            if database_files:
                print(f"    {Color.GREEN}فایل‌های دیتابیس:{Color.RESET} {len(database_files)}")
        else:
            print(f"    {Color.GRAY}(بک‌اند شناسایی نشد){Color.RESET}")

        print(f"\n  {Color.MAGENTA}{Color.BOLD}فرانت‌اند:{Color.RESET}")
        if has_frontend:
            print(f"    {Color.GREEN}زبان‌ها:{Color.RESET} {', '.join(frontend_languages) or '—'}")
            print(f"    {Color.GREEN}فریم‌ورک‌ها:{Color.RESET} {', '.join(frontend_frameworks) or '—'}")
            print(f"    {Color.GREEN}فایل‌های فرانت‌اند:{Color.RESET} {len(frontend_files)}")
            print(f"    {Color.GREEN}فایل‌های استاتیک:{Color.RESET} {len(frontend_assets)}")
        else:
            print(f"    {Color.GRAY}(فرانت‌اند شناسایی نشد){Color.RESET}")

    # ============================================================
    #  تولید خلاصه نهایی
    # ============================================================
    def generate_summary(self):
        elapsed = time.time() - self.start_time

        sec_findings = self.results['security'].get('total_findings', 0)
        sec_critical = self.results['security'].get('by_severity', {}).get('CRITICAL', 0)
        sec_high = self.results['security'].get('by_severity', {}).get('HIGH', 0)

        score = 100
        score -= min(20, self.results['code_quality'].get('large_files_count', 0) * 2)
        score -= min(15, self.results['code_quality'].get('long_functions_count', 0) * 1)
        score -= min(40, sec_critical * 10 + sec_high * 5)
        score -= min(10, self.results['code_quality'].get('duplicate_blocks_count', 0))
        score = max(0, score)

        if score >= 80:
            grade = 'A'
            grade_color = Color.GREEN
        elif score >= 60:
            grade = 'B'
            grade_color = Color.YELLOW
        elif score >= 40:
            grade = 'C'
            grade_color = Color.YELLOW
        elif score >= 20:
            grade = 'D'
            grade_color = Color.RED
        else:
            grade = 'F'
            grade_color = Color.RED + Color.BOLD

        self.results['summary'] = {
            "health_score": score,
            "health_grade": grade,
            "analysis_time_seconds": round(elapsed, 2),
            "files_scanned": self.scanned_files,
            "lines_scanned": self.scanned_lines,
            "total_findings": sec_findings,
            "critical_findings": sec_critical,
            "project_type": self.results['backend_frontend'].get('project_type'),
            "total_dependencies": self.results['libraries'].get('total_dependencies', 0),
        }

        print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}  خلاصه نهایی{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"  {Color.CYAN}زمان تحلیل:{Color.RESET} {elapsed:.2f} ثانیه")
        print(f"  {Color.CYAN}فایل‌های اسکن شده:{Color.RESET} {self.scanned_files:,}")
        print(f"  {Color.CYAN}خطوط اسکن شده:{Color.RESET} {self.scanned_lines:,}")
        print(f"  {Color.CYAN}نوع پروژه:{Color.RESET} {self.results['backend_frontend'].get('project_type')}")
        print(f"  {Color.CYAN}کل وابستگی‌ها:{Color.RESET} {self.results['libraries'].get('total_dependencies', 0)}")
        print(f"  {Color.CYAN}یافته‌های امنیتی:{Color.RESET} {sec_findings} ({sec_critical} بحرانی)")
        print(f"\n  {Color.BOLD}امتیاز سلامت پروژه:{Color.RESET} {grade_color}{Color.BOLD}{score}/100 (نمره {grade}){Color.RESET}")

    # ============================================================
    #  ذخیره گزارش‌ها
    # ============================================================
    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # JSON
        json_path = self.output_dir / f"project_analysis_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        # TXT
        txt_path = self.output_dir / f"project_analysis_{timestamp}.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("  گزارش تحلیل پروژه - Project Analysis Report\n")
            f.write(f"  مسیر: {self.project_path}\n")
            f.write(f"  تاریخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"  سیستم: {platform.system()} {platform.release()}\n")
            f.write("=" * 70 + "\n\n")

            summary = self.results['summary']
            f.write("=== خلاصه نهایی ===\n")
            f.write(f"امتیاز سلامت: {summary['health_score']}/100 (نمره {summary['health_grade']})\n")
            f.write(f"نوع پروژه: {summary['project_type']}\n")
            f.write(f"زمان تحلیل: {summary['analysis_time_seconds']} ثانیه\n")
            f.write(f"فایل‌های اسکن شده: {summary['files_scanned']}\n")
            f.write(f"خطوط اسکن شده: {summary['lines_scanned']}\n")
            f.write(f"کل وابستگی‌ها: {summary['total_dependencies']}\n")
            f.write(f"یافته‌های امنیتی: {summary['total_findings']} ({summary['critical_findings']} بحرانی)\n\n")

            fs = self.results['file_structure']
            f.write("=== ساختار فایل ===\n")
            f.write(f"تعداد فایل‌ها: {fs['total_files']}\n")
            f.write(f"تعداد پوشه‌ها: {fs['total_directories']}\n")
            f.write(f"حجم کل: {fs['total_size_human']}\n")
            f.write(f"حداکثر عمق: {fs['max_depth']}\n")
            f.write("\nپسوندهای پرکاربرد:\n")
            for ext, count in list(fs['extensions'].items())[:10]:
                f.write(f"  {ext}: {count}\n")
            f.write("\nزبان‌ها:\n")
            for lang, count in fs['files_by_language'].items():
                f.write(f"  {lang}: {count} فایل\n")
            f.write("\nبزرگ‌ترین فایل‌ها:\n")
            for f_info in fs['top_largest_files'][:10]:
                f.write(f"  {f_info['size']:>12}  {f_info['file']}\n")

            cq = self.results['code_quality']
            f.write("\n=== کیفیت کد ===\n")
            f.write(f"کل خطوط کد: {cq['total_code_lines']}\n")
            f.write(f"کل خطوط کامنت: {cq['total_comment_lines']}\n")
            f.write(f"نسبت کامنت: {cq['comment_ratio_percent']}%\n")
            f.write(f"TODO: {cq['todo_count']}\n")
            f.write(f"FIXME: {cq['fixme_count']}\n")
            f.write(f"فایل‌های بزرگ: {cq['large_files_count']}\n")
            f.write(f"توابع طولانی: {cq['long_functions_count']}\n")
            f.write(f"بلوک‌های تکراری: {cq['duplicate_blocks_count']}\n")
            if cq['large_files']:
                f.write("\nفایل‌های بزرگ:\n")
                for lf in cq['large_files']:
                    f.write(f"  {lf['lines']} خط  {lf['file']}\n")
            if cq['long_functions']:
                f.write("\nتوابع طولانی:\n")
                for lf in cq['long_functions'][:20]:
                    f.write(f"  {lf['lines']} خط  {lf['function']}  ({lf['language']})  {lf['file']}\n")

            sec = self.results['security']
            f.write("\n=== امنیت ===\n")
            f.write(f"فایل‌های اسکن شده: {sec['scanned_files']}\n")
            f.write(f"کل یافته‌ها: {sec['total_findings']}\n")
            f.write(f"به تفکیک شدت: {sec['by_severity']}\n")
            if sec['findings']:
                f.write("\nیافته‌ها:\n")
                for finding in sec['findings']:
                    f.write(f"  [{finding['severity']}] {finding['type']} - {finding['file']}:{finding['line']}\n")
                    f.write(f"      تطبیق: {finding['match']}\n")

            arch = self.results['architecture']
            f.write("\n=== معماری ===\n")
            f.write(f"نقاط ورود: {arch['entry_points']}\n")
            f.write(f"الگوهای معماری: {', '.join(arch['architectural_patterns']) or 'نامشخص'}\n")
            f.write(f"تعداد Dockerfile: {arch['dockerfile_count']}\n")
            f.write("\nفریم‌ورک‌های شناسایی‌شده:\n")
            for fw, data in arch['detected_frameworks'].items():
                f.write(f"  {fw} ({data['count']} ارجاع)\n")
            f.write("\nفایل‌های کانفیگ:\n")
            for cf in arch['config_files']:
                f.write(f"  {cf}\n")

            libs = self.results['libraries']
            f.write("\n=== کتابخانه‌ها ===\n")
            f.write(f"کل وابستگی‌ها: {libs['total_dependencies']}\n")
            for lang, deps in libs['by_language'].items():
                f.write(f"\n{lang} ({len(deps)}):\n")
                for dep in sorted(deps):
                    f.write(f"  - {dep}\n")

            bf = self.results['backend_frontend']
            f.write("\n=== بک‌اند / فرانت‌اند ===\n")
            f.write(f"نوع پروژه: {bf['project_type']}\n")
            f.write(f"\nبک‌اند:\n")
            f.write(f"  زبان‌ها: {', '.join(bf['backend']['languages'])}\n")
            f.write(f"  فریم‌ورک‌ها: {', '.join(bf['backend']['frameworks'])}\n")
            f.write(f"  تعداد فایل: {bf['backend']['file_count']}\n")
            f.write(f"  فایل‌های API: {bf['backend']['api_route_files']}\n")
            if bf['backend']['database_files']:
                f.write(f"  فایل‌های دیتابیس: {bf['backend']['database_files']}\n")
            f.write(f"\nفرانت‌اند:\n")
            f.write(f"  زبان‌ها: {', '.join(bf['frontend']['languages'])}\n")
            f.write(f"  فریم‌ورک‌ها: {', '.join(bf['frontend']['frameworks'])}\n")
            f.write(f"  تعداد فایل: {bf['frontend']['file_count']}\n")
            f.write(f"  فایل‌های استاتیک: {bf['frontend']['asset_count']}\n")

        # HTML Report
        html_path = self.output_dir / f"project_analysis_{timestamp}.html"
        self._generate_html_report(html_path)

        print(f"\n{Color.GREEN}{Color.BOLD}✓ گزارش‌ها ذخیره شدند:{Color.RESET}")
        print(f"  {Color.CYAN}JSON:{Color.RESET} {json_path}")
        print(f"  {Color.CYAN}TXT:{Color.RESET}  {txt_path}")
        print(f"  {Color.CYAN}HTML:{Color.RESET} {html_path}")

        return json_path, txt_path, html_path

    # ============================================================
    #  ساخت گزارش HTML
    # ============================================================
    def _generate_html_report(self, html_path):
        """ساخت گزارش HTML زیبا."""
        summary = self.results['summary']
        fs = self.results['file_structure']
        cq = self.results['code_quality']
        sec = self.results['security']
        arch = self.results['architecture']
        libs = self.results['libraries']
        bf = self.results['backend_frontend']

        # رنگ نمره
        score = summary['health_score']
        if score >= 80:
            score_color = '#10b981'
        elif score >= 60:
            score_color = '#f59e0b'
        elif score >= 40:
            score_color = '#f97316'
        else:
            score_color = '#ef4444'

        # بار چارت برای زبان‌ها
        lang_bars = ""
        max_lang = max(fs['files_by_language'].values()) if fs['files_by_language'] else 1
        for lang, count in sorted(fs['files_by_language'].items(), key=lambda x: x[1], reverse=True):
            if lang in ['Config', 'Documentation']:
                continue
            width = int((count / max_lang) * 100)
            lang_bars += f"""
            <div class="bar-item">
                <span class="bar-label">{lang}</span>
                <div class="bar-container"><div class="bar-fill" style="width: {width}%"></div></div>
                <span class="bar-value">{count}</span>
            </div>"""

        # یافته‌های امنیتی
        security_rows = ""
        severity_colors = {
            'CRITICAL': '#ef4444',
            'HIGH': '#f97316',
            'MEDIUM': '#f59e0b',
            'LOW': '#6b7280',
        }
        for f in sec.get('findings', [])[:30]:
            color = severity_colors.get(f['severity'], '#6b7280')
            security_rows += f"""
            <tr>
                <td><span class="badge" style="background:{color}">{f['severity']}</span></td>
                <td>{f['type']}</td>
                <td class="file-path">{f['file']}:{f['line']}</td>
            </tr>"""

        # فریم‌ورک‌ها
        framework_items = ""
        for fw, data in sorted(arch['detected_frameworks'].items(), key=lambda x: x[1]['count'], reverse=True):
            framework_items += f"<span class='framework-tag'>{fw} <small>({data['count']})</small></span>"

        # وابستگی‌ها
        deps_html = ""
        for lang, deps in libs['by_language'].items():
            deps_html += f"<h4>{lang} ({len(deps)})</h4><div class='deps-grid'>"
            for dep in sorted(deps):
                deps_html += f"<span class='dep-item'>{dep}</span>"
            deps_html += "</div>"

        html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گزارش تحلیل پروژه</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            background: linear-gradient(135deg, #1e293b, #334155);
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 24px;
            border: 1px solid #334155;
        }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; color: #f1f5f9; }}
        .header .meta {{ color: #94a3b8; font-size: 14px; }}
        .header .meta span {{ margin-left: 20px; }}

        .score-card {{
            background: #1e293b;
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            margin-bottom: 24px;
            border: 1px solid #334155;
        }}
        .score-circle {{
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 8px solid {score_color};
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 15px;
            font-size: 36px;
            font-weight: bold;
            color: {score_color};
        }}
        .score-label {{ font-size: 18px; color: #94a3b8; }}

        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin-bottom: 24px; }}
        .stat-card {{
            background: #1e293b;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #334155;
        }}
        .stat-card .label {{ color: #94a3b8; font-size: 13px; margin-bottom: 5px; }}
        .stat-card .value {{ font-size: 24px; font-weight: bold; color: #f1f5f9; }}

        .section {{
            background: #1e293b;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 24px;
            border: 1px solid #334155;
        }}
        .section h2 {{ color: #60a5fa; margin-bottom: 16px; font-size: 20px; border-bottom: 2px solid #334155; padding-bottom: 10px; }}

        .bar-item {{ display: flex; align-items: center; margin-bottom: 10px; gap: 10px; }}
        .bar-label {{ width: 180px; font-size: 14px; color: #cbd5e1; }}
        .bar-container {{ flex: 1; background: #0f172a; border-radius: 6px; height: 24px; overflow: hidden; }}
        .bar-fill {{ height: 100%; background: linear-gradient(90deg, #3b82f6, #60a5fa); border-radius: 6px; }}
        .bar-value {{ width: 60px; text-align: left; font-weight: bold; color: #60a5fa; }}

        .framework-tag {{
            display: inline-block;
            background: #334155;
            color: #93c5fd;
            padding: 6px 14px;
            border-radius: 20px;
            margin: 4px;
            font-size: 14px;
        }}
        .framework-tag small {{ color: #64748b; }}

        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 10px; text-align: right; border-bottom: 1px solid #334155; }}
        th {{ color: #94a3b8; font-weight: 600; font-size: 13px; }}
        .file-path {{ direction: ltr; text-align: left; font-family: monospace; color: #94a3b8; font-size: 12px; }}

        .badge {{ padding: 3px 10px; border-radius: 12px; font-size: 11px; color: white; font-weight: bold; }}

        .deps-grid {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }}
        .dep-item {{
            background: #0f172a;
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 13px;
            color: #a5b4fc;
            border: 1px solid #334155;
        }}

        .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
        .info-block h3 {{ color: #c084fc; margin-bottom: 10px; font-size: 16px; }}
        .info-block ul {{ list-style: none; }}
        .info-block li {{ padding: 4px 0; color: #cbd5e1; }}

        .badge-success {{ background: #10b981; }}
        .badge-warning {{ background: #f59e0b; }}
        .badge-danger {{ background: #ef4444; }}

        .footer {{ text-align: center; color: #64748b; padding: 20px; font-size: 13px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 گزارش تحلیل پروژه</h1>
            <div class="meta">
                <span>📁 {self.project_path}</span>
                <span>📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</span>
                <span>💻 {platform.system()} {platform.release()}</span>
            </div>
        </div>

        <div class="score-card">
            <div class="score-circle">{score}</div>
            <div class="score-label">امتیاز سلامت پروژه (نمره {summary['health_grade']})</div>
        </div>

        <div class="grid">
            <div class="stat-card">
                <div class="label">نوع پروژه</div>
                <div class="value">{summary['project_type']}</div>
            </div>
            <div class="stat-card">
                <div class="label">فایل‌های اسکن شده</div>
                <div class="value">{summary['files_scanned']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">خطوط اسکن شده</div>
                <div class="value">{summary['lines_scanned']:,}</div>
            </div>
            <div class="stat-card">
                <div class="label">کل وابستگی‌ها</div>
                <div class="value">{summary['total_dependencies']}</div>
            </div>
            <div class="stat-card">
                <div class="label">یافته‌های امنیتی</div>
                <div class="value" style="color: #ef4444">{summary['total_findings']}</div>
            </div>
            <div class="stat-card">
                <div class="label">زمان تحلیل</div>
                <div class="value">{summary['analysis_time_seconds']}s</div>
            </div>
        </div>

        <div class="section">
            <h2>🏗️ ساختار فایل</h2>
            <div class="grid">
                <div class="stat-card">
                    <div class="label">تعداد فایل‌ها</div>
                    <div class="value">{fs['total_files']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="label">تعداد پوشه‌ها</div>
                    <div class="value">{fs['total_directories']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="label">حجم کل</div>
                    <div class="value">{fs['total_size_human']}</div>
                </div>
                <div class="stat-card">
                    <div class="label">حداکثر عمق</div>
                    <div class="value">{fs['max_depth']} سطح</div>
                </div>
            </div>
            <h3 style="color: #94a3b8; margin: 20px 0 10px;">زبان‌های برنامه‌نویسی</h3>
            {lang_bars}
        </div>

        <div class="section">
            <h2>📝 کیفیت کد</h2>
            <div class="grid">
                <div class="stat-card">
                    <div class="label">کل خطوط کد</div>
                    <div class="value">{cq['total_code_lines']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="label">خطوط کامنت</div>
                    <div class="value">{cq['total_comment_lines']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="label">نسبت کامنت</div>
                    <div class="value">{cq['comment_ratio_percent']}%</div>
                </div>
                <div class="stat-card">
                    <div class="label">فایل‌های بزرگ</div>
                    <div class="value" style="color: #f59e0b">{cq['large_files_count']}</div>
                </div>
                <div class="stat-card">
                    <div class="label">توابع طولانی</div>
                    <div class="value" style="color: #f59e0b">{cq['long_functions_count']}</div>
                </div>
                <div class="stat-card">
                    <div class="label">بلوک‌های تکراری</div>
                    <div class="value" style="color: #f59e0b">{cq['duplicate_blocks_count']}</div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2>🔒 امنیت</h2>
            <div class="grid">
                <div class="stat-card">
                    <div class="label">کل یافته‌ها</div>
                    <div class="value" style="color: #ef4444">{sec['total_findings']}</div>
                </div>
                <div class="stat-card">
                    <div class="label">بحرانی</div>
                    <div class="value" style="color: #ef4444">{sec['by_severity'].get('CRITICAL', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="label">خطر بالا</div>
                    <div class="value" style="color: #f97316">{sec['by_severity'].get('HIGH', 0)}</div>
                </div>
                <div class="stat-card">
                    <div class="label">خطر متوسط</div>
                    <div class="value" style="color: #f59e0b">{sec['by_severity'].get('MEDIUM', 0)}</div>
                </div>
            </div>
            {f"<table><thead><tr><th>شدت</th><th>نوع</th><th>محل</th></tr></thead><tbody>{security_rows}</tbody></table>" if security_rows else "<p style='color: #10b981; padding: 10px;'>✓ مشکلی امنیتی یافت نشد!</p>"}
        </div>

        <div class="section">
            <h2>🎯 معماری و فریم‌ورک‌ها</h2>
            <h3 style="color: #94a3b8; margin-bottom: 10px;">فریم‌ورک‌های شناسایی‌شده</h3>
            <div style="margin-bottom: 20px;">{framework_items or '<span style="color: #64748b;">هیچ فریم‌ورکی شناسایی نشد</span>'}</div>
            <h3 style="color: #94a3b8; margin-bottom: 10px;">الگوهای معماری</h3>
            <div>
                {"".join(f"<span class='framework-tag'>{p}</span>" for p in arch['architectural_patterns']) or '<span style="color: #64748b;">نامشخص</span>'}
            </div>
        </div>

        <div class="section">
            <h2>📦 کتابخانه‌ها و وابستگی‌ها</h2>
            {deps_html or '<p style="color: #64748b;">هیچ وابستگی‌ای یافت نشد</p>'}
        </div>

        <div class="section">
            <h2>⚙️ بک‌اند / فرانت‌اند</h2>
            <div class="info-grid">
                <div class="info-block">
                    <h3>Backend (بک‌اند)</h3>
                    <ul>
                        <li>زبان‌ها: {', '.join(bf['backend']['languages']) or '—'}</li>
                        <li>فریم‌ورک‌ها: {', '.join(bf['backend']['frameworks']) or '—'}</li>
                        <li>تعداد فایل: {bf['backend']['file_count']}</li>
                        <li>فایل‌های API: {bf['backend']['api_route_files']}</li>
                    </ul>
                </div>
                <div class="info-block">
                    <h3>Frontend (فرانت‌اند)</h3>
                    <ul>
                        <li>زبان‌ها: {', '.join(bf['frontend']['languages']) or '—'}</li>
                        <li>فریم‌ورک‌ها: {', '.join(bf['frontend']['frameworks']) or '—'}</li>
                        <li>تعداد فایل: {bf['frontend']['file_count']}</li>
                        <li>فایل‌های استاتیک: {bf['frontend']['asset_count']}</li>
                    </ul>
                </div>
            </div>
        </div>

        <div class="footer">
            گزارش تولید شده توسط <strong>Project Analyzer v1.2.0</strong> (Super Z - Z.ai)
        </div>
    </div>
</body>
</html>"""

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)

    # ============================================================
    #  اجرای کامل تحلیل
    # ============================================================
    def run(self):
        print(f"\n{Color.MAGENTA}{Color.BOLD}{'╔' + '═'*58 + '╗'}{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}║  🚀 Project Analyzer v1.2.0 - تحلیلگر جامع پروژه{' ' * 9}║{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}║  مسیر: {str(self.project_path):<51}║{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}{'╚' + '═'*58 + '╝'}{Color.RESET}")

        if not self.project_path.exists():
            print(f"{Color.RED}❌ خطا: مسیر پروژه وجود ندارد!{Color.RESET}")
            print(f"   مسیر بررسی شده: {self.project_path}")
            return False

        self.analyze_file_structure()
        self.analyze_code_quality()
        self.analyze_security()
        self.analyze_architecture()
        self.analyze_libraries()
        self.analyze_backend_frontend()
        self.generate_summary()
        self.save_results()

        print(f"\n{Color.GREEN}{Color.BOLD}✓ تحلیل کامل شد!{Color.RESET}\n")
        return True


# ============================================================
#  نقطه ورود اصلی
# ============================================================
def main():
    # فعال‌سازی رنگ در ویندوز
    Color.enable_windows()

    # تشخیص سیستم‌عامل برای پیام راهنما
    default_path = r"D:\econojin.com"

    parser = argparse.ArgumentParser(
        description='تحلیلگر جامع پروژه - Project Analyzer v1.2.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
مثال‌ها:
  python project_analyzer.py                                    # تحلیل {default_path}
  python project_analyzer.py "D:/my-project"                    # تحلیل مسیر دلخواه
  python project_analyzer.py "C:\\Users\\name\\project" --no-color
  python project_analyzer.py /home/user/project -o ./reports

خروجی‌ها در پوشه analysis_reports/ در داخل مسیر پروژه ذخیره می‌شوند.
        """
    )
    parser.add_argument('path', nargs='?', default=default_path,
                        help=f'مسیر پروژه برای تحلیل (پیش‌فرض: {default_path})')
    parser.add_argument('-o', '--output', default=None,
                        help='پوشه خروجی گزارش‌ها (پیش‌فرض: analysis_reports/ داخل پروژه)')
    parser.add_argument('--no-color', action='store_true',
                        help='غیرفعال کردن رنگ در خروجی کنسول')

    args = parser.parse_args()

    if args.no_color:
        Color.disable()

    analyzer = ProjectAnalyzer(args.path, args.output)
    success = analyzer.run()

    if not success:
        sys.exit(1)


if __name__ == '__main__':
    main()

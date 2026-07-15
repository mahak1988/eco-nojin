#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Frontend Structure Analyzer v1.0
=============================================
اسکریپت جامع تحلیل ساختار، کیفیت و معماری فرانت‌اند

لایه‌های تحلیل:
1. ساختار فایل‌ها (File Structure)
2. گراف وابستگی‌ها (Dependency Graph)
3. شناسایی الگوها (Pattern Detection)
4. کیفیت کد (Code Quality)
5. فایل‌های تکراری (Duplicate Detection)
6. کد مرده (Dead Code Detection)
7. معیارهای کمی (Quantitative Metrics)
8. توصیه‌های معماری (Architecture Recommendations)

نحوه اجرا:
    python scripts/analyze_frontend_structure.py
    python scripts/analyze_frontend_structure.py --output html
    python scripts/analyze_frontend_structure.py --web-dir apps/web

نویسنده: Eco Nojin Architecture Team
نسخه: 1.0.0
"""

import os
import re
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from collections import defaultdict, Counter
import logging

# ============================================================
# Configuration
# ============================================================

VERSION = "1.0.0"
PROJECT_NAME = "Eco Nojin"

# تنظیمات لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('frontend_analysis.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# دایرکتوری‌های مستثنی
EXCLUDED_DIRS = {
    "node_modules", ".next", "dist", "build", ".cache",
    ".turbo", "coverage", ".git", ".vscode", ".idea",
    "__pycache__", ".venv", "venv"
}

# ============================================================
# Data Models
# ============================================================

@dataclass
class FileInfo:
    """اطلاعات یک فایل"""
    path: str
    name: str
    extension: str
    size_bytes: int
    lines_total: int
    lines_code: int
    lines_comment: int
    lines_blank: int
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    pattern_type: str = ""  # component, hook, context, service, util, type, test, other
    complexity: float = 0.0
    has_any_type: bool = False
    any_count: int = 0
    has_ts_ignore: bool = False
    ts_ignore_count: int = 0
    has_use_effect: bool = False
    use_effect_without_deps: bool = False
    content_hash: str = ""
    last_modified: str = ""

@dataclass
class DependencyEdge:
    """یک یال در گراف وابستگی"""
    source: str
    target: str
    import_statement: str
    is_relative: bool = False

@dataclass
class DuplicateGroup:
    """گروه فایل‌های تکراری"""
    hash: str
    files: List[str]
    size_bytes: int
    lines: int

@dataclass
class DeadCode:
    """کد مرده شناسایی‌شده"""
    file: str
    type: str  # unused_export, unused_file, empty_file
    details: str

@dataclass
class Finding:
    """یک یافته (مشکل یا توصیه)"""
    id: str
    category: str
    severity: str  # critical, high, medium, low, info
    message: str
    file: str = ""
    line: int = 0
    recommendation: str = ""

@dataclass
class FrontendReport:
    """گزارش نهایی تحلیل فرانت‌اند"""
    timestamp: str
    project_name: str
    web_root: str
    version: str
    summary: Dict[str, Any]
    files: Dict[str, FileInfo]
    dependencies: List[Dict]
    patterns: Dict[str, int]
    duplicates: List[Dict]
    dead_code: List[Dict]
    findings: List[Dict]
    recommendations: List[Dict]
    metrics: Dict[str, Any]

# ============================================================
# Terminal Colors
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def cprint(msg: str, color: str = Colors.END):
    print(f"{color}{msg}{Colors.END}")

# ============================================================
# TypeScript/React Analyzer
# ============================================================

class TypeScriptAnalyzer:
    """تحلیلگر فایل‌های TypeScript/React"""
    
    # الگوهای شناسایی
    PATTERNS = {
        "component": re.compile(
            r"(?:export\s+(?:default\s+)?)?(?:function|const)\s+[A-Z]\w*(?:\s*=\s*(?:\([^)]*\)|[^=])\s*=>)|(?:class\s+[A-Z]\w*\s+extends\s+(?:React\.Component|Component|PureComponent))",
            re.MULTILINE
        ),
        "hook": re.compile(
            r"(?:export\s+(?:default\s+)?)?(?:function|const)\s+use[A-Z]\w*",
            re.MULTILINE
        ),
        "context": re.compile(
            r"(?:createContext|React\.createContext)",
            re.MULTILINE
        ),
        "service": re.compile(
            r"(?:export\s+(?:default\s+)?)?(?:class|const)\s+\w*(?:Service|Api|Client)\w*",
            re.MULTILINE
        ),
        "util": re.compile(
            r"(?:export\s+(?:default\s+)?)?(?:function|const)\s+\w+(?:Helper|Utils?|Formatter)\w*",
            re.MULTILINE
        ),
        "type": re.compile(
            r"export\s+(?:type|interface)\s+[A-Z]\w*",
            re.MULTILINE
        ),
        "test": re.compile(
            r"(?:describe|it|test)\s*\(",
            re.MULTILINE
        ),
    }
    
    # الگوهای import
    IMPORT_PATTERNS = [
        re.compile(r"import\s+(?:type\s+)?(?:\{[^}]+\}|[\w*]+)\s+from\s+['\"]([^'\"]+)['\"]"),
        re.compile(r"import\s+['\"]([^'\"]+)['\"]"),
        re.compile(r"import\s+\(\s*['\"]([^'\"]+)['\"]\s*\)"),
    ]
    
    # الگوهای export
    EXPORT_PATTERNS = [
        re.compile(r"export\s+(?:default\s+)?(?:function|class|const|let|var|type|interface|enum)\s+(\w+)"),
        re.compile(r"export\s+\{([^}]+)\}"),
    ]
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.content = ""
        self.info = FileInfo(
            path=str(file_path),
            name=file_path.name,
            extension=file_path.suffix,
            size_bytes=0,
            lines_total=0,
            lines_code=0,
            lines_comment=0,
            lines_blank=0,
        )
    
    def analyze(self) -> Optional[FileInfo]:
        """انجام تحلیل کامل"""
        try:
            self.content = self.file_path.read_text(encoding="utf-8")
            self.info.size_bytes = len(self.content.encode("utf-8"))
            self.info.last_modified = datetime.fromtimestamp(
                self.file_path.stat().st_mtime
            ).isoformat()
            
            # محاسبه hash برای تشخیص تکراری
            self.info.content_hash = hashlib.md5(
                self.content.encode("utf-8")
            ).hexdigest()
            
            self._count_lines()
            self._extract_imports()
            self._extract_exports()
            self._detect_pattern()
            self._analyze_quality()
            self._calculate_complexity()
            
            return self.info
        except Exception as e:
            logger.error(f"خطا در تحلیل {self.file_path}: {e}")
            return None
    
    def _count_lines(self):
        """شمارش خطوط"""
        lines = self.content.split("\n")
        self.info.lines_total = len(lines)
        self.info.lines_blank = sum(1 for l in lines if not l.strip())
        
        # شمارش کامنت‌ها
        comment_lines = 0
        in_block_comment = False
        
        for line in lines:
            stripped = line.strip()
            
            if in_block_comment:
                comment_lines += 1
                if "*/" in stripped:
                    in_block_comment = False
            elif stripped.startswith("//"):
                comment_lines += 1
            elif stripped.startswith("/*"):
                comment_lines += 1
                if "*/" not in stripped:
                    in_block_comment = True
            elif stripped.startswith("*"):
                comment_lines += 1
        
        self.info.lines_comment = comment_lines
        self.info.lines_code = self.info.lines_total - comment_lines - self.info.lines_blank
    
    def _extract_imports(self):
        """استخراج لیست importها"""
        imports = set()
        
        for pattern in self.IMPORT_PATTERNS:
            matches = pattern.findall(self.content)
            imports.update(matches)
        
        self.info.imports = sorted(list(imports))
    
    def _extract_exports(self):
        """استخراج لیست exportها"""
        exports = set()
        
        # export function/const/class
        for match in self.EXPORT_PATTERNS[0].finditer(self.content):
            exports.add(match.group(1))
        
        # export { ... }
        for match in self.EXPORT_PATTERNS[1].finditer(self.content):
            names = match.group(1)
            for name in names.split(","):
                name = name.strip()
                if " as " in name:
                    name = name.split(" as ")[0].strip()
                if name and name != "type":
                    exports.add(name)
        
        self.info.exports = sorted(list(exports))
    
    def _detect_pattern(self):
        """شناسایی نوع فایل (الگو)"""
        scores = {}
        
        for pattern_name, pattern_regex in self.PATTERNS.items():
            matches = pattern_regex.findall(self.content)
            scores[pattern_name] = len(matches)
        
        # انتخاب الگوی غالب
        if scores:
            max_pattern = max(scores.items(), key=lambda x: x[1])
            if max_pattern[1] > 0:
                self.info.pattern_type = max_pattern[0]
            else:
                self.info.pattern_type = "other"
        else:
            self.info.pattern_type = "other"
        
        # اصلاح بر اساس نام فایل
        filename = self.file_path.name.lower()
        if filename.endswith(".test.tsx") or filename.endswith(".test.ts"):
            self.info.pattern_type = "test"
        elif filename.endswith(".spec.tsx") or filename.endswith(".spec.ts"):
            self.info.pattern_type = "test"
        elif "hook" in filename or filename.startswith("use"):
            self.info.pattern_type = "hook"
        elif "context" in filename:
            self.info.pattern_type = "context"
        elif "service" in filename or "api" in filename:
            self.info.pattern_type = "service"
        elif "util" in filename or "helper" in filename:
            self.info.pattern_type = "util"
        elif "type" in filename or filename.endswith(".d.ts"):
            self.info.pattern_type = "type"
    
    def _analyze_quality(self):
        """تحلیل کیفیت کد"""
        # شمارش `any`
        any_matches = re.findall(r":\s*any\b", self.content)
        self.info.any_count = len(any_matches)
        self.info.has_any_type = self.info.any_count > 0
        
        # شمارش `@ts-ignore`
        ts_ignore_matches = re.findall(r"@\s*ts-ignore", self.content)
        self.info.ts_ignore_count = len(ts_ignore_matches)
        self.info.has_ts_ignore = self.info.ts_ignore_count > 0
        
        # بررسی useEffect
        use_effect_matches = re.findall(r"useEffect\s*\(", self.content)
        self.info.has_use_effect = len(use_effect_matches) > 0
        
        # بررسی useEffect بدون dependency
        if self.info.has_use_effect:
            # الگوی ساده: useEffect(... بدون []
            bad_patterns = re.findall(
                r"useEffect\s*\(\s*\(\)\s*=>\s*\{[^}]*\}\s*\)(?!\s*\[)",
                self.content,
                re.DOTALL
            )
            self.info.use_effect_without_deps = len(bad_patterns) > 0
    
    def _calculate_complexity(self):
        """محاسبه پیچیدگی تقریبی"""
        # شمارش ساختارهای شرطی و حلقه
        conditionals = len(re.findall(
            r"\b(if|else|while|for|switch|case|\?|&&|\|\||catch)\b",
            self.content
        ))
        
        functions = len(re.findall(
            r"(?:function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])\s*=>)",
            self.content
        ))
        
        if functions > 0:
            self.info.complexity = 1 + (conditionals / functions)
        else:
            self.info.complexity = 1

# ============================================================
# Frontend Structure Analyzer
# ============================================================

class FrontendStructureAnalyzer:
    """تحلیلگر اصلی ساختار فرانت‌اند"""
    
    def __init__(self, web_root: Path):
        self.web_root = web_root
        self.src_dir = web_root / "src" if (web_root / "src").exists() else web_root
        self.files: Dict[str, FileInfo] = {}
        self.dependencies: List[DependencyEdge] = []
        self.duplicates: List[DuplicateGroup] = []
        self.dead_code: List[DeadCode] = []
        self.findings: List[Finding] = []
        self.recommendations: List[Dict] = []
        self.patterns: Dict[str, int] = defaultdict(int)
        self.directory_stats: Dict[str, Dict] = defaultdict(lambda: {
            "files": 0, "lines": 0, "patterns": defaultdict(int)
        })
    
    def analyze(self) -> FrontendReport:
        """اجرای تحلیل کامل"""
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint(f"🔬 {PROJECT_NAME} - Frontend Structure Analyzer v{VERSION}", Colors.HEADER)
        cprint("=" * 70, Colors.HEADER)
        
        # ۱. اسکن فایل‌ها
        cprint("\n📂 مرحله ۱: اسکن ساختار فایل‌ها...", Colors.BLUE)
        all_files = self._scan_files()
        cprint(f"   ✅ {len(all_files)} فایل شناسایی شد", Colors.GREEN)
        
        # ۲. تحلیل فایل‌ها
        cprint("\n🔍 مرحله ۲: تحلیل محتوای فایل‌ها...", Colors.BLUE)
        self._analyze_files(all_files)
        cprint(f"   ✅ {len(self.files)} فایل تحلیل شد", Colors.GREEN)
        
        # ۳. تحلیل گراف وابستگی
        cprint("\n🕸️  مرحله ۳: تحلیل گراف وابستگی...", Colors.BLUE)
        self._analyze_dependencies()
        cprint(f"   ✅ {len(self.dependencies)} یال وابستگی شناسایی شد", Colors.GREEN)
        
        # ۴. شناسایی الگوها
        cprint("\n🎨 مرحله ۴: شناسایی الگوها...", Colors.BLUE)
        self._analyze_patterns()
        
        # ۵. شناسایی فایل‌های تکراری
        cprint("\n🔁 مرحله ۵: شناسایی فایل‌های تکراری...", Colors.BLUE)
        self._find_duplicates()
        cprint(f"   ✅ {len(self.duplicates)} گروه تکراری شناسایی شد", Colors.GREEN)
        
        # ۶. شناسایی کد مرده
        cprint("\n💀 مرحله ۶: شناسایی کد مرده...", Colors.BLUE)
        self._find_dead_code()
        cprint(f"   ✅ {len(self.dead_code)} مورد کد مرده شناسایی شد", Colors.GREEN)
        
        # ۷. تحلیل کیفیت
        cprint("\n✨ مرحله ۷: تحلیل کیفیت کد...", Colors.BLUE)
        self._analyze_quality()
        
        # ۸. تولید توصیه‌ها
        cprint("\n💡 مرحله ۸: تولید توصیه‌های معماری...", Colors.BLUE)
        self._generate_recommendations()
        
        # ۹. تولید گزارش
        cprint("\n📝 مرحله ۹: تولید گزارش نهایی...", Colors.BLUE)
        report = self._generate_report()
        
        return report
    
    def _scan_files(self) -> List[Path]:
        """اسکن تمام فایل‌های فرانت‌اند"""
        files = []
        extensions = {".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".json"}
        
        search_dir = self.src_dir if self.src_dir.exists() else self.web_root
        
        for path in search_dir.rglob("*"):
            if not path.is_file():
                continue
            
            # بررسی استثناها
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            
            # بررسی پسوند
            if path.suffix.lower() in extensions:
                files.append(path)
        
        return files
    
    def _analyze_files(self, files: List[Path]):
        """تحلیل محتوای فایل‌ها"""
        code_extensions = {".ts", ".tsx", ".js", ".jsx"}
        
        for i, file_path in enumerate(files, 1):
            if i % 50 == 0:
                cprint(f"   ⏳ تحلیل {i}/{len(files)}...", Colors.DIM)
            
            if file_path.suffix.lower() in code_extensions:
                analyzer = TypeScriptAnalyzer(file_path)
                info = analyzer.analyze()
                if info:
                    self.files[str(file_path)] = info
                    
                    # به‌روزرسانی آمار دایرکتوری
                    rel_dir = str(file_path.parent.relative_to(self.web_root))
                    self.directory_stats[rel_dir]["files"] += 1
                    self.directory_stats[rel_dir]["lines"] += info.lines_total
                    if info.pattern_type:
                        self.directory_stats[rel_dir]["patterns"][info.pattern_type] += 1
    
    def _analyze_dependencies(self):
        """تحلیل گراف وابستگی"""
        for file_path_str, info in self.files.items():
            file_path = Path(file_path_str)
            
            for import_path in info.imports:
                # رد کردن importهای خارجی (node_modules)
                if not import_path.startswith(".") and not import_path.startswith("/"):
                    continue
                
                # حل مسیر نسبی
                try:
                    if import_path.startswith("."):
                        target_path = (file_path.parent / import_path).resolve()
                        
                        # افزودن پسوند در صورت نیاز
                        if not target_path.exists():
                            for ext in [".ts", ".tsx", ".js", ".jsx"]:
                                if target_path.with_suffix(ext).exists():
                                    target_path = target_path.with_suffix(ext)
                                    break
                        
                        # بررسی index
                        if not target_path.exists():
                            index_path = target_path / "index.ts"
                            if index_path.exists():
                                target_path = index_path
                            else:
                                index_path = target_path / "index.tsx"
                                if index_path.exists():
                                    target_path = index_path
                        
                        if target_path.exists():
                            self.dependencies.append(DependencyEdge(
                                source=file_path_str,
                                target=str(target_path),
                                import_statement=import_path,
                                is_relative=True
                            ))
                except Exception:
                    continue
    
    def _analyze_patterns(self):
        """تحلیل الگوها"""
        for info in self.files.values():
            if info.pattern_type:
                self.patterns[info.pattern_type] += 1
    
    def _find_duplicates(self):
        """شناسایی فایل‌های تکراری"""
        hash_to_files = defaultdict(list)
        
        for file_path, info in self.files.items():
            if info.content_hash:
                hash_to_files[info.content_hash].append(file_path)
        
        for content_hash, file_list in hash_to_files.items():
            if len(file_list) > 1:
                # بررسی اینکه واقعاً تکراری هستند (نه فقط خالی)
                first_file = Path(file_list[0])
                if first_file.exists():
                    info = self.files[file_list[0]]
                    if info.lines_code > 10:  # فقط فایل‌های با محتوای واقعی
                        self.duplicates.append(DuplicateGroup(
                            hash=content_hash,
                            files=file_list,
                            size_bytes=info.size_bytes,
                            lines=info.lines_total
                        ))
    
    def _find_dead_code(self):
        """شناسایی کد مرده"""
        # ۱. فایل‌های خالی
        for file_path, info in self.files.items():
            if info.lines_code == 0 and info.lines_total > 0:
                self.dead_code.append(DeadCode(
                    file=file_path,
                    type="empty_file",
                    details="فایل فقط شامل کامنت یا خطوط خالی است"
                ))
        
        # ۲. فایل‌های بدون export
        for file_path, info in self.files.items():
            if info.lines_code > 20 and not info.exports:
                # بررسی اینکه آیا فایل import شده است
                is_imported = any(
                    dep.target == file_path for dep in self.dependencies
                )
                if not is_imported and info.pattern_type not in ["test"]:
                    self.dead_code.append(DeadCode(
                        file=file_path,
                        type="unused_file",
                        details="فایل export ندارد و توسط هیچ فایل دیگری import نشده"
                    ))
        
        # ۳. Exportهای استفاده نشده
        # (این تحلیل پیچیده‌تر است و نیاز به تحلیل گراف کامل دارد)
    
    def _analyze_quality(self):
        """تحلیل کیفیت کد"""
        finding_id = 0
        
        # ۱. فایل‌های بزرگ
        for file_path, info in self.files.items():
            if info.lines_total > 500:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Quality",
                    severity="high",
                    message=f"فایل بسیار بزرگ: {info.lines_total} خط",
                    file=file_path,
                    recommendation="فایل را به چند فایل کوچکتر تقسیم کنید"
                ))
        
        # ۲. استفاده از `any`
        for file_path, info in self.files.items():
            if info.any_count > 10:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="TypeScript",
                    severity="medium",
                    message=f"استفاده زیاد از `any`: {info.any_count} مورد",
                    file=file_path,
                    recommendation="از typeهای دقیق استفاده کنید"
                ))
        
        # ۳. استفاده از `@ts-ignore`
        for file_path, info in self.files.items():
            if info.ts_ignore_count > 0:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="TypeScript",
                    severity="low",
                    message=f"استفاده از `@ts-ignore`: {info.ts_ignore_count} مورد",
                    file=file_path,
                    recommendation="مشکل type را حل کنید به جای نادیده گرفتن"
                ))
        
        # ۴. useEffect بدون dependency
        for file_path, info in self.files.items():
            if info.use_effect_without_deps:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="React",
                    severity="high",
                    message="useEffect بدون dependency array",
                    file=file_path,
                    recommendation="dependency array را اضافه کنید یا از useEffect به درستی استفاده کنید"
                ))
        
        # ۵. پیچیدگی بالا
        for file_path, info in self.files.items():
            if info.complexity > 10:
                finding_id += 1
                self.findings.append(Finding(
                    id=f"F-{finding_id:03d}",
                    category="Quality",
                    severity="medium",
                    message=f"پیچیدگی بالا: {info.complexity:.1f}",
                    file=file_path,
                    recommendation="توابع را به توابع کوچکتر تقسیم کنید"
                ))
    
    def _generate_recommendations(self):
        """تولید توصیه‌های معماری"""
        
        # ۱. توصیه بر اساس ساختار
        if len(self.files) > 150:
            self.recommendations.append({
                "priority": "high",
                "category": "Architecture",
                "message": f"تعداد فایل‌ها ({len(self.files)}) زیاد است. از ساختار Feature-based استفاده کنید."
            })
        
        # ۲. توصیه بر اساس تکراری‌ها
        if self.duplicates:
            total_waste = sum(d.size_bytes * (len(d.files) - 1) for d in self.duplicates)
            self.recommendations.append({
                "priority": "high",
                "category": "Code Quality",
                "message": f"{len(self.duplicates)} فایل تکراری شناسایی شد ({total_waste/1024:.1f} KB هدررفت). آن‌ها را استخراج و مشترک کنید."
            })
        
        # ۳. توصیه بر اساس کد مرده
        if self.dead_code:
            self.recommendations.append({
                "priority": "medium",
                "category": "Cleanup",
                "message": f"{len(self.dead_code)} مورد کد مرده شناسایی شد. آن‌ها را حذف کنید."
            })
        
        # ۴. توصیه بر اساس کیفیت TypeScript
        total_any = sum(info.any_count for info in self.files.values())
        if total_any > 50:
            self.recommendations.append({
                "priority": "medium",
                "category": "TypeScript",
                "message": f"{total_any} مورد استفاده از `any` در کل پروژه. strict mode را فعال کنید."
            })
        
        # ۵. توصیه بر اساس ساختار پوشه‌ها
        if len(self.directory_stats) > 20:
            self.recommendations.append({
                "priority": "low",
                "category": "Organization",
                "message": f"{len(self.directory_stats)} دایرکتوری مختلف. ساختار را ساده‌تر کنید."
            })
        
        # ۶. توصیه بر اساس الگوها
        component_count = self.patterns.get("component", 0)
        if component_count > 100:
            self.recommendations.append({
                "priority": "medium",
                "category": "Components",
                "message": f"{component_count} کامپوننت شناسایی شد. کامپوننت‌های مشترک را در shared/ قرار دهید."
            })
    
    def _generate_report(self) -> FrontendReport:
        """تولید گزارش نهایی"""
        
        # محاسبه معیارهای کلی
        total_files = len(self.files)
        total_lines = sum(info.lines_total for info in self.files.values())
        total_code_lines = sum(info.lines_code for info in self.files.values())
        total_size = sum(info.size_bytes for info in self.files.values())
        
        # میانگین‌ها
        avg_file_size = total_size / total_files if total_files > 0 else 0
        avg_lines = total_lines / total_files if total_files > 0 else 0
        avg_complexity = sum(info.complexity for info in self.files.values()) / total_files if total_files > 0 else 0
        
        # توزیع زبان‌ها
        lang_counter = Counter(info.extension for info in self.files.values())
        
        # توزیع الگوها
        pattern_counter = Counter(info.pattern_type for info in self.files.values() if info.pattern_type)
        
        # بزرگترین فایل‌ها
        largest_files = sorted(
            self.files.values(),
            key=lambda x: x.lines_total,
            reverse=True
        )[:10]
        
        # پیچیده‌ترین فایل‌ها
        complex_files = sorted(
            self.files.values(),
            key=lambda x: x.complexity,
            reverse=True
        )[:10]
        
        summary = {
            "total_files": total_files,
            "total_lines": total_lines,
            "total_code_lines": total_code_lines,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / 1024 / 1024, 2),
            "avg_file_size_bytes": round(avg_file_size),
            "avg_lines_per_file": round(avg_lines),
            "avg_complexity": round(avg_complexity, 2),
            "languages": dict(lang_counter),
            "patterns": dict(pattern_counter),
            "total_dependencies": len(self.dependencies),
            "total_duplicates": len(self.duplicates),
            "total_dead_code": len(self.dead_code),
            "total_findings": len(self.findings),
            "critical_findings": len([f for f in self.findings if f.severity == "critical"]),
            "high_findings": len([f for f in self.findings if f.severity == "high"]),
        }
        
        metrics = {
            "largest_files": [
                {"path": f.path, "lines": f.lines_total, "size": f.size_bytes}
                for f in largest_files
            ],
            "complex_files": [
                {"path": f.path, "complexity": f.complexity, "lines": f.lines_total}
                for f in complex_files
            ],
            "directory_stats": {
                k: {
                    "files": v["files"],
                    "lines": v["lines"],
                    "patterns": dict(v["patterns"])
                }
                for k, v in sorted(
                    self.directory_stats.items(),
                    key=lambda x: x[1]["files"],
                    reverse=True
                )[:20]
            }
        }
        
        return FrontendReport(
            timestamp=datetime.now().isoformat(),
            project_name=PROJECT_NAME,
            web_root=str(self.web_root),
            version=VERSION,
            summary=summary,
            files={k: asdict(v) for k, v in self.files.items()},
            dependencies=[asdict(d) for d in self.dependencies],
            patterns=dict(self.patterns),
            duplicates=[asdict(d) for d in self.duplicates],
            dead_code=[asdict(d) for d in self.dead_code],
            findings=[asdict(f) for f in self.findings],
            recommendations=self.recommendations,
            metrics=metrics
        )
    
    def print_summary(self, report: FrontendReport):
        """چاپ خلاصه گزارش"""
        cprint("\n" + "=" * 70, Colors.HEADER)
        cprint("📊 خلاصه تحلیل فرانت‌اند", Colors.HEADER)
        cprint("=" * 70, Colors.HEADER)
        
        # آمار کلی
        cprint(f"\n{Colors.BOLD}📈 آمار کلی:{Colors.END}")
        cprint(f"   📁 کل فایل‌ها: {Colors.BOLD}{report.summary['total_files']}{Colors.END}")
        cprint(f"   📝 کل خطوط: {Colors.BOLD}{report.summary['total_lines']:,}{Colors.END}")
        cprint(f"   💻 خطوط کد: {Colors.BOLD}{report.summary['total_code_lines']:,}{Colors.END}")
        cprint(f"   💾 حجم کل: {Colors.BOLD}{report.summary['total_size_mb']} MB{Colors.END}")
        cprint(f"   📏 میانگین خطوط/فایل: {Colors.BOLD}{report.summary['avg_lines_per_file']}{Colors.END}")
        cprint(f"   🌀 میانگین پیچیدگی: {Colors.BOLD}{report.summary['avg_complexity']}{Colors.END}")
        
        # توزیع زبان‌ها
        cprint(f"\n{Colors.BOLD}🌐 توزیع زبان‌ها:{Colors.END}")
        for lang, count in sorted(report.summary['languages'].items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(30, count // 5)
            cprint(f"   {lang:8s}: {count:5d} {Colors.DIM}{bar}{Colors.END}")
        
        # توزیع الگوها
        cprint(f"\n{Colors.BOLD}🎨 توزیع الگوها:{Colors.END}")
        for pattern, count in sorted(report.summary['patterns'].items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(30, count // 2)
            cprint(f"   {pattern:12s}: {count:5d} {Colors.DIM}{bar}{Colors.END}")
        
        # بزرگترین فایل‌ها
        cprint(f"\n{Colors.BOLD}📏 بزرگترین فایل‌ها:{Colors.END}")
        for f in report.metrics['largest_files'][:5]:
            cprint(f"   {f['lines']:5d} خط - {Path(f['path']).name}", Colors.DIM)
        
        # یافته‌ها
        cprint(f"\n{Colors.BOLD}⚠️  یافته‌ها ({len(report.findings)}):{Colors.END}")
        
        severity_colors = {
            "critical": Colors.RED,
            "high": Colors.RED,
            "medium": Colors.YELLOW,
            "low": Colors.BLUE,
            "info": Colors.CYAN,
        }
        
        by_severity = defaultdict(list)
        for f in report.findings:
            by_severity[f['severity']].append(f)
        
        for severity in ["critical", "high", "medium", "low"]:
            findings = by_severity.get(severity, [])
            if findings:
                color = severity_colors[severity]
                cprint(f"\n   {color}{Colors.BOLD}[{severity.upper()}] ({len(findings)}){Colors.END}")
                for f in findings[:5]:
                    cprint(f"      • {f['message']}", Colors.END)
                    if f.get('recommendation'):
                        cprint(f"        {Colors.DIM}→ {f['recommendation']}{Colors.END}")
                if len(findings) > 5:
                    cprint(f"      {Colors.DIM}... و {len(findings) - 5} مورد دیگر{Colors.END}")
        
        # فایل‌های تکراری
        if report.duplicates:
            cprint(f"\n{Colors.BOLD}🔁 فایل‌های تکراری ({len(report.duplicates)}):{Colors.END}")
            for dup in report.duplicates[:5]:
                cprint(f"   • {len(dup['files'])} فایل ({dup['lines']} خط):", Colors.YELLOW)
                for f in dup['files'][:3]:
                    cprint(f"      - {Path(f).name}", Colors.DIM)
        
        # توصیه‌ها
        if report.recommendations:
            cprint(f"\n{Colors.BOLD}💡 توصیه‌های معماری:{Colors.END}")
            for rec in report.recommendations:
                priority_color = {
                    "high": Colors.RED,
                    "medium": Colors.YELLOW,
                    "low": Colors.GREEN
                }.get(rec['priority'], Colors.END)
                cprint(f"   {priority_color}[{rec['priority'].upper()}]{Colors.END} "
                      f"{rec['category']}: {rec['message']}")
        
        cprint("\n" + "=" * 70, Colors.HEADER)

# ============================================================
# Report Generators
# ============================================================

def save_json_report(report: FrontendReport, output_path: Path):
    """ذخیره گزارش JSON"""
    data = {
        "timestamp": report.timestamp,
        "project_name": report.project_name,
        "web_root": report.web_root,
        "version": report.version,
        "summary": report.summary,
        "patterns": report.patterns,
        "duplicates": report.duplicates,
        "dead_code": report.dead_code,
        "findings": report.findings,
        "recommendations": report.recommendations,
        "metrics": report.metrics,
    }
    
    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    cprint(f"\n💾 گزارش JSON ذخیره شد: {output_path}", Colors.GREEN)

def save_html_report(report: FrontendReport, output_path: Path):
    """ذخیره گزارش HTML"""
    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>گزارش تحلیل فرانت‌اند {report.project_name}</title>
    <style>
        * {{ box-sizing: border-box; }}
        body {{ font-family: Tahoma, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 30px; border-right: 4px solid #3498db; padding-right: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 8px; text-align: center; color: white; }}
        .stat-value {{ font-size: 28px; font-weight: bold; }}
        .stat-label {{ opacity: 0.9; margin-top: 5px; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: right; border-bottom: 1px solid #ddd; }}
        th {{ background: #3498db; color: white; }}
        tr:hover {{ background: #f8f9fa; }}
        .critical {{ background: #e74c3c; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
        .high {{ background: #e67e22; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
        .medium {{ background: #f39c12; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
        .low {{ background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
        .finding {{ background: #fff; border-right: 4px solid #e74c3c; padding: 15px; margin: 10px 0; border-radius: 4px; }}
        .finding.high {{ border-right-color: #e67e22; }}
        .finding.medium {{ border-right-color: #f39c12; }}
        .finding.low {{ border-right-color: #3498db; }}
        .recommendation {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-radius: 4px; border-right: 4px solid #27ae60; }}
        .duplicate {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-radius: 4px; border-right: 4px solid #ffc107; }}
        .bar {{ display: inline-block; height: 12px; background: linear-gradient(90deg, #3498db, #2980b9); border-radius: 6px; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        @media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
<div class="container">
    <h1>🔬 گزارش تحلیل فرانت‌اند {report.project_name}</h1>
    <p>تاریخ: {report.timestamp[:10]} | نسخه تحلیلگر: {report.version}</p>
    
    <h2>📈 آمار کلی</h2>
    <div class="summary">
        <div class="stat"><div class="stat-value">{report.summary['total_files']}</div><div class="stat-label">کل فایل‌ها</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_lines']:,}</div><div class="stat-label">کل خطوط</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_code_lines']:,}</div><div class="stat-label">خطوط کد</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_size_mb']} MB</div><div class="stat-label">حجم کل</div></div>
        <div class="stat"><div class="stat-value">{report.summary['avg_lines_per_file']}</div><div class="stat-label">میانگین خطوط/فایل</div></div>
        <div class="stat"><div class="stat-value">{report.summary['avg_complexity']}</div><div class="stat-label">میانگین پیچیدگی</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_duplicates']}</div><div class="stat-label">فایل تکراری</div></div>
        <div class="stat"><div class="stat-value">{report.summary['total_findings']}</div><div class="stat-label">یافته‌ها</div></div>
    </div>
    
    <div class="grid-2">
        <div>
            <h2>🌐 توزیع زبان‌ها</h2>
            <table>
                <tr><th>زبان</th><th>تعداد</th><th>نمودار</th></tr>
"""
    
    for lang, count in sorted(report.summary['languages'].items(), key=lambda x: x[1], reverse=True):
        max_count = max(report.summary['languages'].values())
        bar_width = int((count / max_count) * 200) if max_count > 0 else 0
        html += f"""
                <tr>
                    <td><strong>{lang}</strong></td>
                    <td>{count}</td>
                    <td><div class="bar" style="width: {bar_width}px;"></div></td>
                </tr>
"""
    
    html += """
            </table>
        </div>
        
        <div>
            <h2>🎨 توزیع الگوها</h2>
            <table>
                <tr><th>الگو</th><th>تعداد</th><th>نمودار</th></tr>
"""
    
    if report.summary['patterns']:
        max_pattern = max(report.summary['patterns'].values())
        for pattern, count in sorted(report.summary['patterns'].items(), key=lambda x: x[1], reverse=True):
            bar_width = int((count / max_pattern) * 200) if max_pattern > 0 else 0
            html += f"""
                <tr>
                    <td><strong>{pattern}</strong></td>
                    <td>{count}</td>
                    <td><div class="bar" style="width: {bar_width}px;"></div></td>
                </tr>
"""
    
    html += """
            </table>
        </div>
    </div>
    
    <h2>📏 بزرگترین فایل‌ها</h2>
    <table>
        <tr><th>فایل</th><th>خطوط</th><th>حجم (KB)</th></tr>
"""
    
    for f in report.metrics['largest_files'][:10]:
        html += f"""
        <tr>
            <td><code>{Path(f['path']).name}</code></td>
            <td>{f['lines']:,}</td>
            <td>{f['size']/1024:.1f}</td>
        </tr>
"""
    
    html += """
    </table>
    
    <h2>⚠️ یافته‌ها</h2>
"""
    
    for f in report.findings[:30]:
        html += f"""
    <div class="finding {f['severity']}">
        <span class="{f['severity']}">{f['severity'].upper()}</span>
        <strong>[{f['category']}]</strong> {f['message']}
        <br><small>📁 {Path(f.get('file', '')).name if f.get('file') else ''}</small>
        <br><small>→ {f.get('recommendation', '')}</small>
    </div>
"""
    
    if report.duplicates:
        html += """
    <h2>🔁 فایل‌های تکراری</h2>
"""
        for dup in report.duplicates[:10]:
            html += f"""
    <div class="duplicate">
        <strong>{len(dup['files'])} فایل تکراری</strong> ({dup['lines']} خط)
        <ul>
"""
            for f in dup['files'][:5]:
                html += f"            <li><code>{Path(f).name}</code></li>\n"
            html += """
        </ul>
    </div>
"""
    
    html += """
    
    <h2>💡 توصیه‌های معماری</h2>
"""
    
    for rec in report.recommendations:
        html += f"""
    <div class="recommendation">
        <strong>[{rec['priority'].upper()}] {rec['category']}:</strong> {rec['message']}
    </div>
"""
    
    html += """
</div>
</body>
</html>
"""
    
    output_path.write_text(html, encoding="utf-8")
    cprint(f"💾 گزارش HTML ذخیره شد: {output_path}", Colors.GREEN)

# ============================================================
# Main Entry Point
# ============================================================

def find_project_root() -> Path:
    """پیدا کردن ریشه پروژه"""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "apps").exists():
            return current
        current = current.parent
    return Path.cwd()

def main():
    parser = argparse.ArgumentParser(
        description=f"{PROJECT_NAME} - Frontend Structure Analyzer v{VERSION}"
    )
    parser.add_argument(
        "--web-dir", type=str, default="",
        help="مسیر دایرکتوری فرانت‌اند (پیش‌فرض: apps/web)"
    )
    parser.add_argument(
        "--output", type=str, default="all",
        choices=["terminal", "json", "html", "all"],
        help="نوع خروجی"
    )
    parser.add_argument(
        "--output-dir", type=str, default=".",
        help="دایرکتوری ذخیره گزارش‌ها"
    )
    
    args = parser.parse_args()
    
    project_root = find_project_root()
    
    # تعیین مسیر فرانت‌اند
    if args.web_dir:
        web_root = Path(args.web_dir).resolve()
    else:
        web_root = project_root / "apps" / "web"
    
    if not web_root.exists():
        cprint(f"\n❌ دایرکتوری فرانت‌اند یافت نشد: {web_root}", Colors.RED)
        sys.exit(1)
    
    cprint(f"\n🌱 {PROJECT_NAME} Frontend Analyzer v{VERSION}", Colors.BOLD)
    cprint(f"📂 ریشه پروژه: {project_root}", Colors.DIM)
    cprint(f"📂 دایرکتوری فرانت: {web_root}", Colors.DIM)
    
    # اجرای تحلیل
    analyzer = FrontendStructureAnalyzer(web_root)
    report = analyzer.analyze()
    
    # نمایش خلاصه
    analyzer.print_summary(report)
    
    # ذخیره گزارش‌ها
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if args.output in ["json", "all"]:
        save_json_report(report, output_dir / f"frontend_analysis_{timestamp}.json")
    
    if args.output in ["html", "all"]:
        save_html_report(report, output_dir / f"frontend_analysis_{timestamp}.html")
    
    cprint(f"\n✅ تحلیل با موفقیت انجام شد!", Colors.GREEN + Colors.BOLD)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n⏹️  متوقف شد.", Colors.YELLOW)
        sys.exit(0)
    except Exception as e:
        cprint(f"\n❌ خطای غیرمنتظره: {e}", Colors.RED)
        import traceback
        traceback.print_exc()
        sys.exit(1)
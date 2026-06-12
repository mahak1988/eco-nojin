#!/usr/bin/env python3
"""
=============================================================================
Econojin Project Comprehensive Analyzer
تحلیل‌گر جامع پروژه Econojin
=============================================================================
این اسکریپت کل پروژه را اسکن می‌کند و گزارش کاملی از:
- ساختار ماژول‌ها
- API endpoints
- جداول دیتابیس
- نقش‌ها و دسترسی‌ها
- مخاطبان احتمالی
- ارتباط بین ماژول‌ها
تهیه می‌کند.
=============================================================================
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass, field, asdict


@dataclass
class ModuleInfo:
    """اطلاعات یک ماژول"""
    name: str
    path: str
    type: str  # 'backend', 'frontend', 'shared'
    has_router: bool = False
    has_models: bool = False
    has_schemas: bool = False
    has_service: bool = False
    endpoints: List[Dict] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    schemas: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class EndpointInfo:
    """اطلاعات یک API endpoint"""
    method: str
    path: str
    module: str
    function: str
    auth_required: bool = False
    roles: List[str] = field(default_factory=list)
    description: str = ""


@dataclass
class PageInfo:
    """اطلاعات یک صفحه frontend"""
    path: str
    file: str
    type: str  # 'page', 'layout', 'loading', 'error'
    is_dynamic: bool = False
    components_used: List[str] = field(default_factory=list)
    hooks_used: List[str] = field(default_factory=list)


@dataclass
class RoleInfo:
    """اطلاعات یک نقش کاربری"""
    name: str
    permissions: List[str] = field(default_factory=list)
    modules_access: List[str] = field(default_factory=list)


class ProjectAnalyzer:
    """تحلیل‌گر اصلی پروژه"""
    
    def __init__(self, project_root: str):
        self.root = Path(project_root)
        self.api_path = self.root / "api"
        self.apps_path = self.root / "apps"
        self.packages_path = self.root / "packages"
        
        # نتایج
        self.modules: Dict[str, ModuleInfo] = {}
        self.endpoints: List[EndpointInfo] = []
        self.pages: List[PageInfo] = []
        self.roles: Dict[str, RoleInfo] = {}
        self.database_models: Dict[str, List[str]] = {}
        self.dependencies_graph: Dict[str, Set[str]] = defaultdict(set)
        
        # الگوهای regex
        self.endpoint_pattern = re.compile(
            r'@(router|app)\.(get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']',
            re.IGNORECASE
        )
        self.class_pattern = re.compile(r'class\s+(\w+)\s*(?:\(|:)')
        self.import_pattern = re.compile(r'(?:from|import)\s+([\w\.]+)')
        self.function_pattern = re.compile(r'(?:async\s+)?def\s+(\w+)\s*\(')
        self.auth_pattern = re.compile(r'(?:@require_auth|@login_required|Depends\(.*auth)', re.IGNORECASE)
        self.role_pattern = re.compile(r'(?:role|permission|access)\s*[=:]\s*["\']?(\w+)["\']?', re.IGNORECASE)
        
    def analyze(self) -> Dict:
        """تحلیل کامل پروژه"""
        print("=" * 80)
        print("🔍 Econojin Project Analyzer - شروع تحلیل جامع")
        print("=" * 80)
        print(f"📁 مسیر پروژه: {self.root}")
        print()
        
        # مرحله ۱: اسکن ساختار کلی
        self._scan_project_structure()
        
        # مرحله ۲: تحلیل Backend
        self._analyze_backend()
        
        # مرحله ۳: تحلیل Frontend
        self._analyze_frontend()
        
        # مرحله ۴: تحلیل Packages مشترک
        self._analyze_packages()
        
        # مرحله ۵: تحلیل Authentication و Roles
        self._analyze_auth_and_roles()
        
        # مرحله ۶: تحلیل Database Models
        self._analyze_database_models()
        
        # مرحله ۷: شناسایی مخاطبان
        self._identify_audiences()
        
        # مرحله ۸: تحلیل ارتباطات
        self._analyze_connections()
        
        # مرحله ۹: تولید گزارش
        report = self._generate_report()
        
        print("\n" + "=" * 80)
        print("✅ تحلیل کامل شد!")
        print("=" * 80)
        
        return report
    
    def _scan_project_structure(self):
        """اسکن ساختار کلی پروژه"""
        print("📂 مرحله ۱: اسکن ساختار کلی...")
        
        # بررسی ریشه
        if not self.root.exists():
            raise FileNotFoundError(f"مسیر پروژه یافت نشد: {self.root}")
        
        # لیست دایرکتوری‌های سطح بالا
        top_dirs = [d.name for d in self.root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        print(f"   📁 دایرکتوری‌های سطح بالا: {', '.join(top_dirs)}")
        
        # بررسی فایل‌های مهم
        important_files = [
            'package.json', 'pyproject.toml', 'requirements.txt',
            'docker-compose.yml', 'README.md', '.env', '.env.example'
        ]
        
        for f in important_files:
            if (self.root / f).exists():
                print(f"   ✅ {f} یافت شد")
    
    def _analyze_backend(self):
        """تحلیل کامل Backend"""
        print("\n🔧 مرحله ۲: تحلیل Backend...")
        
        if not self.api_path.exists():
            print("   ⚠️  پوشه api/ یافت نشد")
            return
        
        # اسکن ماژول‌ها
        modules_path = self.api_path / "modules"
        if modules_path.exists():
            for module_dir in modules_path.iterdir():
                if module_dir.is_dir() and not module_dir.name.startswith('_'):
                    self._analyze_backend_module(module_dir)
        
        # تحلیل فایل main.py
        main_file = self.api_path / "main.py"
        if main_file.exists():
            self._analyze_main_file(main_file)
        
        print(f"   ✅ {len(self.modules)} ماژول backend شناسایی شد")
        print(f"   ✅ {len(self.endpoints)} API endpoint شناسایی شد")
    
    def _analyze_backend_module(self, module_path: Path):
        """تحلیل یک ماژول backend"""
        module_name = module_path.name
        module = ModuleInfo(
            name=module_name,
            path=str(module_path.relative_to(self.root)),
            type='backend'
        )
        
        # بررسی فایل‌های موجود
        files = {f.name: f for f in module_path.iterdir() if f.is_file()}
        
        module.has_router = 'router.py' in files
        module.has_models = 'models.py' in files
        module.has_schemas = 'schemas.py' in files
        module.has_service = 'service.py' in files
        
        # استخراج endpoints از router.py
        if module.has_router:
            module.endpoints = self._extract_endpoints(files['router.py'], module_name)
        
        # استخراج models
        if module.has_models:
            module.models = self._extract_classes(files['models.py'])
        
        # استخراج schemas
        if module.has_schemas:
            module.schemas = self._extract_classes(files['schemas.py'])
        
        # استخراج description از docstring
        if module.has_service:
            module.description = self._extract_module_description(files['service.py'])
        
        self.modules[module_name] = module
    
    def _extract_endpoints(self, file_path: Path, module_name: str) -> List[Dict]:
        """استخراج endpoints از فایل router"""
        endpoints = []
        try:
            content = file_path.read_text(encoding='utf-8')
            
            for match in self.endpoint_pattern.finditer(content):
                method = match.group(2).upper()
                path = match.group(3)
                
                # پیدا کردن تابع مربوطه
                pos = match.end()
                func_match = re.search(r'async\s+def\s+(\w+)|def\s+(\w+)', content[pos:pos+500])
                func_name = func_match.group(1) or func_match.group(2) if func_match else "unknown"
                
                # بررسی auth
                func_content = content[pos:pos+1000]
                auth_required = bool(self.auth_pattern.search(func_content))
                
                # استخراج roles
                roles = list(set(self.role_pattern.findall(func_content)))
                
                endpoints.append({
                    'method': method,
                    'path': path,
                    'function': func_name,
                    'auth_required': auth_required,
                    'roles': roles
                })
                
                # اضافه کردن به لیست کلی
                self.endpoints.append(EndpointInfo(
                    method=method,
                    path=path,
                    module=module_name,
                    function=func_name,
                    auth_required=auth_required,
                    roles=roles
                ))
        except Exception as e:
            print(f"   ⚠️  خطا در خواندن {file_path}: {e}")
        
        return endpoints
    
    def _extract_classes(self, file_path: Path) -> List[str]:
        """استخراج نام کلاس‌ها از فایل"""
        classes = []
        try:
            content = file_path.read_text(encoding='utf-8')
            classes = self.class_pattern.findall(content)
        except Exception as e:
            print(f"   ⚠️  خطا در استخراج کلاس‌ها از {file_path}: {e}")
        return classes
    
    def _extract_module_description(self, file_path: Path) -> str:
        """استخراج توضیحات ماژول"""
        try:
            content = file_path.read_text(encoding='utf-8')
            # پیدا کردن docstring ابتدای فایل
            match = re.search(r'"""(.*?)"""|\'\'\'(.*?)\'\'\'', content, re.DOTALL)
            if match:
                return (match.group(1) or match.group(2) or "").strip()[:200]
        except:
            pass
        return ""
    
    def _analyze_main_file(self, main_file: Path):
        """تحلیل فایل main.py"""
        try:
            content = main_file.read_text(encoding='utf-8')
            
            # پیدا کردن routerهای ثبت شده
            router_pattern = re.compile(r'(?:app|router)\.include_router\s*\(\s*([\w_]+)')
            routers = router_pattern.findall(content)
            
            print(f"   📡 Routerهای ثبت شده در main: {len(routers)}")
            
        except Exception as e:
            print(f"   ⚠️  خطا در تحلیل main.py: {e}")
    
    def _analyze_frontend(self):
        """تحلیل کامل Frontend"""
        print("\n🎨 مرحله ۳: تحلیل Frontend...")
        
        web_app = self.apps_path / "web" / "src" / "app"
        if not web_app.exists():
            print("   ⚠️  مسیر apps/web/src/app یافت نشد")
            return
        
        # اسکن تمام صفحات
        for page_file in web_app.rglob("page.tsx"):
            self._analyze_page(page_file, web_app)
        
        # اسکن layouts
        layout_count = len(list(web_app.rglob("layout.tsx")))
        
        # اسکن کامپوننت‌ها
        components_path = self.apps_path / "web" / "src" / "components"
        component_count = 0
        if components_path.exists():
            component_count = len(list(components_path.rglob("*.tsx")))
        
        # اسکن hooks
        hooks_path = self.apps_path / "web" / "src" / "hooks"
        hook_count = 0
        if hooks_path.exists():
            hook_count = len(list(hooks_path.rglob("*.ts"))) + len(list(hooks_path.rglob("*.tsx")))
        
        # اسکن stores
        stores_path = self.apps_path / "web" / "src" / "store"
        store_count = 0
        if stores_path.exists():
            store_count = len(list(stores_path.rglob("*.ts")))
        
        print(f"   📄 {len(self.pages)} صفحه شناسایی شد")
        print(f"   🧩 {component_count} کامپوننت")
        print(f"   🪝 {hook_count} هوک")
        print(f"   🗄️  {store_count} store")
        print(f"   📐 {layout_count} layout")
    
    def _analyze_page(self, page_file: Path, app_root: Path):
        """تحلیل یک صفحه"""
        try:
            relative_path = page_file.parent.relative_to(app_root)
            path_str = str(relative_path).replace('\\', '/')
            
            # بررسی dynamic route
            is_dynamic = '[' in path_str
            
            # خواندن محتوا
            content = page_file.read_text(encoding='utf-8')
            
            # استخراج imports
            components = re.findall(r'import\s+\{?\s*([A-Z]\w+)', content)
            hooks = re.findall(r'use(\w+)', content)
            
            page = PageInfo(
                path=path_str,
                file=str(page_file.relative_to(self.root)),
                type='page',
                is_dynamic=is_dynamic,
                components_used=list(set(components))[:10],
                hooks_used=list(set(hooks))[:10]
            )
            
            self.pages.append(page)
            
        except Exception as e:
            print(f"   ⚠️  خطا در تحلیل {page_file}: {e}")
    
    def _analyze_packages(self):
        """تحلیل packages مشترک"""
        print("\n📦 مرحله ۴: تحلیل Packages مشترک...")
        
        if not self.packages_path.exists():
            print("   ⚠️  پوشه packages/ یافت نشد")
            return
        
        for pkg_dir in self.packages_path.iterdir():
            if pkg_dir.is_dir() and not pkg_dir.name.startswith('.'):
                pkg_json = pkg_dir / "package.json"
                if pkg_json.exists():
                    try:
                        data = json.loads(pkg_json.read_text(encoding='utf-8'))
                        print(f"   📦 {pkg_dir.name}: {data.get('name', 'N/A')}")
                    except:
                        print(f"   📦 {pkg_dir.name}")
    
    def _analyze_auth_and_roles(self):
        """تحلیل سیستم احراز هویت و نقش‌ها"""
        print("\n🔐 مرحله ۵: تحلیل Auth و Roles...")
        
        # جستجو در فایل‌های backend
        auth_files = []
        for pattern in ['**/auth*.py', '**/middleware*.py', '**/permissions*.py', '**/roles*.py']:
            auth_files.extend(self.api_path.glob(pattern))
        
        for auth_file in auth_files:
            try:
                content = auth_file.read_text(encoding='utf-8')
                
                # پیدا کردن نقش‌ها
                roles_found = re.findall(r'(?:class|ROLE|role)\s*=?\s*["\']?(\w+)["\']?', content)
                for role in roles_found:
                    if role not in self.roles and len(role) > 2:
                        self.roles[role] = RoleInfo(name=role)
                
            except:
                pass
        
        # جستجو در frontend
        auth_ts_files = []
        web_src = self.apps_path / "web" / "src"
        if web_src.exists():
            for pattern in ['**/auth*.ts', '**/auth*.tsx', '**/permissions*.ts']:
                auth_ts_files.extend(web_src.glob(pattern))
        
        print(f"   🔑 {len(self.roles)} نقش شناسایی شد")
        print(f"   📄 {len(auth_files)} فایل auth در backend")
        print(f"   📄 {len(auth_ts_files)} فایل auth در frontend")
    
    def _analyze_database_models(self):
        """تحلیل مدل‌های دیتابیس"""
        print("\n💾 مرحله ۶: تحلیل Database Models...")
        
        for module_name, module in self.modules.items():
            if module.has_models:
                models_file = self.root / module.path / "models.py"
                if models_file.exists():
                    models = self._extract_classes(models_file)
                    self.database_models[module_name] = models
    
    def _identify_audiences(self):
        """شناسایی مخاطبان بر اساس ماژول‌ها"""
        print("\n👥 مرحله ۷: شناسایی مخاطبان...")
        
        audiences = {
            'کشاورز': [],
            'مدیر مزرعه': [],
            'کارشناس کشاورزی': [],
            'حسابدار': [],
            'مدیر فروش': [],
            'مدیر ارشد': [],
            'مشتری': [],
            'توسعه‌دهنده': [],
        }
        
        # نگاشت ماژول‌ها به مخاطبان
        module_audience_map = {
            'accounting': ['حسابدار', 'مدیر ارشد'],
            'financial': ['حسابدار', 'مدیر ارشد'],
            'inventory': ['مدیر مزرعه', 'حسابدار'],
            'shop': ['مشتری', 'مدیر فروش'],
            'soil_water': ['کارشناس کشاورزی', 'کشاورز'],
            'gis': ['کارشناس کشاورزی'],
            'satellite': ['کارشناس کشاورزی'],
            'iot': ['مدیر مزرعه', 'کارشناس کشاورزی'],
            'weather': ['کشاورز', 'کارشناس کشاورزی'],
            'academy': ['کشاورز', 'کارشناس کشاورزی'],
            'blockchain': ['توسعه‌دهنده', 'مدیر ارشد'],
            'carbon': ['مدیر ارشد', 'کارشناس کشاورزی'],
            'drought': ['کارشناس کشاورزی', 'مدیر مزرعه'],
            'forest': ['کارشناس کشاورزی'],
        }
        
        for module_name, audience_list in module_audience_map.items():
            if module_name in self.modules:
                for audience in audience_list:
                    if audience in audiences:
                        audiences[audience].append(module_name)
        
        # چاپ نتایج
        for audience, modules in audiences.items():
            if modules:
                print(f"   👤 {audience}: {', '.join(modules)}")
        
        self.audiences = audiences
    
    def _analyze_connections(self):
        """تحلیل ارتباطات بین ماژول‌ها"""
        print("\n🔗 مرحله ۸: تحلیل ارتباطات بین ماژول‌ها...")
        
        for module_name, module in self.modules.items():
            # بررسی imports در فایل‌های ماژول
            module_dir = self.root / module.path
            for py_file in module_dir.glob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8')
                    imports = self.import_pattern.findall(content)
                    
                    for imp in imports:
                        if 'api.modules.' in imp:
                            # استخراج نام ماژول مرجع
                            parts = imp.split('.')
                            if len(parts) >= 3 and parts[2] != module_name:
                                self.dependencies_graph[module_name].add(parts[2])
                except:
                    pass
        
        connections_count = sum(len(deps) for deps in self.dependencies_graph.values())
        print(f"   🔗 {connections_count} وابستگی بین ماژول‌ها شناسایی شد")
    
    def _generate_report(self) -> Dict:
        """تولید گزارش نهایی"""
        print("\n📊 مرحله ۹: تولید گزارش...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'project_root': str(self.root),
            'summary': {
                'backend_modules': len(self.modules),
                'frontend_pages': len(self.pages),
                'api_endpoints': len(self.endpoints),
                'database_models': sum(len(m) for m in self.database_models.values()),
                'user_roles': len(self.roles),
                'audiences_identified': len([a for a, m in self.audiences.items() if m]),
            },
            'modules': {name: asdict(module) for name, module in self.modules.items()},
            'endpoints': [asdict(ep) for ep in self.endpoints],
            'pages': [asdict(page) for page in self.pages],
            'roles': {name: asdict(role) for name, role in self.roles.items()},
            'database_models': self.database_models,
            'audiences': self.audiences,
            'dependencies': {k: list(v) for k, v in self.dependencies_graph.items()},
        }
        
        # ذخیره JSON
        json_file = self.root / "project-analysis.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        print(f"   💾 گزارش JSON ذخیره شد: {json_file}")
        
        # ذخیره Markdown
        md_file = self.root / "PROJECT-ANALYSIS.md"
        self._save_markdown_report(report, md_file)
        print(f"   💾 گزارش Markdown ذخیره شد: {md_file}")
        
        return report
    
    def _save_markdown_report(self, report: Dict, file_path: Path):
        """ذخیره گزارش به فرمت Markdown"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# 📊 گزارش تحلیل جامع پروژه Econojin\n\n")
            f.write(f"**تاریخ تحلیل:** {report['timestamp']}\n\n")
            
            # خلاصه
            f.write("## 📈 خلاصه آماری\n\n")
            f.write("| شاخص | تعداد |\n")
            f.write("|------|-------|\n")
            for key, value in report['summary'].items():
                f.write(f"| {key} | {value} |\n")
            f.write("\n")
            
            # ماژول‌ها
            f.write("## 🧩 ماژول‌های Backend\n\n")
            for name, module in report['modules'].items():
                f.write(f"### 📦 {name}\n")
                f.write(f"- **مسیر:** `{module['path']}`\n")
                if module['description']:
                    f.write(f"- **توضیحات:** {module['description']}\n")
                f.write(f"- **فایل‌ها:** Router: {'✅' if module['has_router'] else '❌'}, ")
                f.write(f"Models: {'✅' if module['has_models'] else '❌'}, ")
                f.write(f"Schemas: {'✅' if module['has_schemas'] else '❌'}, ")
                f.write(f"Service: {'✅' if module['has_service'] else '❌'}\n")
                
                if module['models']:
                    f.write(f"- **مدل‌ها:** {', '.join(module['models'][:5])}\n")
                if module['endpoints']:
                    f.write(f"- **Endpoints:** {len(module['endpoints'])} عدد\n")
                    for ep in module['endpoints'][:5]:
                        auth_mark = "🔒" if ep['auth_required'] else "🔓"
                        f.write(f"  - `{ep['method']} {ep['path']}` {auth_mark}\n")
                f.write("\n")
            
            # مخاطبان
            f.write("## 👥 مخاطبان شناسایی‌شده\n\n")
            for audience, modules in report['audiences'].items():
                if modules:
                    f.write(f"### 👤 {audience}\n")
                    f.write(f"**ماژول‌های مرتبط:** {', '.join(modules)}\n\n")
            
            # صفحات Frontend
            f.write("## 🎨 صفحات Frontend\n\n")
            f.write("| مسیر | داینامیک | کامپوننت‌ها |\n")
            f.write("|------|----------|-------------|\n")
            for page in report['pages'][:30]:
                dynamic = "✅" if page['is_dynamic'] else "❌"
                comps = ', '.join(page['components_used'][:3]) or '-'
                f.write(f"| `{page['path']}` | {dynamic} | {comps} |\n")
            if len(report['pages']) > 30:
                f.write(f"\n*... و {len(report['pages']) - 30} صفحه دیگر*\n")
            f.write("\n")
            
            # وابستگی‌ها
            f.write("## 🔗 وابستگی‌های بین ماژول‌ها\n\n")
            for module, deps in report['dependencies'].items():
                if deps:
                    f.write(f"- **{module}** ← {', '.join(deps)}\n")
            f.write("\n")
            
            # پیشنهادات
            f.write("## 💡 پیشنهادات توسعه\n\n")
            f.write("### ماژول‌های با اولویت بالا (بر اساس تعداد endpoints و وابستگی‌ها):\n")
            module_priority = sorted(
                report['modules'].items(),
                key=lambda x: len(x[1]['endpoints']) + len(x[1].get('dependencies', [])),
                reverse=True
            )
            for i, (name, module) in enumerate(module_priority[:5], 1):
                f.write(f"{i}. **{name}** - {len(module['endpoints'])} endpoint\n")
            f.write("\n")


def main():
    """تابع اصلی"""
    import sys
    
    # مسیر پیش‌فرض
    project_root = sys.argv[1] if len(sys.argv) > 1 else r"D:\econojin.com"
    
    try:
        analyzer = ProjectAnalyzer(project_root)
        report = analyzer.analyze()
        
        print("\n" + "=" * 80)
        print("📊 خلاصه نهایی:")
        print("=" * 80)
        for key, value in report['summary'].items():
            print(f"  • {key}: {value}")
        print("=" * 80)
        print("\n✅ گزارش‌های کامل ذخیره شدند:")
        print("   📄 PROJECT-ANALYSIS.md")
        print("   📄 project-analysis.json")
        print("\n🎯 گام بعدی:")
        print("   1. فایل PROJECT-ANALYSIS.md را مطالعه کنید")
        print("   2. ماژول‌های اولویت‌دار را مشخص کنید")
        print("   3. برای هر ماژول، سند هویت جداگانه بنویسید")
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
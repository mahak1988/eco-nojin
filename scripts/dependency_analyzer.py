#!/usr/bin/env python3
"""
Dependency Analyzer - فاز ۲
تحلیل وابستگی‌ها، شناسایی وابستگی‌های چرخشی، و گراف وابستگی‌ها
"""

import ast
import os
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class ModuleInfo:
    """اطلاعات یک ماژول"""
    path: Path
    name: str
    imports: Set[str] = field(default_factory=set)
    imported_by: Set[str] = field(default_factory=set)
    is_orphan: bool = False
    layer: str = ""  # modules, domains, services, routers, etc.


@dataclass
class DependencyGraph:
    """گراف وابستگی‌ها"""
    modules: Dict[str, ModuleInfo] = field(default_factory=dict)
    circular_deps: List[List[str]] = field(default_factory=list)
    layers: Dict[str, Set[str]] = field(default_factory=lambda: defaultdict(set))


class DependencyAnalyzer:
    """تحلیلگر وابستگی‌ها"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.graph = DependencyGraph()
        
        # الگوهای regex برای TypeScript/JavaScript
        self.ts_import_pattern = re.compile(
            r'(?:import|from)\s+[\'"]([^\'"]+)[\'"]',
            re.MULTILINE
        )
        
    def analyze_python_file(self, file_path: Path) -> Set[str]:
        """تحلیل import های فایل Python با ast"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            print(f"⚠️  خطا در parse کردن {file_path}: {e}", file=sys.stderr)
        
        return imports
    
    def analyze_ts_js_file(self, file_path: Path) -> Set[str]:
        """تحلیل import های فایل TypeScript/JavaScript با regex"""
        imports = set()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for match in self.ts_import_pattern.finditer(content):
                import_path = match.group(1)
                # فقط import های نسبی یا داخلی
                if import_path.startswith('.') or not import_path.startswith(('node:', 'http:', 'https:')):
                    # استخراج نام ماژول اصلی
                    module_name = import_path.split('/')[0].lstrip('.')
                    if module_name:
                        imports.add(module_name)
        except Exception as e:
            print(f"⚠️  خطا در parse کردن {file_path}: {e}", file=sys.stderr)
        
        return imports
    
    def get_layer(self, file_path: Path) -> str:
        """تعیین لایه فایل (modules, domains, services, routers, etc.)"""
        rel_path = file_path.relative_to(self.project_root)
        parts = rel_path.parts
        
        # برای apps/api
        if len(parts) >= 3 and parts[0] == 'apps' and parts[1] == 'api':
            if len(parts) >= 4:
                return parts[3]  # modules, domains, services, routers, etc.
        
        # برای apps/simulation
        if len(parts) >= 3 and parts[0] == 'apps' and parts[1] == 'simulation':
            if len(parts) >= 4:
                return parts[3]  # hydrology, soil, energy, etc.
        
        # برای apps/web
        if len(parts) >= 3 and parts[0] == 'apps' and parts[1] == 'web':
            if len(parts) >= 3:
                return parts[2]  # app, components, lib, etc.
        
        return "other"
    
    def scan_project(self):
        """اسکن کل پروژه و ساخت گراف وابستگی‌ها"""
        print("🔍 در حال اسکن پروژه...")
        
        # پیدا کردن تمام فایل‌های کد
        code_files = []
        for ext in ['*.py', '*.ts', '*.tsx', '*.js', '*.jsx']:
            code_files.extend(self.project_root.rglob(ext))
        
        # حذف فایل‌های node_modules و venv
        code_files = [
            f for f in code_files
            if 'node_modules' not in str(f) and '.venv' not in str(f) and 'venv' not in str(f)
        ]
        
        print(f"📁 پیدا شد {len(code_files)} فایل کد")
        
        # تحلیل هر فایل
        for file_path in code_files:
            rel_path = file_path.relative_to(self.project_root)
            module_name = rel_path.stem
            
            # تعیین لایه
            layer = self.get_layer(file_path)
            
            # ایجاد ModuleInfo
            module_info = ModuleInfo(
                path=file_path,
                name=module_name,
                layer=layer
            )
            
            # تحلیل import ها
            if file_path.suffix == '.py':
                imports = self.analyze_python_file(file_path)
            else:
                imports = self.analyze_ts_js_file(file_path)
            
            module_info.imports = imports
            self.graph.modules[module_name] = module_info
            self.graph.layers[layer].add(module_name)
        
        print(f"✅ تحلیل {len(self.graph.modules)} ماژول کامل شد")
        
        # ساخت imported_by
        self._build_imported_by()
        
        # شناسایی فایل‌های یتیم
        self._find_orphans()
        
        # شناسایی وابستگی‌های چرخشی
        self._find_circular_dependencies()
    
    def _build_imported_by(self):
        """ساخت رابطه imported_by"""
        for module_name, module_info in self.graph.modules.items():
            for import_name in module_info.imports:
                if import_name in self.graph.modules:
                    self.graph.modules[import_name].imported_by.add(module_name)
    
    def _find_orphans(self):
        """شناسایی فایل‌های یتیم (فایل‌هایی که هیچ‌جا import نشده‌اند)"""
        for module_name, module_info in self.graph.modules.items():
            # فایل یتیم است اگر:
            # 1. هیچ‌جا import نشده باشد
            # 2. فایل اصلی نباشد (main, __init__, etc.)
            if (not module_info.imported_by and 
                module_name not in ['main', '__init__', 'index', 'app'] and
                not module_name.startswith('test_')):
                module_info.is_orphan = True
    
    def _find_circular_dependencies(self):
        """شناسایی وابستگی‌های چرخشی با DFS"""
        print("🔍 در حال شناسایی وابستگی‌های چرخشی...")
        
        visited = set()
        rec_stack = set()
        path = []
        
        def dfs(node: str):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            if node in self.graph.modules:
                for neighbor in self.graph.modules[node].imports:
                    if neighbor not in visited and neighbor in self.graph.modules:
                        dfs(neighbor)
                    elif neighbor in rec_stack:
                        # پیدا کردن چرخه
                        cycle_start = path.index(neighbor)
                        cycle = path[cycle_start:] + [neighbor]
                        self.graph.circular_deps.append(cycle)
            
            path.pop()
            rec_stack.remove(node)
        
        for module_name in self.graph.modules:
            if module_name not in visited:
                dfs(module_name)
        
        print(f"⚠️  پیدا شد {len(self.graph.circular_deps)} وابستگی چرخشی")
    
    def generate_report(self) -> str:
        """تولید گزارش متنی"""
        lines = []
        lines.append("=" * 80)
        lines.append("📊 گزارش تحلیل وابستگی‌ها")
        lines.append("=" * 80)
        lines.append("")
        
        # آمار کلی
        lines.append(f"📈 آمار کلی:")
        lines.append(f"   • تعداد ماژول‌ها: {len(self.graph.modules)}")
        lines.append(f"   • تعداد لایه‌ها: {len(self.graph.layers)}")
        lines.append(f"   • تعداد وابستگی‌های چرخشی: {len(self.graph.circular_deps)}")
        lines.append(f"   • تعداد فایل‌های یتیم: {sum(1 for m in self.graph.modules.values() if m.is_orphan)}")
        lines.append("")
        
        # آمار لایه‌ها
        lines.append("📚 آمار لایه‌ها:")
        for layer, modules in sorted(self.graph.layers.items()):
            lines.append(f"   • {layer}: {len(modules)} ماژول")
        lines.append("")
        
        # وابستگی‌های چرخشی
        if self.graph.circular_deps:
            lines.append("🔄 وابستگی‌های چرخشی:")
            for i, cycle in enumerate(self.graph.circular_deps[:10], 1):
                lines.append(f"   {i}. {' → '.join(cycle)}")
            if len(self.graph.circular_deps) > 10:
                lines.append(f"   ... و {len(self.graph.circular_deps) - 10} مورد دیگر")
            lines.append("")
        
        # فایل‌های یتیم
        orphans = [m for m in self.graph.modules.values() if m.is_orphan]
        if orphans:
            lines.append("👻 فایل‌های یتیم (import نشده):")
            for module in sorted(orphans, key=lambda m: m.name)[:20]:
                lines.append(f"   • {module.name} ({module.layer})")
            if len(orphans) > 20:
                lines.append(f"   ... و {len(orphans) - 20} مورد دیگر")
            lines.append("")
        
        # ماژول‌های با بیشترین وابستگی
        lines.append("🔗 ماژول‌های با بیشترین وابستگی:")
        sorted_modules = sorted(
            self.graph.modules.values(),
            key=lambda m: len(m.imports),
            reverse=True
        )
        for module in sorted_modules[:10]:
            lines.append(f"   • {module.name}: {len(module.imports)} import")
        lines.append("")
        
        # ماژول‌های با بیشترین imported_by
        lines.append("🎯 ماژول‌های با بیشترین استفاده:")
        sorted_modules = sorted(
            self.graph.modules.values(),
            key=lambda m: len(m.imported_by),
            reverse=True
        )
        for module in sorted_modules[:10]:
            lines.append(f"   • {module.name}: {len(module.imported_by)} بار استفاده شده")
        lines.append("")
        
        return "\n".join(lines)
    
    def export_dot(self, output_file: Path):
        """export گراف به فرمت DOT (برای Graphviz)"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("digraph dependencies {\n")
            f.write("  rankdir=LR;\n")
            f.write("  node [shape=box];\n")
            f.write("\n")
            
            # رنگ‌بندی لایه‌ها
            layer_colors = {
                'modules': 'lightblue',
                'domains': 'lightgreen',
                'services': 'lightyellow',
                'routers': 'lightcoral',
                'core': 'lightgray',
                'app': 'lightpink',
            }
            
            # اضافه کردن ماژول‌ها
            for module_name, module_info in self.graph.modules.items():
                color = layer_colors.get(module_info.layer, 'white')
                f.write(f'  "{module_name}" [style=filled, fillcolor={color}];\n')
            
            f.write("\n")
            
            # اضافه کردن edges
            for module_name, module_info in self.graph.modules.items():
                for import_name in module_info.imports:
                    if import_name in self.graph.modules:
                        f.write(f'  "{module_name}" -> "{import_name}";\n')
            
            f.write("}\n")
        
        print(f"✅ گراف DOT ذخیره شد در: {output_file}")


def main():
    """تابع اصلی"""
    if len(sys.argv) < 2:
        print("Usage: python dependency_analyzer.py <project_root>")
        sys.exit(1)
    
    project_root = Path(sys.argv[1])
    if not project_root.exists():
        print(f"❌ مسیر {project_root} وجود ندارد")
        sys.exit(1)
    
    # ایجاد تحلیلگر
    analyzer = DependencyAnalyzer(project_root)
    
    # اسکن پروژه
    analyzer.scan_project()
    
    # تولید گزارش
    report = analyzer.generate_report()
    print(report)
    
    # ذخیره گزارش
    report_file = project_root / "dependency_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ گزارش ذخیره شد در: {report_file}")
    
    # export DOT
    dot_file = project_root / "dependency_graph.dot"
    analyzer.export_dot(dot_file)
    
    print("\n💡 برای مشاهده گراف گرافیکی:")
    print("   dot -Tpng dependency_graph.dot -o dependency_graph.png")


if __name__ == "__main__":
    main()
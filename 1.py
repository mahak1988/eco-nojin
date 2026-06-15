import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List

class EcoTechMonorepoAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        
        # لیست سیاه دایرکتوری‌ها برای جلوگیری از اسکن فایل‌های بک‌آپ و کش (محاسبات سبز)
        self.blacklist_dirs = {
            '.venv', 'node_modules', '__pycache__', '.git', '.next', 'dist', 'build',
            '.pnpm-store', '.turbo', '.mypy_cache', '.pytest_cache', '.blackbox',
            '_QUARANTINE', 'analysis_reports', 'structure_reports', 'output', 'uploads'
        }
        # الگوی regex برای حذف پویای تمام پوشه‌های بک‌آپ انباشته شده
        self.backup_pattern = re.compile(r'^_backup_.*')
        
        # مسیرهای هدف دقیق بر اساس توپولوژی کشف‌شده پروژه econojin.com
        self.target_paths = {
            "frontend": ["apps/web", "apps/cms", "apps/library", "packages"],
            "backend": ["api", "apps/api", "backend", "core", "models", "database", "alembic"],
            "ai_agents": ["agents", "knowledge_hub"]
        }

        self.report = {
            "project_path": str(self.project_path),
            "architecture_type": "Monorepo (Next.js + FastAPI + AI Agents)",
            "frontend_analysis": {},
            "python_backend_analysis": {},
            "ai_agent_analysis": {},
            "sustainability_score": 0,
            "strategic_recommendations": []
        }

    def _is_blacklisted(self, dir_name: str) -> bool:
        """بررسی می‌کند که آیا یک دایرکتوری باید از چرخه اسکن حذف شود یا خیر"""
        if dir_name in self.blacklist_dirs:
            return True
        if self.backup_pattern.match(dir_name):
            return True
        return False

    def _search_files(self, target_dirs: List[str], extensions: tuple) -> List[str]:
        """جستجوی بهینه در مسیرهای هدف با اعمال لیست سیاه در سطح درخت"""
        contents = []
        for target_dir in target_dirs:
            dir_path = self.project_path / target_dir
            if not dir_path.exists():
                continue
                
            for root, dirs, files in os.walk(dir_path):
                # حذف دایرکتوری‌های لیست سیاه قبل از ورود به آن‌ها (کاهش شدید I/O)
                dirs[:] = [d for d in dirs if not self._is_blacklisted(d)]
                
                for file in files:
                    if file.endswith(extensions):
                        try:
                            with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                                contents.append(f.read().lower())
                        except Exception:
                            continue
        return contents

    def analyze_frontend(self) -> Dict[str, Any]:
        metrics = {
            "framework": "Unknown",
            "monorepo_packages_detected": 0,
            "eco_dashboard_components": 0,
            "state_management": "None",
            "issues": []
        }
        
        contents = self._search_files(self.target_paths["frontend"], ('.js', '.jsx', '.ts', '.tsx'))
        
        if not contents:
            metrics["issues"].append("هیچ فایل فرانت‌اندی در مسیرهای apps/ و packages/ یافت نشد.")
        else:
            for content in contents:
                if 'next' in content: metrics["framework"] = "Next.js (SSR/SSG)"
                elif 'react' in content: metrics["framework"] = "React"
                
                # شناسایی ساختار Monorepo و پکیج‌های مشترک
                if 'workspace:' in content or '"name": "@econojin/' in content: 
                    metrics["monorepo_packages_detected"] += 1
                
                # کامپوننت‌های بصری‌سازی داده‌های اکولوژیکی و نقشه‌ها
                if any(lib in content for lib in ['recharts', 'd3', 'mapbox', 'leaflet', 'chart.js', 'nivo', 'deck.gl']):
                    metrics["eco_dashboard_components"] += 1
                    
                # مدیریت State (فرانت‌اند و سرور)
                if any(state in content for state in ['zustand', 'redux', 'jotai', 'recoil', 'swr', 'react-query', '@tanstack/query']):
                    metrics["state_management"] = "Advanced (Client/Server State)"

        if metrics["eco_dashboard_components"] == 0:
            metrics["issues"].append("عدم شناسایی کتابخانه‌های بصری‌سازی داده‌های محیطی (Data Visualization).")
            
        self.report["frontend_analysis"] = metrics
        return metrics

    def analyze_python_backend(self) -> Dict[str, Any]:
        metrics = {
            "framework": "Unknown",
            "scientific_libs": [],
            "green_computing_flags": 0,
            "database_orm": "Unknown",
            "issues": []
        }
        
        contents = self._search_files(self.target_paths["backend"], ('.py',))
        
        if not contents:
            metrics["issues"].append("هیچ فایل بک‌اندی در مسیرهای api/ و core/ یافت نشد.")
        else:
            scientific_keywords = ['geopandas', 'scipy', 'numpy', 'pandas', 'xarray', 'rasterio', 'shapely']
            green_keywords = ['asyncio', 'yield', 'multiprocessing', 'lru_cache', 'async def']
            orm_keywords = ['sqlalchemy', 'alembic', 'supabase', 'prisma', 'databases']
            
            for content in contents:
                if 'fastapi' in content: metrics["framework"] = "FastAPI (High Performance)"
                elif 'django' in content: metrics["framework"] = "Django"
                
                for lib in scientific_keywords:
                    if f"import {lib}" in content or f"from {lib}" in content:
                        if lib not in metrics["scientific_libs"]: metrics["scientific_libs"].append(lib)
                        
                for kw in green_keywords:
                    if kw in content: metrics["green_computing_flags"] += 1
                    
                for orm in orm_keywords:
                    if orm in content: metrics["database_orm"] = orm.capitalize()

        if not metrics["scientific_libs"]:
            metrics["issues"].append("عدم استفاده از کتابخانه‌های تحلیل داده‌های مکانی/اکولوژیکی.")
            
        self.report["python_backend_analysis"] = metrics
        return metrics

    def analyze_ai_agents(self) -> Dict[str, Any]:
        metrics = {
            "agent_framework_detected": False,
            "rag_implementation": False,
            "llm_providers": [],
            "context_management": "Basic",
            "domain_specific_prompts": 0,
            "issues": []
        }
        
        # اسکن کل پروژه (با لیست سیاه) برای یافتن تمام فایل‌های مرتبط با AI و پرامپت‌ها
        all_contents = self._search_files(["."], ('.py', '.md', '.json', '.yaml', '.yml', '.txt'))
        
        ai_keywords = ['langchain', 'llama_index', 'llamaindex', 'openai', 'anthropic', 'huggingface', 'autogen', 'crewai']
        rag_keywords = ['rag', 'retrieval', 'vectorstore', 'chromadb', 'pinecone', 'weaviate', 'qdrant', 'embedding']
        eco_prompts = ['کشاورزی', 'اکوسیستم', 'آب', 'خاک', 'ارگانیک', 'پایش', 'agriculture', 'ecosystem', 'water', 'soil']
        
        llm_providers_set = set()
        
        for content in all_contents:
            if any(kw in content for kw in ai_keywords): 
                metrics["agent_framework_detected"] = True
                
            if any(rag in content for rag in rag_keywords): 
                metrics["rag_implementation"] = True
                
            if 'memory' in content or 'session' in content or 'buffer' in content: 
                metrics["context_management"] = "Advanced"
                
            # شناسایی ارائه‌دهندگان مدل‌های زبانی (LLMs)
            if 'openai' in content: llm_providers_set.add("OpenAI")
            if 'anthropic' in content or 'claude' in content: llm_providers_set.add("Anthropic")
            if 'ollama' in content or 'llama' in content: llm_providers_set.add("Local/LLaMA")
            
            for prompt_kw in eco_prompts:
                if prompt_kw in content: 
                    metrics["domain_specific_prompts"] += 1

        metrics["llm_providers"] = list(llm_providers_set)

        if not metrics["rag_implementation"]:
            metrics["issues"].append("معماری RAG برای اتصال به پایگاه دانش تخصصی اکوسیستم شناسایی نشد.")
            
        self.report["ai_agent_analysis"] = metrics
        return metrics

    def calculate_sustainability_score(self) -> int:
        score = 0
        
        # فرانت‌اند (حداکثر 30 امتیاز)
        if self.report["frontend_analysis"].get("eco_dashboard_components", 0) > 0: score += 15
        if "Advanced" in self.report["frontend_analysis"].get("state_management", ""): score += 10
        if self.report["frontend_analysis"].get("monorepo_packages_detected", 0) > 0: score += 5
        
        # بک‌اند (حداکثر 35 امتیاز)
        score += min(len(self.report["python_backend_analysis"].get("scientific_libs", [])) * 5, 20)
        score += min(self.report["python_backend_analysis"].get("green_computing_flags", 0) * 2, 15)
        
        # هوش مصنوعی (حداکثر 35 امتیاز)
        if self.report["ai_agent_analysis"].get("rag_implementation"): score += 20
        if self.report["ai_agent_analysis"].get("agent_framework_detected"): score += 5
        # آستانه پرامپت‌ها را تعدیل می‌کنیم زیرا اکنون فقط کدهای زنده اسکن می‌شوند
        if self.report["ai_agent_analysis"].get("domain_specific_prompts", 0) > 10: score += 10 
        
        self.report["sustainability_score"] = min(score, 100)
        
        # توصیه‌های استراتژیک بر اساس امتیاز
        if self.report["sustainability_score"] < 50:
            self.report["strategic_recommendations"].append("توسعه داشبوردهای بصری‌سازی داده‌های محیطی و ارتقای معماری RAG.")
        elif self.report["sustainability_score"] < 80:
            self.report["strategic_recommendations"].append("افزایش استفاده از کتابخانه‌های علمی در بک‌اند و بهینه‌سازی مصرف منابع.")
        else:
            self.report["strategic_recommendations"].append("پروژه دارای معماری بلوغ‌یافته و پتانسیل بالای تجاری‌سازی در بازار AgriTech است.")
            
        # توصیه بحرانی و اختصاصی بر اساس توپولوژی کشف‌شده
        self.report["strategic_recommendations"].append("🚨 اقدام فوری مدیریتی: وجود ده‌ها پوشه بک‌آپ انباشته شده (_backup_...) باعث اتلاف منابع دیسک، پیچیدگی CI/CD و کندی عملیات Git می‌شود. انتقال فوری به سیستم کنترل نسخه استاندارد و پاکسازی فیزیکی این پوشه‌ها از ریشه پروژه الزامی است.")

        return self.report["sustainability_score"]

    def generate_and_save_report(self) -> None:
        print("🔄 در حال تحلیل معماری Monorepo با اعمال لیست سیاه... (لطفاً چند لحظه صبر کنید)")
        self.analyze_frontend()
        self.analyze_python_backend()
        self.analyze_ai_agents()
        self.calculate_sustainability_score()
        
        print("\n" + "="*70)
        print("🌿 گزارش تحلیلی سامانه اکوتکنولوژی (نسخه Monorepo-Aware) 🌿")
        print("="*70)
        print(json.dumps(self.report, indent=4, ensure_ascii=False))
        
        output_file = self.project_path / "eco_tech_monorepo_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=4, ensure_ascii=False)
        print(f"\n✅ گزارش دقیق در فایل '{output_file.name}' ذخیره گردید.")
        print("="*70 + "\n")

if __name__ == "__main__":
    CURRENT_PROJECT_PATH = r"D:\econojin.com"
    try:
        analyzer = EcoTechMonorepoAnalyzer(CURRENT_PROJECT_PATH)
        analyzer.generate_and_save_report()
    except Exception as e:
        print(f"❌ خطای سیستمی در تحلیل پروژه: {e}")
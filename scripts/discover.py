import os
from pathlib import Path

def discover_project_structure(project_path: str) -> None:
    print(f"🔍 در حال کشف توپولوژی پروژه در مسیر: {project_path}\n")
    
    root_dir = Path(project_path)
    
    # ۱. شناسایی پوشه‌های سطح اول (به استثنای محیط‌های مجازی و کش)
    print("📂 ساختار دایرکتوری سطح اول (Top-Level Directories):")
    exclude_dirs = {'.venv', '__pycache__', '.git', 'node_modules', '.next', 'dist', 'build'}
    for item in sorted(root_dir.iterdir()):
        if item.is_dir() and item.name not in exclude_dirs:
            print(f"   ├── 📁 {item.name}/")
            
    # ۲. جستجوی فایل‌های کلیدی برای تشخیص فریم‌ورک‌ها و معماری
    print("\n🔑 فایل‌های پیکربندی و نقطه ورود شناسایی‌شده (Key Config & Entry Points):")
    key_files = {
        'package.json': 'Frontend Ecosystem (Node.js/React/Vue)',
        'requirements.txt': 'Python Backend Dependencies',
        'Pipfile': 'Python Backend (Pipenv)',
        'pyproject.toml': 'Python Project Configuration',
        'manage.py': 'Django Backend Entry',
        'main.py': 'FastAPI / General Python App',
        'app.py': 'Flask / FastAPI App',
        'next.config.js': 'Next.js Frontend',
        'nuxt.config.js': 'Nuxt.js Frontend',
        'vite.config.js': 'Vite Frontend',
        'tsconfig.json': 'TypeScript Configuration'
    }
    
    found_frameworks = set()
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in key_files:
                rel_path = os.path.relpath(os.path.join(root, file), project_path)
                print(f"   ✅ {rel_path}  ➡️  {key_files[file]}")
                found_frameworks.add(key_files[file])

    print("\n📊 نتیجه‌گیری اولیه از معماری:")
    if found_frameworks:
        for fw in found_frameworks:
            print(f"   • {fw}")
    else:
        print("   ⚠️ هیچ فایل پیکربندی استانداردی شناسایی نشد.")

if __name__ == "__main__":
    CURRENT_PROJECT_PATH = r"D:\econojin.com"
    discover_project_structure(CURRENT_PROJECT_PATH)
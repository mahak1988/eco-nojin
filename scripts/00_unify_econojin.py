#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 Econojin - Unified Project Structure Setup
یکپارچه‌سازی کامل پروژه در ریشه D:\\econojin.com
"""
import os
import sys
import shutil
import json
from pathlib import Path

# مسیر ریشه پروژه
ROOT = Path(__file__).parent.resolve()
print(f"📁 مسیر ریشه پروژه: {ROOT}")


def write_file(path: Path, content: str) -> None:
    """کمک‌کننده برای نوشتن فایل با encoding صحیح"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def cleanup_old_structure() -> None:
    """حذف پوشه‌های تکراری و ساختارهای قدیمی"""
    items_to_remove = [
        ROOT / "econojin-super-platform",
        ROOT / "backend" / ".venv",
        ROOT / "frontend" / "node_modules",
        ROOT / "__pycache__",
        ROOT / "api" / "__pycache__",
    ]
    
    for item in items_to_remove:
        if item.exists():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
                print(f"🗑️ حذف پوشه: {item.name}")
            else:
                item.unlink(missing_ok=True)
                print(f"🗑️ حذف فایل: {item.name}")


def create_unified_structure() -> None:
    """ایجاد ساختار استاندارد و یکپارچه"""
    
    backend_modules = [
        "weather", "accounting", "calendar", "store", "library",
        "desktop", "education", "gis", "psychology", "telegram_bots",
        "ecomining", "community", "games", "infrastructure", "agents"
    ]
    
    frontend_pages = [
        "dashboard", "weather", "accounting", "calendar", "store",
        "library", "desktop", "education", "gis", "psychology",
        "ecomining", "community", "games", "settings", "auth"
    ]
    
    frontend_components = [
        "common", "charts", "maps", "forms", "tables", "modals"
    ]
    
    dirs = []
    
    # پوشه‌های بک‌اند
    for mod in backend_modules:
        dirs.append(ROOT / "api" / "modules" / mod)
    
    dirs.extend([
        ROOT / "api" / "core",
        ROOT / "api" / "agents" / "core",
        ROOT / "api" / "agents" / "agents",
        ROOT / "api" / "agents" / "managers",
        ROOT / "tests",
        ROOT / "scripts",
    ])
    
    # پوشه‌های فرانت‌اند
    for page in frontend_pages:
        dirs.append(ROOT / "web" / "src" / "app" / page)
    
    for comp in frontend_components:
        dirs.append(ROOT / "web" / "src" / "components" / comp)
    
    dirs.extend([
        ROOT / "web" / "public" / "icons",
        ROOT / "web" / "public" / "images",
        ROOT / "web" / "src" / "styles",
        ROOT / "docs" / "api",
        ROOT / "docs" / "user-guides",
        ROOT / "docs" / "developer-guides",
        ROOT / "infrastructure" / "docker",
        ROOT / "infrastructure" / "nginx",
        ROOT / "infrastructure" / "monitoring",
    ])
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    
    print(f"✅ {len(dirs)} پوشه اصلی ایجاد شد.")


def create_backend_files() -> None:
    """ایجاد فایل‌های پایه بک‌اند"""
    
    # main.py
    main_py = r'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛰️ Econojin Backend - Production Ready
پلتفرم جامع خدمات رایگان کشاورزی، آموزش و محیط زیست
"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.core.config import settings
from api.core.database import init_db
from api.agents.orchestrator import EconojinOrchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    app.state.orchestrator = EconojinOrchestrator()
    print(f"✅ Econojin v{settings.APP_VERSION} started")
    yield
    print("👋 Econojin shutting down")

app = FastAPI(
    title=settings.APP_NAME,
    description="🌍 ابرپروژه اکو نوژین - خدمات جامع رایگان",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "🛰️ Welcome to Econojin",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "status": "running"
    }

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "modules": 15,
        "agents": "active"
    }

# Import module routers
from api.modules.weather.router import router as weather_router
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])

from api.modules.accounting.router import router as accounting_router
app.include_router(accounting_router, prefix="/api/v1/accounting", tags=["Accounting"])

from api.modules.education.router import router as education_router
app.include_router(education_router, prefix="/api/v1/education", tags=["Education"])

from api.modules.gis.router import router as gis_router
app.include_router(gis_router, prefix="/api/v1/gis", tags=["GIS"])

from api.modules.ecomining.router import router as ecomining_router
app.include_router(ecomining_router, prefix="/api/v1/ecomining", tags=["EcoMining"])

from api.modules.psychology.router import router as psychology_router
app.include_router(psychology_router, prefix="/api/v1/psychology", tags=["Psychology"])

# Exception Handlers
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    return JSONResponse(
        status_code=422,
        content={"error": "درخواست نامعتبر", "details": [str(e) for e in exc.errors()]}
    )

@app.exception_handler(Exception)
async def global_error(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "خطای داخلی سرور", "detail": "لطفاً بعداً تلاش کنید"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
'''
    write_file(ROOT / "api" / "main.py", main_py)
    
    # config.py
    config_py = '''from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Econojin"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./econojin.db"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "*"]
    ECOIN_NETWORK: str = "testnet"
    ENABLE_LOCAL_LLM: bool = True
    LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"
    
    class Config:
        env_file = ".env"

settings = Settings()
'''
    write_file(ROOT / "api" / "core" / "config.py", config_py)
    
    # database.py
    database_py = '''import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()
engine = None
AsyncSessionLocal = None

async def init_db():
    global engine, AsyncSessionLocal
    from api.core.config import settings
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized")

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
'''
    write_file(ROOT / "api" / "core" / "database.py", database_py)
    
    # requirements.txt
    requirements_txt = '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
httpx>=0.26.0
structlog>=24.1.0
sqlalchemy[asyncio]>=2.0.0
aiosqlite>=0.20.0
websockets>=12.0
celery[redis]>=5.3.0
redis>=5.0.0
alembic>=1.13.0
'''
    write_file(ROOT / "requirements.txt", requirements_txt)
    
    # weather router sample
    weather_router = '''from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

@router.get("/forecast")
async def get_forecast(location: str = Query(..., description="نام منطقه"), days: int = Query(7, ge=1, le=14)):
    return {
        "location": location,
        "days": days,
        "forecast": "offline_cached_data",
        "source": "local_model"
    }

@router.get("/alerts")
async def get_agricultural_alerts(region: str):
    return {
        "region": region,
        "alerts": [],
        "last_updated": "2026-06-01T00:00:00Z"
    }
'''
    write_file(ROOT / "api" / "modules" / "weather" / "router.py", weather_router)
    
    # ایجاد __init__.py برای پوشه‌های پایتون
    for py_dir in (ROOT / "api").rglob("*"):
        if py_dir.is_dir() and not py_dir.name.startswith("."):
            (py_dir / "__init__.py").write_text("# Econojin Module\n", encoding="utf-8")
    
    print("📝 فایل‌های بک‌اند ایجاد شد.")


def create_frontend_files() -> None:
    """ایجاد فایل‌های پایه فرانت‌اند"""
    
    # package.json
    package_json = {
        "name": "econojin-web",
        "version": "2.0.0",
        "private": True,
        "scripts": {
            "dev": "next dev -p 3000",
            "build": "next build",
            "start": "next start",
            "lint": "next lint",
            "pwa": "next build && next export"
        },
        "dependencies": {
            "next": "14.2.5",
            "react": "18.3.1",
            "react-dom": "18.3.1",
            "recharts": "^2.12.7",
            "leaflet": "^1.9.4",
            "react-leaflet": "^4.2.1",
            "framer-motion": "^11.3.0",
            "tailwindcss": "^3.4.7",
            "axios": "^1.7.2",
            "zustand": "^4.5.4",
            "date-fns-jalali": "^3.6.0",
            "lucide-react": "^0.400.0"
        },
        "devDependencies": {
            "@types/node": "22.1.0",
            "@types/react": "18.3.3",
            "@types/leaflet": "^1.9.12",
            "typescript": "5.5.4",
            "postcss": "^8.4.39",
            "autoprefixer": "^10.4.19"
        }
    }
    write_file(ROOT / "web" / "package.json", json.dumps(package_json, indent=2, ensure_ascii=False))
    
    # next.config.js
    next_config = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  output: 'export',
  images: { unoptimized: true },
  i18n: { locales: ['fa', 'en'], defaultLocale: 'fa' },
  async rewrites() {
    return [
      { source: '/api/:path*', destination: 'http://127.0.0.1:8000/api/:path*' }
    ]
  }
}
module.exports = nextConfig
'''
    write_file(ROOT / "web" / "next.config.js", next_config)
    
    # tsconfig.json
    tsconfig = {
        "compilerOptions": {
            "target": "ES2020",
            "lib": ["dom", "dom.iterable", "esnext"],
            "allowJs": True,
            "skipLibCheck": True,
            "strict": True,
            "noEmit": True,
            "esModuleInterop": True,
            "module": "esnext",
            "moduleResolution": "bundler",
            "resolveJsonModule": True,
            "isolatedModules": True,
            "jsx": "preserve",
            "incremental": True,
            "plugins": [{"name": "next"}],
            "paths": {"@/*": ["./src/*"]}
        },
        "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
        "exclude": ["node_modules"]
    }
    write_file(ROOT / "web" / "tsconfig.json", json.dumps(tsconfig, indent=2))
    
    # tailwind.config.js
    tailwind_config = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: { extend: { fontFamily: { sans: ["Vazirmatn", "system-ui"] } } },
  plugins: [],
  darkMode: "class"
}
'''
    write_file(ROOT / "web" / "tailwind.config.js", tailwind_config)
    
    # page.tsx
    page_tsx = '''export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 text-white p-8" dir="rtl">
      <header className="text-center mb-12">
        <h1 className="text-5xl font-bold mb-4 text-cyan-400">🌍 Econojin</h1>
        <p className="text-xl text-slate-300">ابرپروژه خدمات جامع رایگان</p>
      </header>
      
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
        {[
          {title: "🌤️ هواشناسی", href: "/weather", desc: "پیش‌بینی و هشدارهای کشاورزی"},
          {title: "💰 حسابداری", href: "/accounting", desc: "مدیریت مالی شخصی و کسب‌وکار"},
          {title: "📅 تقویم", href: "/calendar", desc: "مدیریت جلسات و رویدادها"},
          {title: "🛒 فروشگاه", href: "/store", desc: "بازارچه محصولات کشاورزی"},
          {title: "📚 کتابخانه", href: "/library", desc: "منابع آموزشی و تحقیقاتی"},
          {title: "🖥️ میزکار", href: "/desktop", desc: "محیط کار وب یکپارچه"},
          {title: "🎓 آموزش", href: "/education", desc: "کلاس‌ها و وبینارهای آنلاین"},
          {title: "🗺️ GIS", href: "/gis", desc: "نقشه‌کشی و تحلیل مکانی"},
          {title: "🧠 روانشناسی", href: "/psychology", desc: "مشاوره و آزمون‌های آنلاین"},
          {title: "🌱 EcoCoin", href: "/ecomining", desc: "ماینینگ سبز و پاداش"},
          {title: "👥 جامعه", href: "/community", desc: "شبکه اجتماعی و خیریه"},
          {title: "🎮 بازی", href: "/games", desc: "بازی‌های آموزشی متاورس"},
        ].map((m, i) => (
          <a key={i} href={m.href} className="block p-6 bg-slate-800 rounded-xl hover:bg-slate-700 transition-all hover:scale-105">
            <h3 className="text-xl font-bold mb-2">{m.title}</h3>
            <p className="text-sm text-slate-400">{m.desc}</p>
          </a>
        ))}
      </div>
    </div>
  )
}
'''
    write_file(ROOT / "web" / "src" / "app" / "page.tsx", page_tsx)
    
    # layout.tsx
    layout_tsx = '''import "@/styles/globals.css"
import { Vazirmatn } from "next/font/google"

const vazir = Vazirmatn({ subsets: ["arabic", "latin"], variable: "--font-vazir" })

export const metadata = {
  title: "🌍 Econojin - ابرپروژه خدمات جامع",
  description: "پلتفرم رایگان کشاورزی، آموزش، محیط زیست و جامعه",
  manifest: "/manifest.json",
  themeColor: "#0f172a"
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" className={vazir.variable}>
      <body className="font-sans bg-slate-900 text-slate-100">{children}</body>
    </html>
  )
}
'''
    write_file(ROOT / "web" / "src" / "app" / "layout.tsx", layout_tsx)
    
    # globals.css
    globals_css = '''@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  body { @apply antialiased; }
  * { @apply box-border; }
}

@layer components {
  .btn-primary { @apply bg-cyan-600 hover:bg-cyan-500 text-white px-4 py-2 rounded-lg transition; }
  .card { @apply bg-slate-800 rounded-xl p-4 border border-slate-700; }
}
'''
    write_file(ROOT / "web" / "src" / "styles" / "globals.css", globals_css)
    
    # manifest.json
    manifest = {
        "name": "Econojin",
        "short_name": "Eco",
        "description": "ابرپروژه خدمات جامع رایگان",
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0f172a",
        "theme_color": "#0ea5e9",
        "icons": [
            {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png"}
        ]
    }
    write_file(ROOT / "web" / "public" / "manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
    
    print("🎨 فایل‌های فرانت‌اند ایجاد شد.")


def create_config_files() -> None:
    """ایجاد فایل‌های پیکربندی ریشه پروژه"""
    
    # .env.example
    env_example = '''# Econojin Environment Variables
APP_NAME=Econojin
APP_VERSION=2.0.0
DEBUG=true
HOST=127.0.0.1
PORT=8000

# Database
DATABASE_URL=sqlite+aiosqlite:///./econojin.db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,*

# EcoCoin
ECOIN_NETWORK=testnet

# AI
ENABLE_LOCAL_LLM=true
LLM_MODEL=Qwen/Qwen2.5-7B-Instruct
'''
    write_file(ROOT / ".env.example", env_example)
    
    # .gitignore
    gitignore = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
env/
*.env
*.db
*.sqlite3

# Node
node_modules/
.next/
out/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Build
dist/
build/
*.egg-info/

# Data
data/
backups/
uploads/
'''
    write_file(ROOT / ".gitignore", gitignore)
    
    # README.md - با استفاده از تابع جداگانه برای جلوگیری از خطا
    readme_content = "# 🌍 Econojin\n\nابرپروژه جامع خدمات رایگان برای کشاورزی، آموزش، محیط زیست و جامعه\n\n> 🌱 ۱۰۰٪ رایگان • 📱 آفلاین-اول • 🌐 دسترسی جهانی • 🔐 حریم خصوصی"
    write_file(ROOT / "README.md", readme_content)
    
    # docker-compose.yml
    docker_compose = '''version: "3.9"

services:
  backend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./econojin.db
      - DEBUG=true
    volumes:
      - ../../api:/app/api
      - ../../data:/app/data
    restart: unless-stopped

  frontend:
    build:
      context: ../..
      dockerfile: infrastructure/docker/Dockerfile.frontend
    ports: ["3000:3000"]
    depends_on: [backend]
    restart: unless-stopped

volumes:
  data:
'''
    write_file(ROOT / "infrastructure" / "docker" / "docker-compose.yml", docker_compose)
    
    print("⚙️ فایل‌های پیکربندی ایجاد شد.")


def install_dependencies() -> None:
    """نصب وابستگی‌های پایتون و Node.js"""
    import subprocess
    
    print("🐍 در حال نصب وابستگی‌های بک‌اند...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")], 
                      cwd=ROOT, check=True, capture_output=True)
        print("✅ نصب بک‌اند کامل شد.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ خطا در نصب بک‌اند: {e}")
    
    print("⚛️ در حال نصب وابستگی‌های فرانت‌اند...")
    npm = "npm.cmd" if os.name == "nt" else "npm"
    try:
        subprocess.run([npm, "install"], cwd=ROOT / "web", check=True, capture_output=True)
        print("✅ نصب فرانت‌اند کامل شد.")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ خطا در نصب فرانت‌اند: {e}")


def main() -> int:
    """تابع اصلی اجرا"""
    print("🚀 شروع یکپارچه‌سازی ابرپروژه اکو نوژین...")
    print(f"📁 مسیر ریشه: {ROOT}")
    
    try:
        print("\n🧹 مرحله ۱: پاکسازی ساختارهای قدیمی...")
        cleanup_old_structure()
        
        print("\n🏗️ مرحله ۲: ایجاد ساختار یکپارچه...")
        create_unified_structure()
        
        print("\n📝 مرحله ۳: ایجاد فایل‌های بک‌اند...")
        create_backend_files()
        
        print("\n🎨 مرحله ۴: ایجاد فایل‌های فرانت‌اند...")
        create_frontend_files()
        
        print("\n⚙️ مرحله ۵: ایجاد فایل‌های پیکربندی...")
        create_config_files()
        
        print("\n📦 مرحله ۶ (اختیاری): نصب وابستگی‌ها...")
        install_dependencies()
        
        print("\n" + "="*70)
        print("🎉 یکپارچه‌سازی با موفقیت تکمیل شد!")
        print("="*70)
        print("\n📋 ساختار نهایی:")
        print("   📁 D:\\econojin.com/")
        print("   ├── api/              ← بک‌اند FastAPI")
        print("   ├── web/              ← فرانت‌اند Next.js + PWA")
        print("   ├── docs/             ← مستندات")
        print("   ├── infrastructure/   ← Docker و پیکربندی")
        print("   ├── scripts/          ← اسکریپت‌های کمکی")
        print("   ├── requirements.txt  ← وابستگی‌های پایتون")
        print("   └── README.md         ← راهنمای پروژه")
        print("\n🚀 برای شروع:")
        print("   # ترمینال ۱: بک‌اند")
        print("   python -m api.main")
        print("   # ترمینال ۲: فرانت‌اند")
        print("   cd web && npm run dev")
        print("\n🔗 دسترسی:")
        print("   • فرانت‌اند:  http://localhost:3000")
        print("   • بک‌اند:     http://localhost:8000")
        print("   • مستندات:    http://localhost:8000/docs")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
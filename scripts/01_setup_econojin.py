#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 Econojin Super-Platform - Setup Script
ایجاد ساختار پروژه، نصب وابستگی‌ها و مستندات
"""
import os
import sys
import subprocess
import json
from pathlib import Path

PROJECT = Path(__file__).parent / "econojin-super-platform"

def create_dir_structure():
    """ایجاد ساختار پوشه‌های پروژه"""
    backend_modules = [
        "weather", "accounting", "calendar", "store", "library",
        "desktop", "education", "gis", "psychology", "telegram_bots",
        "ecomining", "community", "games", "infrastructure"
    ]
    frontend_pages = [
        "dashboard", "weather", "accounting", "education", 
        "gis", "ecomining", "psychology", "community"
    ]
    
    dirs = []
    for mod in backend_modules:
        dirs.append(PROJECT / "backend" / "api" / "modules" / mod)
    dirs.extend([
        PROJECT / "backend" / "core",
        PROJECT / "backend" / "tests",
        PROJECT / "backend" / "agents" / "core",
        PROJECT / "backend" / "agents" / "agents",
    ])
    for page in frontend_pages:
        dirs.append(PROJECT / "frontend" / "src" / "app" / page)
    dirs.extend([
        PROJECT / "frontend" / "public",
        PROJECT / "docs",
        PROJECT / "scripts",
        PROJECT / "infrastructure" / "docker",
    ])
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
    print(f"✅ {len(dirs)} پوشه ایجاد شد.")

def write_file(path: Path, content: str):
    """کمک‌کننده برای نوشتن فایل با encoding صحیح"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def write_files():
    """ایجاد فایل‌های پایه پروژه"""
    
    # فایل‌های بک‌اند
    write_file(PROJECT / "backend" / "api" / "main.py", '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Econojin Backend", version="2.0.0", docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def root():
    return {"message": "🛰️ Econojin Backend Ready", "version": "2.0.0"}

@app.get("/api/v1/health")
def health():
    return {"status": "healthy", "service": "econojin-backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True)
''')
    
    write_file(PROJECT / "backend" / "api" / "core" / "config.py", '''from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Econojin Super-Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"

settings = Settings()
''')
    
    write_file(PROJECT / "backend" / "requirements.txt", '''fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
httpx>=0.26.0
structlog>=24.1.0
''')
    
    # فایل‌های فرانت‌اند
    package_json = {
        "name": "econojin-frontend",
        "version": "2.0.0",
        "private": True,
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "recharts": "^2.12.0",
            "leaflet": "^1.9.4",
            "react-leaflet": "^4.2.1"
        },
        "devDependencies": {
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
            "@vitejs/plugin-react": "^4.2.0",
            "typescript": "^5.3.0",
            "vite": "^5.0.0"
        }
    }
    write_file(PROJECT / "frontend" / "package.json", json.dumps(package_json, indent=2, ensure_ascii=False))
    
    write_file(PROJECT / "frontend" / "vite.config.js", '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: { port: 3000, proxy: { '/api': { target: 'http://127.0.0.1:8000' } } }
})
''')
    
    write_file(PROJECT / "frontend" / "src" / "app" / "page.tsx", '''export default function Home() {
  return (
    <div className="min-h-screen bg-slate-900 text-white p-8" dir="rtl">
      <h1 className="text-4xl font-bold text-cyan-400">🌍 Econojin</h1>
      <p className="mt-4 text-slate-300">ابرپروژه خدمات جامع رایگان</p>
    </div>
  )
}
''')
    
    # مستندات
    write_file(PROJECT / "docs" / "README.md", '''# 🌍 Econojin Super-Platform

ابرپروژه جامع خدمات رایگان برای کشاورزی، آموزش، محیط زیست و جامعه.

## 🚀 شروع سریع

### پیش‌نیازها
- Python 3.10+
- Node.js 18+

### نصب
```bash
# بک‌اند
cd backend
python -m venv .venv
.venv\\Scripts\\activate  # ویندوز
pip install -r requirements.txt

# فرانت‌اند
cd ../frontend
npm install
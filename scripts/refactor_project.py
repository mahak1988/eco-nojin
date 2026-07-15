#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - اسکریپت جامع بازسازی معماری (نسخه بازنویسی‌شده)
نسخه: 2.1.0

این اسکریپت به‌طور خودکار:
- پروژه را اسکن کرده و معماری فعلی را شناسایی می‌کند
- لایه‌های گم‌شده DDD را ایجاد می‌نماید
- کتابخانه‌های مورد نیاز را نصب می‌کند
- کلاینت‌های سرویس‌های رایگان را تولید می‌کند
- فایل‌های پیکربندی را ایجاد می‌کند
- گزارش کامل از اقدامات انجام‌شده ارائه می‌دهد
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import ast

# ============================================================
# تنظیمات پروژه
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPS_DIR = PROJECT_ROOT / "apps"
WEB_DIR = APPS_DIR / "web"
API_DIR = APPS_DIR / "api"
APP_DIR = PROJECT_ROOT / "app"

# لایه‌های DDD
DDD_LAYERS = {
    "domain": APP_DIR / "domain",
    "application": APP_DIR / "application",
    "infrastructure": APP_DIR / "infrastructure",
    "presentation": APP_DIR / "presentation",
    "core": APP_DIR / "core",
}

# حوزه‌های دامنه
DOMAINS = [
    "hydrology", "soil", "carbon", "drought", "ecosystem",
    "energy", "biodiversity", "user", "eco_coin", "result"
]

# ============================================================
# ابزارهای کمکی
# ============================================================

def log(message: str, level: str = "INFO"):
    """چاپ پیام با رنگ‌بندی"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "HEADER": "\033[95m",
        "END": "\033[0m",
    }
    color = colors.get(level, "")
    end = colors.get("END", "")
    print(f"{color}[{level}]{end} {message}")

def create_file(path: Path, content: str, overwrite: bool = False):
    """ایجاد فایل با محتوای مشخص"""
    if path.exists() and not overwrite:
        log(f"فایل {path.name} از قبل وجود دارد (رد شد)", "WARNING")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"ایجاد: {path.relative_to(PROJECT_ROOT)}", "SUCCESS")
    return True

# ============================================================
# کلاس اصلی بازسازی
# ============================================================

class EcoNojinRefactor:
    def __init__(self):
        self.created_files = []
        self.updated_files = []
        self.installed_packages = []
        self.discovery_data = {}
        self.stats = {
            "total_files": 0,
            "python_files": 0,
            "js_files": 0,
            "json_files": 0,
            "missing_layers": [],
            "existing_layers": [],
        }

    # ------------------------------------------------------------
    # مرحله ۱: شناسایی پروژه
    # ------------------------------------------------------------
    def discover_project(self):
        log("🔍 مرحله ۱: شناسایی پروژه", "HEADER")
        log("=" * 60, "HEADER")

        # اسکن پوشه‌ها
        for folder in [APP_DIR, API_DIR, WEB_DIR]:
            if folder.exists():
                self._scan_directory(folder)

        # بررسی لایه‌های DDD
        for name, path in DDD_LAYERS.items():
            if path.exists() and any(path.iterdir()):
                self.stats["existing_layers"].append(name)
                log(f"✅ لایه {name}: موجود است", "SUCCESS")
            else:
                self.stats["missing_layers"].append(name)
                log(f"❌ لایه {name}: وجود ندارد", "ERROR")

        log(f"\n📊 آمار شناسایی:")
        log(f"   فایل‌های پایتون: {self.stats['python_files']}")
        log(f"   فایل‌های جاوااسکریپت: {self.stats['js_files']}")
        log(f"   فایل‌های JSON: {self.stats['json_files']}")
        log(f"   مجموع فایل‌ها: {self.stats['total_files']}")

    def _scan_directory(self, path: Path):
        """اسکن یک پوشه و جمع‌آوری اطلاعات"""
        for file in path.rglob("*"):
            if file.is_file():
                # نادیده گرفتن پوشه‌های خاص
                if any(part in file.parts for part in ["__pycache__", "node_modules", ".git", ".venv", ".pytest_cache"]):
                    continue
                self.stats["total_files"] += 1
                ext = file.suffix.lower()
                if ext == ".py":
                    self.stats["python_files"] += 1
                elif ext in [".ts", ".tsx", ".js", ".jsx"]:
                    self.stats["js_files"] += 1
                elif ext == ".json":
                    self.stats["json_files"] += 1

    # ------------------------------------------------------------
    # مرحله ۲: ایجاد معماری DDD
    # ------------------------------------------------------------
    def create_ddd_layers(self):
        log("\n🏗️ مرحله ۲: ایجاد معماری DDD", "HEADER")
        log("=" * 60, "HEADER")

        # ایجاد لایه‌های اصلی
        for layer_name, layer_path in DDD_LAYERS.items():
            if not layer_path.exists():
                layer_path.mkdir(parents=True, exist_ok=True)
                (layer_path / "__init__.py").touch()
                self.created_files.append(str(layer_path / "__init__.py"))
                log(f"✅ ایجاد لایه: {layer_name}")

        # ایجاد حوزه‌های دامنه
        domain_root = DDD_LAYERS["domain"]
        for domain in DOMAINS:
            domain_dir = domain_root / domain
            if not domain_dir.exists():
                domain_dir.mkdir(parents=True, exist_ok=True)
                # فایل‌های اصلی هر حوزه
                files = {
                    "__init__.py": "",
                    "entities.py": "# موجودیت‌های حوزه " + domain + "\n\n",
                    "value_objects.py": "# اشیاء مقداری حوزه " + domain + "\n\n",
                    "repositories.py": "# اینترفیس‌های مخزن حوزه " + domain + "\n\n",
                    "events.py": "# رویدادهای حوزه " + domain + "\n\n",
                    "services.py": "# سرویس‌های حوزه " + domain + "\n\n",
                }
                for fname, content in files.items():
                    fpath = domain_dir / fname
                    fpath.write_text(content, encoding="utf-8")
                    self.created_files.append(str(fpath))
                log(f"   ✅ حوزه: {domain}")

        # ایجاد لایه application (use cases)
        app_root = DDD_LAYERS["application"]
        for domain in DOMAINS:
            app_domain = app_root / domain
            if not app_domain.exists():
                app_domain.mkdir(parents=True, exist_ok=True)
                files = {
                    "__init__.py": "",
                    "dto.py": "# DTO برای حوزه " + domain + "\n\n",
                    f"create_{domain}.py": f"# Use Case: ایجاد {domain}\n\n",
                    f"get_{domain}.py": f"# Use Case: دریافت {domain}\n\n",
                    f"update_{domain}.py": f"# Use Case: به‌روزرسانی {domain}\n\n",
                    f"delete_{domain}.py": f"# Use Case: حذف {domain}\n\n",
                }
                for fname, content in files.items():
                    fpath = app_domain / fname
                    fpath.write_text(content, encoding="utf-8")
                    self.created_files.append(str(fpath))
                log(f"   ✅ application: {domain}")

        # ایجاد لایه infrastructure (مدل‌ها و مخزن‌ها)
        infra_root = DDD_LAYERS["infrastructure"]
        # persistence/models
        models_path = infra_root / "persistence" / "models"
        models_path.mkdir(parents=True, exist_ok=True)
        (models_path / "__init__.py").touch()
        self.created_files.append(str(models_path / "__init__.py"))

        # persistence/repositories
        repos_path = infra_root / "persistence" / "repositories"
        repos_path.mkdir(parents=True, exist_ok=True)
        (repos_path / "__init__.py").touch()
        self.created_files.append(str(repos_path / "__init__.py"))

        # base.py برای مدل‌ها
        base_content = """# کلاس پایه برای مدل‌های SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
"""
        create_file(infra_root / "persistence" / "base.py", base_content)

        # ایجاد کلاینت‌های سرویس‌های خارجی
        ext_services = infra_root / "external_services"
        services = ["ai_models", "satellite", "finance", "weather", "blockchain"]
        for svc in services:
            svc_dir = ext_services / svc
            svc_dir.mkdir(parents=True, exist_ok=True)
            (svc_dir / "__init__.py").touch()
            self.created_files.append(str(svc_dir / "__init__.py"))

        # ایجاد لایه presentation
        pres_root = DDD_LAYERS["presentation"]
        endpoints_path = pres_root / "api" / "v1" / "endpoints"
        schemas_path = pres_root / "api" / "v1" / "schemas"
        endpoints_path.mkdir(parents=True, exist_ok=True)
        schemas_path.mkdir(parents=True, exist_ok=True)

        for domain in DOMAINS:
            # endpoint
            ep_file = endpoints_path / f"{domain}.py"
            ep_content = f"""# Endpointهای حوزه {domain}
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.presentation.api.v1.schemas.{domain} import *

router = APIRouter(prefix="/{domain}", tags=["{domain.capitalize()}"])

@router.get("/", response_model=List[{domain.capitalize()}Response])
async def get_all():
    return []

@router.get("/{{entity_id}}", response_model={domain.capitalize()}Response)
async def get_one(entity_id: int):
    return {domain.capitalize()}Response(id=entity_id)

@router.post("/", response_model={domain.capitalize()}Response)
async def create(data: {domain.capitalize()}Create):
    return {domain.capitalize()}Response(id=1)

@router.put("/{{entity_id}}", response_model={domain.capitalize()}Response)
async def update(entity_id: int, data: {domain.capitalize()}Update):
    return {domain.capitalize()}Response(id=entity_id)

@router.delete("/{{entity_id}}")
async def delete(entity_id: int):
    return {{"status": "deleted"}}
"""
            create_file(ep_file, ep_content)

            # schema
            sch_file = schemas_path / f"{domain}.py"
            sch_content = f"""# Pydantic Schemas برای {domain}
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class {domain.capitalize()}Base(BaseModel):
    pass

class {domain.capitalize()}Create({domain.capitalize()}Base):
    pass

class {domain.capitalize()}Update(BaseModel):
    pass

class {domain.capitalize()}Response({domain.capitalize()}Base):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
"""
            create_file(sch_file, sch_content)

        # router اصلی
        router_content = '''# روتر اصلی v1
from fastapi import APIRouter
from app.presentation.api.v1.endpoints import (
    auth, users, hydrology, soil, carbon, drought,
    ecosystem, energy, biodiversity, eco_coin, results
)

api_v1_router = APIRouter(prefix="/api/v1")
for r in [auth, users, hydrology, soil, carbon, drought,
          ecosystem, energy, biodiversity, eco_coin, results]:
    api_v1_router.include_router(r.router)
'''
        create_file(pres_root / "api" / "v1" / "router.py", router_content)

        # ایجاد core (config, database, security)
        core_root = DDD_LAYERS["core"]
        core_files = {
            "config.py": '''# تنظیمات برنامه
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "sqlite:///./econojin.db"
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    allowed_origins: list = ["http://localhost:5173"]
    openrouter_api_key: Optional[str] = None
    google_earth_engine_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    tushare_token: Optional[str] = None
    ethereum_rpc_url: Optional[str] = None
    owner_private_key: Optional[str] = None
    eco_coin_contract_address: Optional[str] = None
    env_state: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
''',
            "database.py": '''# اتصال به دیتابیس
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator
from app.core.config import settings

async_engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.debug, future=True
)
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
sync_engine = create_engine(settings.database_url, echo=settings.debug)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

def get_sync_engine():
    return sync_engine
''',
            "security.py": '''# امنیت و JWT
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
'''
        }
        for fname, content in core_files.items():
            create_file(core_root / fname, content)

        log(f"\n✅ مجموع فایل‌های ایجادشده: {len(self.created_files)}")

    # ------------------------------------------------------------
    # مرحله ۳: نصب کتابخانه‌ها
    # ------------------------------------------------------------
    def install_packages(self):
        log("\n📦 مرحله ۳: نصب کتابخانه‌های مورد نیاز", "HEADER")
        log("=" * 60, "HEADER")

        required = [
            "fastapi", "uvicorn[standard]", "sqlalchemy[asyncio]",
            "psycopg[binary]", "alembic", "pydantic", "pydantic-settings",
            "python-jose[cryptography]", "passlib[bcrypt]", "python-multipart",
            "httpx", "supabase", "python-dotenv", "email-validator",
            "langchain", "langchain-community", "openai", "tiktoken",
            "web3", "pytest", "pytest-asyncio", "anyio", "setuptools",
            "bandit", "flake8", "pylint", "mypy", "radon", "pip-audit", "safety",
            "yfinance"
        ]

        installed = []
        failed = []
        for pkg in required:
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", pkg],
                    capture_output=True, check=True, text=True
                )
                installed.append(pkg)
                log(f"   ✅ {pkg}", "SUCCESS")
            except subprocess.CalledProcessError:
                failed.append(pkg)
                log(f"   ❌ {pkg} (خطا)", "ERROR")

        self.installed_packages = installed

        # به‌روزرسانی requirements.txt
        req_file = PROJECT_ROOT / "requirements.txt"
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True, text=True, check=True
        )
        lines = [l for l in result.stdout.split("\n") if l.strip() and not l.startswith("pkg-resources")]
        req_file.write_text("\n".join(lines), encoding="utf-8")
        self.updated_files.append(str(req_file))

        log(f"\n✅ نصب شد: {len(installed)} کتابخانه", "SUCCESS")
        if failed:
            log(f"⚠️ خطا در نصب {len(failed)} کتابخانه", "WARNING")

    # ------------------------------------------------------------
    # مرحله ۴: ایجاد کلاینت‌های سرویس‌های رایگان
    # ------------------------------------------------------------
    def create_free_service_clients(self):
        log("\n🆓 مرحله ۴: ایجاد کلاینت‌های سرویس‌های رایگان", "HEADER")
        log("=" * 60, "HEADER")

        infra_root = DDD_LAYERS["infrastructure"]
        ext_path = infra_root / "external_services"

        # کلاینت OpenRouter
        openrouter_content = '''# کلاینت OpenRouter
import httpx
import json
from typing import Dict, Any, AsyncGenerator
from app.core.config import settings

class OpenRouterClient:
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = settings.openrouter_api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

    async def chat_completion(self, messages: list, model: str = "google/gemini-2.5-flash", temp: float = 0.7, max_tokens: int = 1000) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json={
                "model": model, "messages": messages, "temperature": temp, "max_tokens": max_tokens
            }, headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    async def stream_chat(self, messages: list, model: str = "google/gemini-2.5-flash", temp: float = 0.7):
        async with httpx.AsyncClient(timeout=60) as client:
            async with client.stream("POST", f"{self.base_url}/chat/completions", json={
                "model": model, "messages": messages, "temperature": temp, "stream": True
            }, headers=self.headers) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            yield chunk["choices"][0]["delta"].get("content", "")
                        except:
                            continue
'''
        create_file(ext_path / "ai_models" / "openrouter.py", openrouter_content)

        # کلاینت Google Earth Engine
        gee_content = '''# کلاینت Google Earth Engine
import json
from typing import Dict, Any

class GeeClient:
    def __init__(self):
        self.credentials = None
        # در عمل از earthengine-api استفاده کنید

    async def get_ndvi(self, lat: float, lon: float, start: str, end: str) -> Dict[str, Any]:
        return {"ndvi": 0.65, "lat": lat, "lon": lon, "status": "simulated"}

    async def get_land_cover(self, lat: float, lon: float) -> Dict[str, Any]:
        return {"type": "agriculture", "status": "simulated"}
'''
        create_file(ext_path / "satellite" / "google_earth_engine.py", gee_content)

        # کلاینت Supabase
        supabase_content = '''# کلاینت Supabase
from supabase import create_client, Client
from app.core.config import settings

def get_supabase() -> Client:
    return create_client(settings.supabase_url, settings.supabase_anon_key) if settings.supabase_url else None

class SupabaseService:
    def __init__(self):
        self.client = get_supabase()

    async def get_user(self, user_id: int):
        if not self.client: return None
        res = self.client.table("users").select("*").eq("id", user_id).execute()
        return res.data[0] if res.data else None

    async def create_user(self, data: dict):
        if not self.client: return None
        res = self.client.table("users").insert(data).execute()
        return res.data[0] if res.data else None

    async def save_result(self, data: dict):
        if not self.client: return None
        res = self.client.table("simulation_results").insert(data).execute()
        return res.data[0] if res.data else None
'''
        supabase_dir = infra_root / "supabase"
        supabase_dir.mkdir(parents=True, exist_ok=True)
        create_file(supabase_dir / "client.py", supabase_content)

        # کلاینت Yahoo Finance
        yfinance_content = '''# کلاینت Yahoo Finance
import yfinance as yf
from typing import Dict, Any, List
from datetime import datetime

class YahooFinanceClient:
    async def get_price(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if len(data) > 0:
                return {"symbol": symbol, "price": data["Close"].iloc[-1], "currency": "USD", "timestamp": datetime.now().isoformat()}
        except:
            pass
        return {"symbol": symbol, "price": 0}

    async def get_history(self, symbol: str, period: str = "1mo", interval: str = "1d") -> List[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            if len(data) > 0:
                return [{"date": d.isoformat(), "open": row["Open"], "high": row["High"], "low": row["Low"], "close": row["Close"], "volume": row["Volume"]} for d, row in data.iterrows()]
        except:
            pass
        return []
'''
        create_file(ext_path / "finance" / "yahoo_finance.py", yfinance_content)

        log("✅ تمام کلاینت‌ها ایجاد شدند", "SUCCESS")

    # ------------------------------------------------------------
    # مرحله ۵: ایجاد فایل‌های پیکربندی
    # ------------------------------------------------------------
    def create_config_files(self):
        log("\n⚙️ مرحله ۵: ایجاد فایل‌های پیکربندی", "HEADER")
        log("=" * 60, "HEADER")

        # .env.example
        env_content = '''# ============================
# بک‌اند
# ============================
ENV_STATE=development
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///./econojin.db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173
OPENROUTER_API_KEY=sk-...
GOOGLE_EARTH_ENGINE_KEY={"type":"service_account",...}
ALPHA_VANTAGE_API_KEY=...
TUSHARE_TOKEN=...
OPENWEATHER_API_KEY=...
ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/...
OWNER_PRIVATE_KEY=0x...
ECOCOIN_CONTRACT_ADDRESS=0x...

# ============================
# فرانت‌اند
# ============================
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=eyJ...
'''
        create_file(PROJECT_ROOT / ".env.example", env_content)

        # .gitignore
        gitignore_content = '''# Python
__pycache__/
*.pyc
*.pyo
*.so
.Python
env/
venv/
.venv/
.env
*.db
*.sqlite3
*.log

# Node
node_modules/
dist/
build/
.DS_Store

# IDE
.vscode/
.idea/
*.swp

# Testing
.pytest_cache/
.coverage
htmlcov/

# Keys & secrets
*.pem
*.key
*.crt
'''
        create_file(PROJECT_ROOT / ".gitignore", gitignore_content)

        # اسکریپت run_dev.py
        run_dev_content = '''#!/usr/bin/env python3
import subprocess, sys, os, signal, threading
from pathlib import Path

ROOT = Path(__file__).parent.parent
API_DIR = ROOT / "apps" / "api"
WEB_DIR = ROOT / "apps" / "web"

def run_backend():
    os.chdir(API_DIR)
    return subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

def run_frontend():
    os.chdir(WEB_DIR)
    return subprocess.Popen(["pnpm", "run", "dev"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

def main():
    procs = [("Backend", run_backend()), ("Frontend", run_frontend())]
    for name, p in procs:
        def log_output(proc=p, n=name):
            for line in iter(proc.stdout.readline, ''):
                if line: print(f"[{n}] {line.rstrip()}")
        threading.Thread(target=log_output, daemon=True).start()
    print("✅ سرویس‌ها راه‌اندازی شدند (Ctrl+C برای توقف)")
    try:
        for _, p in procs:
            p.wait()
    except KeyboardInterrupt:
        for _, p in procs:
            p.terminate()
        sys.exit(0)

if __name__ == "__main__":
    main()
'''
        scripts_dir = PROJECT_ROOT / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        create_file(scripts_dir / "run_dev.py", run_dev_content)

        log("✅ تمام فایل‌های پیکربندی ایجاد شدند", "SUCCESS")

    # ------------------------------------------------------------
    # مرحله ۶: گزارش نهایی
    # ------------------------------------------------------------
    def generate_report(self):
        log("\n📊 مرحله ۶: تولید گزارش نهایی", "HEADER")
        log("=" * 60, "HEADER")

        report = {
            "timestamp": datetime.now().isoformat(),
            "project": "Eco Nojin",
            "actions": {
                "created_files": self.created_files,
                "updated_files": self.updated_files,
                "installed_packages": self.installed_packages,
            },
            "summary": {
                "total_created": len(self.created_files),
                "total_updated": len(self.updated_files),
                "total_installed": len(self.installed_packages),
                "existing_layers": self.stats["existing_layers"],
                "missing_layers": self.stats["missing_layers"],
            }
        }

        report_file = PROJECT_ROOT / "refactor_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        log(f"✅ گزارش در {report_file} ذخیره شد", "SUCCESS")

        # نمایش خلاصه
        log("\n📈 خلاصه اقدامات:", "HEADER")
        log(f"   فایل‌های ایجادشده: {len(self.created_files)}")
        log(f"   فایل‌های به‌روزرسانی‌شده: {len(self.updated_files)}")
        log(f"   کتابخانه‌های نصب‌شده: {len(self.installed_packages)}")
        log(f"   لایه‌های موجود: {', '.join(self.stats['existing_layers']) if self.stats['existing_layers'] else 'هیچ‌کدام'}")
        log(f"   لایه‌های گم‌شده که ایجاد شدند: {', '.join(self.stats['missing_layers']) if self.stats['missing_layers'] else 'همه وجود داشتند'}")

    # ------------------------------------------------------------
    # اجرای کل
    # ------------------------------------------------------------
    def run(self):
        log("🌱 Eco Nojin - Refactoring Suite v2.1", "HEADER")
        log("=" * 60, "HEADER")

        self.discover_project()
        self.create_ddd_layers()
        self.install_packages()
        self.create_free_service_clients()
        self.create_config_files()
        self.generate_report()

        log("\n✅ بازسازی کامل شد!", "SUCCESS")
        log("📌 مراحل بعدی:", "INFO")
        log("   1. کپی .env.example به .env و تنظیم کلیدها")
        log("   2. اجرای `alembic upgrade head`")
        log("   3. اجرای `python scripts/run_dev.py`")
        log("   4. مشاهده مستندات API در http://localhost:8000/docs")

# ============================================================
# نقطه ورود
# ============================================================

if __name__ == "__main__":
    try:
        refactor = EcoNojinRefactor()
        refactor.run()
    except KeyboardInterrupt:
        log("\n⏹️ اجرا متوقف شد.", "WARNING")
        sys.exit(0)
    except Exception as e:
        log(f"❌ خطا: {e}", "ERROR")
        import traceback
        traceback.print_exc()
        sys.exit(1)
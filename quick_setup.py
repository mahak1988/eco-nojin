#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Econojin Quick Setup - همه‌کاره
این اسکریپت: ۱) پکیج‌ها را نصب می‌کند ۲) فایل‌ها را می‌سازد ۳) پروژه را تست می‌کند
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
print(f"🚀 Econojin Quick Setup | Root: {ROOT}")

# ========== ۱. بررسی و تعمیر محیط پایتون ==========
print("\n[1/4] Checking Python environment...")
python_exe = sys.executable
print(f"   Python: {python_exe}")

# تست pip
try:
    subprocess.run([python_exe, "-m", "pip", "--version"], check=True, capture_output=True)
    print("   ✅ pip is available")
except:
    print("   ⚠️ pip not found, trying to bootstrap...")
    # تلاش برای نصب pip اگر نیست
    try:
        subprocess.run(
            [python_exe, "-m", "ensurepip", "--upgrade"], check=True, capture_output=True
        )
        print("   ✅ pip bootstrapped")
    except:
        print("   ❌ Could not bootstrap pip. Using system packages only.")

# ========== ۲. نصب پکیج‌های ضروری ==========
print("\n[2/4] Installing required packages...")
packages = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic-settings",
    "python-dotenv",
    "httpx",
    "sqlalchemy",
    "aiosqlite",
    "structlog",
]
for pkg in packages:
    try:
        subprocess.run(
            [
                python_exe,
                "-m",
                "pip",
                "install",
                pkg,
                "--quiet",
                "--trusted-host",
                "pypi.org",
                "--trusted-host",
                "files.pythonhosted.org",
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )
        print(f"   ✅ {pkg}")
    except Exception as e:
        print(f"   ⚠️ {pkg}: {str(e)[:50]}")

# ========== ۳. ایجاد ساختار فایل‌ها ==========
print("\n[3/4] Creating project files...")


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


# api/__init__.py
write_file(ROOT / "api" / "__init__.py", "# Econojin API\n")

# api/core/__init__.py
write_file(ROOT / "api" / "core" / "__init__.py", "# Core module\n")

# api/core/config.py
write_file(
    ROOT / "api" / "core" / "config.py",
    """from pydantic_settings import BaseSettings
class Settings(BaseSettings):
    APP_NAME: str = "Econojin"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DATABASE_URL: str = "sqlite+aiosqlite:///./econojin.db"
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001", "*"]
    class Config:
        env_file = ".env"
settings = Settings()
""",
)

# api/core/database.py
write_file(
    ROOT / "api" / "core" / "database.py",
    """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
Base = declarative_base()
engine = None
AsyncSessionLocal = None
async def init_db():
    global engine, AsyncSessionLocal
    from api.core.config import settings
    connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
    engine = create_async_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)
    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(f"✅ Database: {settings.DATABASE_URL}")
async def get_db():
    async with AsyncSessionLocal() as session:
        try: yield session
        finally: await session.close()
""",
)

# api/modules/weather/router.py
write_file(ROOT / "api" / "modules" / "weather" / "__init__.py", "# Weather module\n")
write_file(
    ROOT / "api" / "modules" / "weather" / "router.py",
    """from fastapi import APIRouter, Query
router = APIRouter()
@router.get("/forecast")
async def get_forecast(location: str = Query("تهران"), days: int = Query(7, ge=1, le=14)):
    return {"location": location, "days": days, "forecast": [{"day": f"روز {i+1}", "temp_c": 20+i} for i in range(days)]}
@router.get("/alerts")
async def get_alerts(region: str = Query("خراسان")):
    return {"region": region, "alerts": [{"type": "frost", "message": "احتمال یخبندان"}]}
""",
)

# api/modules/accounting/router.py
write_file(ROOT / "api" / "modules" / "accounting" / "__init__.py", "# Accounting module\n")
write_file(
    ROOT / "api" / "modules" / "accounting" / "router.py",
    """from fastapi import APIRouter
router = APIRouter()
@router.get("/summary")
async def get_summary():
    return {"total_income": 112400000, "total_expense": 48700000, "net_profit": 63700000, "currency": "IRR"}
""",
)

# api/modules/gis/router.py
write_file(ROOT / "api" / "modules" / "gis" / "__init__.py", "# GIS module\n")
write_file(
    ROOT / "api" / "modules" / "gis" / "router.py",
    """from fastapi import APIRouter, Body
router = APIRouter()
@router.post("/calculate/area")
async def calculate_area(coordinates: list[list[float]] = Body(...)):
    if len(coordinates) < 3: return {"error": "حداقل ۳ نقطه نیاز است"}
    area = sum(coordinates[i][0]*coordinates[(i+1)%len(coordinates)][1] - coordinates[(i+1)%len(coordinates)][0]*coordinates[i][1] for i in range(len(coordinates)))
    return {"area_km2": abs(area)/2/1_000_000}
""",
)

# api/agents/orchestrator.py
write_file(ROOT / "api" / "agents" / "__init__.py", "# Agents module\n")
write_file(
    ROOT / "api" / "agents" / "orchestrator.py",
    """class EconojinOrchestrator:
    async def process_request(self, request: str, context: dict):
        return {"status": "processed", "response": "OK", "context": context}
""",
)

# api/main.py - فایل اصلی
write_file(
    ROOT / "api" / "main.py",
    '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""🛰️ Econojin Backend"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))

from api.core.config import settings
from api.core.database import init_db
from api.agents.orchestrator import EconojinOrchestrator

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"✅ {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    await init_db()
    app.state.orchestrator = EconojinOrchestrator()
    print(f"✅ Ready on http://{settings.HOST}:{settings.PORT}")
    yield
    print(f"👋 Shutting down")

app = FastAPI(title=settings.APP_NAME, description="🌍 Econojin", version=settings.APP_VERSION, lifespan=lifespan, docs_url="/docs")
app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.get("/")
async def root(): return {"message": "🛰️ Welcome to Econojin", "version": settings.APP_VERSION, "docs": "/docs", "status": "running"}

@app.get("/api/v1/health")
async def health(): return {"status": "healthy", "service": settings.APP_NAME, "version": settings.APP_VERSION, "modules": 15}

@app.get("/api/v1/modules")
async def list_modules(): return {"modules": [{"id": m, "name": m, "status": "active"} for m in ["weather", "accounting", "gis"]]}

from api.modules.weather.router import router as weather_router
app.include_router(weather_router, prefix="/api/v1/weather", tags=["Weather"])
from api.modules.accounting.router import router as accounting_router
app.include_router(accounting_router, prefix="/api/v1/accounting", tags=["Accounting"])
from api.modules.gis.router import router as gis_router
app.include_router(gis_router, prefix="/api/v1/gis", tags=["GIS"])

@app.exception_handler(Exception)
async def global_error(request, exc: Exception):
    return JSONResponse(status_code=500, content={"error": "Server Error", "detail": str(exc) if settings.DEBUG else "Try later"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
''',
)

# ========== ۴. تست و گزارش نهایی ==========
print("\n[4/4] Testing setup...")
tests = [
    ("Config import", "from api.core.config import settings"),
    ("Database import", "from api.core.database import init_db"),
    ("Orchestrator import", "from api.agents.orchestrator import EconojinOrchestrator"),
    ("Main import", "from api.main import app"),
]
passed = 0
for name, code in tests:
    try:
        exec(code, {"__name__": "__main__"})
        print(f"   ✅ {name}")
        passed += 1
    except Exception as e:
        print(f"   ❌ {name}: {str(e)[:40]}")

print(f"\n{'='*50}")
print(f"✅ Setup Complete: {passed}/{len(tests)} tests passed")
if passed == len(tests):
    print(f"\n🚀 To run backend:")
    print(f"   python api\\main.py")
    print(f"\n🔗 Then open:")
    print(f"   http://localhost:8000")
    print(f"   http://localhost:8000/docs")
else:
    print(f"\n⚠️  Some tests failed. Check errors above.")
print(f"{'='*50}")

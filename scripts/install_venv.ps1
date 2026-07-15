# اسکریپت نصب Packages در Virtual Environment

Write-Host "🚀 شروع نصب Packages در venv..." -ForegroundColor Cyan

# فعال‌سازی venv (اگر فعال نیست)
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "❌ venv وجود ندارد!" -ForegroundColor Red
    exit 1
}

# فعال‌سازی
.\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`n📦 Upgrade pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# نصب dependencies
Write-Host "`n📦 نصب Core Dependencies..." -ForegroundColor Yellow
python -m pip install `
    fastapi `
    uvicorn `
    sqlalchemy `
    pydantic `
    python-jose `
    passlib `
    bcrypt `
    python-multipart

Write-Host "`n📦 نصب LangChain..." -ForegroundColor Yellow
python -m pip install `
    langchain `
    langchain-core `
    langchain-openai `
    langchain-groq `
    langchain-ollama `
    langchain-google-genai `
    langchain-community `
    langgraph

Write-Host "`n📦 نصب Utilities..." -ForegroundColor Yellow
python -m pip install `
    httpx `
    python-dotenv `
    pydantic-settings

Write-Host "`n📦 نصب RAG..." -ForegroundColor Yellow
python -m pip install `
    sentence-transformers `
    qdrant-client `
    faiss-cpu

Write-Host "`n📦 نصب Compute..." -ForegroundColor Yellow
python -m pip install `
    numba `
    scipy `
    numpy `
    matplotlib

Write-Host "`n📦 نصب Web Tools..." -ForegroundColor Yellow
python -m pip install `
    duckduckgo-search `
    PyPDF2

# تست نصب
Write-Host "`n🧪 تست نصب..." -ForegroundColor Green

$tests = @(
    "import sqlalchemy; print('✅ SQLAlchemy:', sqlalchemy.__version__)",
    "import fastapi; print('✅ FastAPI:', fastapi.__version__)",
    "import langchain; print('✅ LangChain:', langchain.__version__)",
    "import numpy; print('✅ NumPy:', numpy.__version__)",
    "import torch; print('✅ PyTorch:', torch.__version__)"
)

foreach ($test in $tests) {
    try {
        python -c $test
    } catch {
        Write-Host "❌ خطا: $test" -ForegroundColor Red
    }
}

Write-Host "`n✅ نصب کامل شد!" -ForegroundColor Green
Write-Host "`n📌 گام بعدی:" -ForegroundColor Cyan
Write-Host "python -c 'from apps.main import app; print(`"✅ Import موفق`")'"
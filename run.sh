#!/bin/bash
set -e

echo "🚀 Econojin - شروع بدون Docker"
echo "================================"

# بررسی نصب uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv نصب نیست. در حال نصب..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# نصب Python مناسب پروژه (بر اساس pyproject.toml)
echo ""
echo "📦 نصب Python 3.12..."
uv python install 3.12

# نصب dependencies
echo ""
echo "📦 نصب dependencies..."
uv sync --extra dev

# اجرای سرور
echo ""
echo "🚀 اجرای سرور روی http://localhost:8000"
echo "📚 مستندات: http://localhost:8000/docs"
echo "🔴 Swagger UI: http://localhost:8000/redoc"
echo ""
echo "برای توقف: Ctrl+C"
echo ""

uv run uvicorn apps.main:app --host 0.0.0.0 --port 8000 --reload

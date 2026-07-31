#!/bin/bash
set -e
echo "🚀 Starting Eco-Nojin Automated Setup..."

# 1. Python Backend Setup
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
if [ -f "requirements.txt" ]; then pip install -r requirements.txt; fi
if [ -f "requirements-scientific.txt" ]; then pip install -r requirements-scientific.txt; fi

# 2. Node.js Frontend Setup
echo "📦 Setting up Node.js and pnpm..."
corepack enable pnpm
pnpm install

# 3. Git Hooks (Optional but recommended)
if command -v pre-commit &> /dev/null; then
    echo "🔒 Installing pre-commit hooks..."
    pre-commit install
fi

echo "✅ Setup Complete! You can now start developing."
echo "   -> Backend: source .venv/bin/activate && uvicorn apps.main:app --reload --port 8000"
echo "   -> Frontend: pnpm --filter web dev"

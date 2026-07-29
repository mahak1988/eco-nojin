#!/usr/bin/env bash
set -euo pipefail
if command -v docker >/dev/null 2>&1; then
  docker compose up -d postgres redis
  sleep 8
fi
export FORCE_POSTGRES=1
export DATABASE_URL="postgresql+asyncpg://econojin:econojin@127.0.0.1:5432/econojin"
export ENVIRONMENT=local
pip install 'asyncpg>=0.30.0' 'psycopg[binary]>=3.1.0' -q
alembic upgrade head
echo "Run: FORCE_POSTGRES=1 DATABASE_URL=postgresql+asyncpg://econojin:econojin@127.0.0.1:5432/econojin uvicorn apps.main:app --reload --port 8000"

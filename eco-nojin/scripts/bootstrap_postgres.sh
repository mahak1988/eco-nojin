#!/usr/bin/env bash
# Bring up Docker stack and run Alembic against Postgres
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> docker compose up"
docker compose up --build -d postgres redis
echo "Waiting for postgres..."
sleep 5
docker compose up -d api worker beat

echo "==> install sync driver for alembic (host)"
pip install -q "psycopg[binary]>=3.1" asyncpg alembic sqlalchemy 2>/dev/null || true

export ENVIRONMENT=staging
export ALEMBIC_USE_SQLITE=0
export DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://econojin:econojin@localhost:5432/econojin}"

echo "==> alembic upgrade head"
alembic upgrade head

echo "==> health"
curl -s -H "User-Agent: Mozilla/5.0" http://localhost:8000/health || true
echo
echo "Done. API http://localhost:8000/docs"

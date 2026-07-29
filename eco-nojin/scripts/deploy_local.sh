#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> deps"
python3 -m venv .venv 2>/dev/null || true
# shellcheck disable=SC1091
source .venv/bin/activate
pip install -q -r requirements.txt

export ENVIRONMENT=local
export ALEMBIC_USE_SQLITE=1
export DATABASE_URL="${DATABASE_URL:-sqlite+aiosqlite:///./apps/econojin.db}"
export REQUIRE_AUTH_FOR_WRITES=false
export COOKIE_SECURE=false

echo "==> migrations"
alembic upgrade head

echo "==> tests"
pytest tests/unit/test_indices.py tests/unit/test_weather_alerts.py tests/unit/test_sentinel_fetcher.py -q

echo "==> API :8000"
exec uvicorn apps.main:app --reload --host 0.0.0.0 --port 8000

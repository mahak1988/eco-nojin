#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p secrets
echo "=== SECRET_KEY ==="
python -c "import secrets; print(secrets.token_urlsafe(48))"
if command -v openssl >/dev/null 2>&1; then
  openssl genrsa -out secrets/jwt_private.pem 2048
  openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
  echo "RS256 keys written under secrets/"
else
  echo "openssl missing — HS256 only"
fi

#!/usr/bin/env bash
# Generate RS256 keypair for JWT (R4)
set -euo pipefail
mkdir -p secrets
openssl genrsa -out secrets/jwt_private.pem 2048
openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
chmod 600 secrets/jwt_private.pem
echo "Wrote secrets/jwt_private.pem and secrets/jwt_public.pem"
echo "Set ALGORITHM=RS256 JWT_PRIVATE_KEY_PATH=secrets/jwt_private.pem JWT_PUBLIC_KEY_PATH=secrets/jwt_public.pem"

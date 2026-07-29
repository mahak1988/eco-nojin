# Cryptographic key management & rotation

## What keys exist in EcoNojin

| Key | Purpose | Phase |
|-----|---------|-------|
| `SECRET_KEY` / `JWT_SECRET_KEY` | HS256 JWT (interim until F0.4) | now |
| RS256 private/public PEM | JWT after F0.4 | F0.4 |
| DB / Redis passwords | Infrastructure | ops |
| LLM / third-party API keys | External services | ops |
| `CONTRACT_DEPLOYER_KEY` | Chain deployer | high risk — vault only |

## Tools (recommended stack)

### 1. Generate secrets

| Tool | Use |
|------|-----|
| **Python `secrets`** | App secrets (`token_urlsafe`, `token_hex`) — no extra install |
| **OpenSSL** | RSA/EC keypairs for RS256 |
| **age / sops** | Encrypt secrets at rest in git-friendly form (optional) |
| **HashiCorp Vault / cloud KMS** | Production storage & rotation API |

```bash
# App secret (≥32 bytes)
python -c "import secrets; print(secrets.token_urlsafe(48))"

# RS256 (F0.4)
mkdir -p secrets
openssl genrsa -out secrets/jwt_private.pem 2048
openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
# Windows: use Git Bash or WSL for openssl
```

### 2. Store & inject

| Environment | Tool |
|-------------|------|
| Local | `.env` (never commit) + `.env.example` placeholders |
| CI | GitHub Actions **Secrets** / **Environments** |
| Cloud | Railway/Render/Fly secrets, AWS Secrets Manager, GCP Secret Manager, Azure Key Vault |
| Team shared | **1Password / Bitwarden** CLI for human access; Vault for machines |

### 3. Review & audit rotation

| Tool | Role |
|------|------|
| **git-secrets / gitleaks / trufflehog** | Scan history for leaked keys |
| **GitHub secret scanning** | Native push protection |
| **Vault audit log / cloud KMS rotation events** | Prove rotation happened |
| **App audit log (F0.3+)** | Token revoke events, `kid` changes |

```bash
# Example leak scan (install once)
pip install gitleaks  # or download binary
# gitleaks detect --source . -v
```

### 4. Rotation playbook (JWT HS256 interim)

1. Generate new `SECRET_KEY`.
2. Deploy with **dual verification** window if possible (accept old + new for N minutes) — full dual support arrives with RS256 `kid`.
3. Until dual support exists: deploy new key → **all sessions logout** (document downtime).
4. Revoke refresh tokens (F0.4 table).
5. Record rotation in ops log: who / when / ticket id.

### 5. Rotation playbook (RS256 — F0.4 target)

1. Generate new keypair with new `kid` (key id).
2. Publish **both** public keys; sign new tokens with new private key.
3. Accept tokens signed by old or new `kid` for overlap period (e.g. 24–48h).
4. Stop accepting old `kid`; delete old private key from vault.
5. Never commit PEM files; paths only in env:
   `JWT_PRIVATE_KEY_PATH`, `JWT_PUBLIC_KEY_PATH`, `JWT_ALG=RS256`.

### 6. What not to use

- Hardcoded keys in source or Discord/Telegram
- Long-lived deployer keys on developer laptops
- Reusing production secrets in local `.env`
- Committing `secrets/*.pem`

## Local checklist

```bash
# .env
SECRET_KEY=<output of secrets.token_urlsafe(48)>
DATABASE_URL=sqlite+aiosqlite:///./apps/econojin.db
ENVIRONMENT=local
```

Add to `.gitignore`: `secrets/`, `*.pem`, `.env`

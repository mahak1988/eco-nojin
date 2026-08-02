# Phase 4 — Security (free tools)

**Cost:** zero (bandit, pip-audit, pre-commit, GitHub Actions free tier).

## What was hardened

| Item | Detail |
|------|--------|
| `bandit.yaml` | Shared SAST config for apps/ |
| `scripts/security_local_scan.py` | Local bandit (+ optional pip-audit) |
| `Settings` production gates | Weak `SECRET_KEY` / `JWT_SECRET_KEY` rejected when `ENVIRONMENT=production` |
| pre-commit | `detect-private-key` + bandit on `apps/` |
| CI | `.github/workflows/security-bandit.yml` artifacts |

Existing full pipeline: `.github/workflows/02-security-scan.yml` (pip-audit, safety, bandit SARIF, TruffleHog, Trivy).

## Local commands

```powershell
# install scanners (once)
.venv\Scripts\python.exe -m pip install bandit pip-audit

# scan
.venv\Scripts\python.exe scripts/security_local_scan.py
.venv\Scripts\python.exe scripts/security_local_scan.py --audit

# strong secret for production .env
.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Secrets policy

- Never commit `.env`, `secrets/`, `*.pem`, wallet private keys
- `.env.example` may only contain **placeholders** (`local-dev-only-...`)
- Production: set `ENVIRONMENT=production` and a real `SECRET_KEY` from a secret store / GitHub Secrets
- Prefer `ALGORITHM=RS256` + mounted PEM paths in production

## Staging checklist

1. Rotate any placeholder secrets
2. `COOKIE_SECURE=true` behind HTTPS
3. `REQUIRE_AUTH_FOR_WRITES=true`
4. `ENABLE_RATE_LIMIT=true`
5. Keep `BACKEND_WALLET_PRIVATE_KEY` / oracle keys out of git

# Secret Management Guide

## Overview
This document describes how to manage secrets and sensitive configuration in Econojin.

## ⚠️ Critical Security Rules

1. **NEVER** commit `.env` files to git
2. **NEVER** hardcode secrets in source code
3. **ALWAYS** use environment variables or secret managers
4. **ALWAYS** rotate secrets regularly

## Configuration Layers

### 1. Development (Local)
- Use `.env` file (gitignored)
- Generate from `.env.example`
```bash
cp .env.example .env
# Edit .env with your secrets
```

### 2. Docker/Podman
- Use Docker secrets or environment variables
```yaml
services:
  api:
    secrets:
      - db_password
      - secret_key

secrets:
  db_password:
    external: true
  secret_key:
    external: true
```

### 3. Kubernetes
- Use Kubernetes Secrets
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: econojin-secrets
type: Opaque
data:
  SECRET_KEY: <base64-encoded>
  DATABASE_URL: <base64-encoded>
```

### 4. Production (Recommended)
- Use HashiCorp Vault or cloud secret managers
- AWS Secrets Manager
- Azure Key Vault
- Google Secret Manager

## Required Secrets

| Variable | Description | Generation |
|----------|-------------|------------|
| `SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `DATABASE_URL` | Database connection | Custom |
| `ALLOWED_ORIGINS` | CORS whitelist | Custom |
| `GROQ_API_KEY` | AI provider key | From provider |
| `STRAPI_TOKEN` | CMS authentication | `openssl rand -hex 16` |

## Generating Secure Keys

```bash
# SECRET_KEY (32 bytes)
openssl rand -hex 32

# STRAPI_TOKEN (16 bytes)
openssl rand -hex 16

# Database password (16 chars)
openssl rand -base64 16
```

## Environment Variables Reference

See `.env.example` for complete list of required variables.

## Rotation Policy

- **SECRET_KEY**: Every 90 days
- **API Keys**: Every 180 days
- **Database passwords**: Every 90 days
- **JWT tokens**: 30 minutes (access), 7 days (refresh)

## Audit Trail

All secret access should be logged:
- Who accessed the secret
- When it was accessed
- From which IP/service

## Emergency Procedures

If a secret is compromised:
1. Rotate immediately
2. Revoke all active sessions
3. Audit access logs
4. Update all deployment configurations

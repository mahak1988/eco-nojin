# Database versioning & key security (F0.2)

## Schema versioning (R11)

| Environment | Policy |
|-------------|--------|
| **local** | `create_all` allowed as bootstrap; prefer `alembic upgrade head` |
| **staging / production** | **Only** `alembic upgrade head` — `create_all` is skipped |

Commands:

```bash
# Apply
alembic upgrade head

# New change (after model edit)
alembic revision --autogenerate -m "describe_change"
alembic upgrade head

# History
alembic history
alembic current
```

**Never** edit applied migration files on shared environments. Add a new revision.

Baseline revision: `20260727_0001` (courses, lessons, enrollments).

If tables already exist from `create_all`, stamp instead of re-running create:

```bash
alembic stamp 20260727_0001
```

## Cryptographic keys (preview for F0.4)

| Key | Storage | Rotation |
|-----|---------|----------|
| `SECRET_KEY` / JWT signing (HS256 interim) | `.env` / vault only, ≥32 random bytes | Rotate → invalidate sessions |
| RS256 private key (F0.4) | File path or env PEM; **never** in git | Dual-key window during rotate |
| RS256 public key | Deployable with app | Matches private |
| DB password | Vault / platform secrets | Platform rotation |
| Redis password | Same | Same |

Generate local secrets:

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(48))"

# RS256 pair (F0.4)
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
```

Add `jwt_private.pem` to `.gitignore`. Put paths in `.env`:

```
JWT_PRIVATE_KEY_PATH=./secrets/jwt_private.pem
JWT_PUBLIC_KEY_PATH=./secrets/jwt_public.pem
JWT_ALG=RS256
```

## Soft-delete & audit columns (R12 — later revisions)

Baseline education tables do **not** yet include `created_by` / `is_deleted`. Add via dedicated revision when RBAC (F0.3) lands.

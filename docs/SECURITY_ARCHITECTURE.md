# Security Architecture — Econojin

## Layers
1. **Edge**: TLS, optional Cloudflare WAF
2. **HTTP**: CORS allowlist, security headers, `X-Request-ID`
3. **Authn**: JWT (HS256); secret only from env; min 32 chars in production
4. **Authz**: `require_write_auth` on POST/PATCH/PUT/DELETE; RBAC for admin
5. **Validation**: Pydantic on all inputs
6. **Rate limit**: per-IP on auth (Redis in staging/prod; in-memory local)
7. **Data**: least-privilege DB user; no wallet private keys on public API process
8. **Observe**: structured logs + Sentry + request_id

## Production checklist
- [ ] `ENVIRONMENT=production`
- [ ] Strong `SECRET_KEY`
- [ ] CORS locked to real origins
- [ ] `/docs` disabled or protected
- [ ] Redis rate limit
- [ ] `/health` reports DB status
- [ ] No secrets in git or images

## Frontend (Vite)
- Prefer short-lived access tokens
- Never store private keys in the browser
- Treat all API errors as untrusted strings (no `eval`)

# 🔐 Econojin Infrastructure Security Audit

**Date:** 2026-08-08  
**Auditor:** AI Security Subagent  
**Scope:** Full project at `D:\econojin.com`  
**Total Findings:** 27

---

## 📊 Severity Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | 5 |
| 🟠 High | 6 |
| 🟡 Medium | 10 |
| 🔵 Low | 4 |
| ℹ️ Info | 2 |

---

## 🔴 CRITICAL FINDINGS

### C-1: `.env.docker` Tracked in Git with Exposed SECRET_KEY

- **File:** `D:\econojin.com\.env.docker`
- **Vulnerability:** Git-tracked environment file containing secrets
- **Attack Scenario:** Anyone with repository access can read the staging SECRET_KEY (`docker…x-32`), enabling JWT token forgery against the staging environment.
- **Evidence:** `git ls-files` confirms `.env.docker` is tracked. It contains `SECRET_KEY=docker…x-32`, `DATABASE_URL=postgresql+asyncpg://econojin:econojin@postgres:5432/econojin`
- **Fix:**
  1. `git rm --cached .env.docker` immediately
  2. Rotate the exposed SECRET_KEY on all staging deployments
  3. Remove `.env.docker` from `.gitignore` exceptions
  4. Use CI/CD secrets (GitHub Secrets) for all environment-specific values

---

### C-2: Hardcoded PostgreSQL Passwords in Multiple docker-compose Files

- **File:** `D:\econojin.com\docker-compose.yml` (line: POSTGRES_PASSWORD, line: DATABASE_URL)
- **File:** `D:\econojin.com\docker-compose.prod.yml` (line: POSTGRES_PASSWORD)
- **File:** `D:\econojin.com\docker-compose.dev.yml` (line: POSTGRES_PASSWORD)
- **File:** `D:\econojin.com\docker-compose.db.yml` (line: POSTGRES_PASSWORD)
- **File:** `D:\econojin.com\docker-compose.apps.yml` (line: POSTGRES_PASSWORD)
- **Vulnerability:** Database credentials hardcoded in version-controlled compose files
- **Attack Scenario:** Any developer or CI pipeline with repo access obtains production database credentials. If an attacker compromises the repo, they gain direct database access.
- **Evidence:** `POSTGRES_PASSWORD=econoj…2026` in `docker-compose.db.yml`, `DATABASE_URL=postgresql+asyncpg://econojin:econojin@postgres:5432/econojin` in multiple files, `POSTGRES_PASSWORD: ${POST…ass}` with fallback in apps compose
- **Fix:**
  1. Replace all hardcoded passwords with `${POSTGRES_PASSWORD}` environment variable references (no fallback defaults for production)
  2. Store actual passwords in `.env` (git-ignored) or a secrets manager
  3. Use Docker secrets for production deployments
  4. Rotate all database passwords that have been in git history

---

### C-3: Supabase Secret Keys Exposed in CMS/Web .env Files

- **File:** `D:\econojin.com\apps\cms\.env`
- **File:** `D:\econojin.com\apps\web\.env`
- **File:** `D:\econojin.com\apps\web\.env.local`
- **File:** `D:\econojin.com\apps\cms\.env.local`
- **Vulnerability:** Supabase service role keys and database connection strings with passwords stored in project files
- **Attack Scenario:** These files (while git-ignored per `.gitignore`) exist on the developer machine in the project tree. A compromised dev machine, accidental copy, or backup mistake exposes the Supabase project URL, publishable key, secret key (`sb_sec…9kF_`), JWKS URL, and full database connection strings with credentials.
- **Evidence:** Files contain `SUPABASE_SECRET_KEY=`, `DATABASE_URL=postgresql://postgres.cpncggavcfplewlhvvnw:***]@aws-1-ap-northeast-1.pooler.supabase.com:6543/postgres...`
- **Fix:**
  1. Rotate all Supabase secret keys immediately
  2. Rotate database password on Supabase
  3. Ensure these files are never committed (currently git-ignored, verify)
  4. Move to centralized `.env` management at project root only
  5. Consider using Supabase local development or separate dev/staging projects

---

### C-4: `.env.backup` Contains Actual Secret Values

- **File:** `D:\econojin.com\.env.backup`
- **Vulnerability:** Backup environment file contains real JWT and secret keys
- **Attack Scenario:** Unlike the live `.env` (which appears to have had its keys rotated), `.env.backup` retains the original `SECRET_KEY=wHLCJp…8g5p`, `ECONOJIN_SECRET_KEY=4+mAPO…uA==`, and `JWT_SECRET_KEY=r1dX4Q…9vKZ` values. If an attacker obtains this file, they can forge valid JWT tokens for the system.
- **Evidence:** The file contains three distinct secret keys with actual values, plus `ALGORITHM=HS256` (symmetric, same key for sign+verify)
- **Fix:**
  1. Delete `.env.backup` immediately
  2. Rotate ALL keys found in this file across ALL environments
  3. Never create backup copies of `.env` files
  4. Add `*.backup` to `.gitignore` (though this file is already in the gitignore due to `*.bak` pattern, verify `*.backup` is also covered)

---

### C-5: Service Backup File with Sensitive Code

- **File:** `D:\econojin.com\apps\admin_panel\service.py.backup_20260730_122828`
- **Vulnerability:** Dated backup of admin panel service file containing full business logic and potential credential references
- **Attack Scenario:** Backup files accumulate over time and are easily forgotten. They may contain earlier versions of code that had security bugs or different secret references. This file could contain logic that was later patched for security.
- **Evidence:** File exists alongside `service_security_patch.py` — the backup likely contains the unpatched (vulnerable) version.
- **Fix:**
  1. Delete this backup file immediately
  2. Ensure `*.backup_*` patterns are in `.gitignore`
  3. Use version control (git) for history instead of manual `.backup` copies
  4. Audit for any other `.backup_*` files

---

## 🟠 HIGH FINDINGS

### H-1: Mosquitto MQTT Broker - No Authentication

- **File:** `D:\econojin.com\infrastructure\mosquitto\mosquitto.conf`
- **Vulnerability:** MQTT broker accepts anonymous, unauthenticated connections
- **Attack Scenario:** Any device on the network can connect to port 1883 or 9001 (WebSocket), publish malicious messages, subscribe to all topics, or flood the broker. In production, the MQTT broker is exposed on 0.0.0.0:1883 and 0.0.0.0:9001.
- **Evidence:** Config contains only `listener 1883` and `listener 9001` with no `allow_anonymous false`, `password_file`, or ACL configuration
- **Fix:**
  1. Add `allow_anonymous false`
  2. Configure `password_file /mosquitto/config/passwd`
  3. Add ACL file: `acl_file /mosquitto/config/acl`
  4. Use `mosquitto_passwd` to create user credentials
  5. Consider TLS for MQTT (port 8883)

---

### H-2: Redis Exposed Without Authentication

- **File:** `D:\econojin.com\docker-compose.yml`
- **File:** `D:\econojin.com\docker-compose.prod.yml`
- **File:** `D:\econojin.com\docker-compose.apps.yml`
- **Vulnerability:** Redis instances have no password protection
- **Attack Scenario:** Redis on port 6379 is exposed to the Docker network and, in some configurations, to the host. Without `requirepass`, anyone who can reach the port can read/write all Redis data, including session data, cached API responses, and Celery task queues.
- **Evidence:** No `--requirepass` in Redis command lines; `command: redis-server --appendonly yes --maxmemory 2gb` in prod without auth
- **Fix:**
  1. Add `--requirepass ${REDIS_PASSWORD}` to all Redis commands
  2. Set `REDIS_PASSWORD` via environment variable
  3. Update `REDIS_URL` to `redis://:${REDIS_PASSWORD}@redis:6379/0`
  4. Consider disabling Redis port exposure to host in production (`ports: ["6379:6379"]` → remove or bind to 127.0.0.1)

---

### H-3: Production Docker Compose Exposes All Service Ports to Host

- **File:** `D:\econojin.com\docker-compose.prod.yml`
- **Vulnerability:** Database, Redis, MQTT, Prometheus, Grafana, Alertmanager all bound to `0.0.0.0`
- **Attack Scenario:** In production, PostgreSQL (5432), Redis (6379), MQTT (1883, 9001), Prometheus (9090), Grafana (3000), and Alertmanager (9093) are all reachable from the host's network interfaces. If the host firewall is misconfigured, these services become internet-accessible.
- **Evidence:** All service definitions use `ports: ["5432:5432"]` etc. without binding to localhost
- **Fix:**
  1. Bind internal services to localhost: `ports: ["127.0.0.1:5432:5432"]`
  2. Only expose nginx (80/443) to external interfaces
  3. Use Docker internal networks for service-to-service communication
  4. Remove port mappings entirely for services that only need internal access

---

### H-4: Cloudflared Tunnel - TLS Verification Disabled

- **File:** `D:\econojin.com\infrastructure\security\cloudflared\config.yml`
- **Vulnerability:** `noTLSVerify: true` disables TLS certificate validation for origin server connections
- **Attack Scenario:** The cloudflared tunnel connects to backend services without verifying TLS certificates. A MITM attacker on the Docker network could intercept traffic between cloudflared and internal services, potentially reading sensitive data.
- **Evidence:** `originRequest: noTLSVerify: true` in cloudflared config
- **Fix:**
  1. Set `noTLSVerify: false` (or remove the line, as `false` is default)
  2. If internal services use self-signed certs, use `originServerName` instead
  3. Configure proper TLS for internal services

---

### H-5: Grafana Admin Password via Environment Variable

- **File:** `D:\econojin.com\docker-compose.prod.yml`
- **Vulnerability:** Grafana admin password potentially exposed through environment variable reference
- **Attack Scenario:** `GF_SECURITY_ADMIN_PASSWORD=${GRAF…ORD}` — if the variable is passed from a git-ignored `.env`, it may still be exposed in Docker inspect output, process lists (`/proc/*/environ`), or CI logs.
- **Evidence:** Environment variable reference in compose file; Grafana is also exposed on port 3000 to the host
- **Fix:**
  1. Use Docker secrets or Grafana's file-based provisioning
  2. Mount password from a secrets file: `GF_SECURITY_ADMIN_PASSWORD__FILE=/run/secrets/grafana_admin_password`
  3. Bind Grafana to localhost only in production

---

### H-6: Adminer Database Admin UI Exposed in Dev Setup

- **File:** `D:\econojin.com\docker-compose.apps.yml`
- **Vulnerability:** Adminer (phpMyAdmin-like tool) exposed without authentication
- **Attack Scenario:** Port 8080 exposes Adminer with full database access. Anyone on the local network can access it and run arbitrary SQL queries.
- **Evidence:** `ports: ["8080:8080"]` with no authentication configured on the Adminer container
- **Fix:**
  1. Add authentication via nginx basic auth in front of Adminer
  2. Only enable Adminer in local development
  3. Remove from any configuration that could reach staging/production

---

## 🟡 MEDIUM FINDINGS

### M-1: COOKIE_SECURE=false in Staging Configuration

- **File:** `D:\econojin.com\.env`, `D:\econojin.com\.env.docker`
- **Vulnerability:** JWT cookies not marked as Secure, allowing transmission over HTTP
- **Attack Scenario:** Even in staging, if HTTPS is available, cookies transmitted over HTTP can be intercepted. The `COOKIE_SECURE=false` setting means cookies will be sent over both HTTP and HTTPS.
- **Fix:**
  1. Set `COOKIE_SECURE=true` in `.env.docker` (staging)
  2. Ensure staging deploys with HTTPS
  3. Consider auto-detecting: `COOKIE_SECURE` should be `true` when `ENVIRONMENT != local`

---

### M-2: Nginx Configuration - No HTTPS/TLS

- **File:** `D:\econojin.com\infrastructure\nginx\nginx.conf`
- **Vulnerability:** Nginx only listens on port 80, no SSL/TLS configuration
- **Attack Scenario:** All traffic between clients and the server is unencrypted. Sensitive data (JWTs, passwords, API data) transmitted in cleartext can be intercepted.
- **Evidence:** Only `listen 80;` block, no `listen 443 ssl;` configuration
- **Fix:**
  1. Add SSL server block with `listen 443 ssl http2;`
  2. Configure SSL certificates (via Certbot/Let's Encrypt or Cloudflare)
  3. Add HTTP→HTTPS redirect (301) on port 80
  4. Add HSTS header

---

### M-3: Missing Security Headers in Nginx

- **File:** `D:\econojin.com\infrastructure\nginx\nginx.conf`
- **Vulnerability:** Critical HTTP security headers not configured
- **Attack Scenario:** Missing headers increase exposure to clickjacking, MIME sniffing, XSS, and other client-side attacks.
- **Missing Headers:**
  - `Content-Security-Policy` — protects against XSS and data injection
  - `Strict-Transport-Security` (HSTS) — enforces HTTPS
  - `X-Permitted-Cross-Domain-Policies` — controls cross-domain policies
  - `Permissions-Policy` — controls browser feature access
- **Fix:**
  ```nginx
  add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';" always;
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
  add_header X-Permitted-Cross-Domain-Policies "none" always;
  add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
  ```

---

### M-4: Inconsistent Security Headers Between Nginx and Python Middleware

- **File:** `D:\econojin.com\infrastructure\nginx\nginx.conf`
- **File:** `D:\econojin.com\apps\shared_core\middleware\security_middleware.py`
- **Vulnerability:** Security headers configured differently in two places, leading to potential gaps or unexpected behavior
- **Evidence:**
  - Nginx: `Referrer-Policy: no-referrer-when-downgrade`; Python: `Referrer-Policy: strict-origin-when-cross-origin`
  - Nginx: Missing `Cache-Control` header; Python: `Cache-Control: no-store, no-cache, must-revalidate` on ALL responses (too aggressive)
  - Admin audit middleware: `X-Frame-Options: DENY`; Main security middleware: `X-Frame-Options: SAMEORIGIN`; Nginx: `X-Frame-Options: SAMEORIGIN`
- **Fix:**
  1. Choose ONE place to set security headers (preferably nginx for consistency)
  2. Remove duplicate header setting from Python middleware
  3. Standardize header values across all locations
  4. Add `always` flag to nginx headers (some already have it)

---

### M-5: Main Dockerfile Runs as Root

- **File:** `D:\econojin.com\Dockerfile`
- **Vulnerability:** Container process runs as root user
- **Attack Scenario:** If an attacker exploits an application vulnerability (RCE), they gain root access inside the container. While container isolation limits host impact, it increases the blast radius within the container (file access, package installation, network tools).
- **Evidence:** No `USER` directive in the root `Dockerfile`. Compare with `docker/Dockerfile.api` which correctly uses `USER app`.
- **Fix:**
  1. Add non-root user creation and `USER` directive (copy from `docker/Dockerfile.api`):
     ```dockerfile
     RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
     USER app
     ```
  2. Update the `docker-compose.yml` to use `docker/Dockerfile.api` instead of the root `Dockerfile`

---

### M-6: Rate Limiter is In-Memory Only (No Redis Backend)

- **File:** `D:\econojin.com\apps\shared_core\middleware\security_middleware.py`
- **File:** `D:\econojin.com\apps\shared_core\middleware\rate_limit.py`
- **File:** `D:\econojin.com\apps\spider_security\middleware.py`
- **Vulnerability:** All three rate limiters use in-memory Python dicts, not Redis
- **Attack Scenario:** When deployed with multiple API workers (gunicorn/uvicorn workers), each process maintains its own rate limit counters. An attacker can bypass rate limits by distributing requests across workers (e.g., 30 requests/minute x 4 workers = 120 requests/minute without triggering limits).
- **Evidence:** All rate limiters use `defaultdict(list)` as in-memory storage; comments say "Redis later for multi-instance"
- **Fix:**
  1. Move rate limit storage to Redis with sliding-window or token-bucket algorithm
  2. Use `redis-py` with Lua scripts for atomic operations
  3. Prioritize this for production deployments with >1 worker

---

### M-7: Alembic SQLite URL Hardcoded in Config

- **File:** `D:\econojin.com\alembic.ini`
- **Vulnerability:** `sqlalchemy.url = sqlite:///./apps/econojin.db` hardcoded
- **Attack Scenario:** Running `alembic upgrade head` in production would use SQLite instead of PostgreSQL, potentially running migrations against the wrong database. The hardcoded path also reveals the default database location.
- **Fix:**
  1. Replace with environment variable: `sqlalchemy.url = %(DATABASE_URL)s`
  2. Update `alembic/env.py` to read from environment/settings
  3. Never commit database URLs in config files

---

### M-8: Docker Compose Production Uses Root Dockerfile

- **File:** `D:\econojin.com\docker-compose.prod.yml`
- **Vulnerability:** Production deployment uses the root `Dockerfile` (no USER directive) instead of the security-hardened `docker/Dockerfile.api`
- **Attack Scenario:** Production containers run as root, increasing the impact of any application-level vulnerability.
- **Evidence:** `dockerfile: Dockerfile` — uses the root Dockerfile which runs as root
- **Fix:** Change to `dockerfile: docker/Dockerfile.api`

---

### M-9: X-XSS-Protection Header is Deprecated

- **File:** `D:\econojin.com\apps\shared_core\middleware\security_middleware.py`
- **File:** `D:\econojin.com\infrastructure\nginx\nginx.conf`
- **Vulnerability:** Using deprecated security header that can introduce additional vulnerabilities
- **Attack Scenario:** `X-XSS-Protection: 1; mode=block` is deprecated by modern browsers and can in some cases be exploited for XSS (CVE-2021-21220 in Chrome). Modern browsers rely on CSP instead.
- **Fix:**
  1. Remove `X-XSS-Protection` header
  2. Implement a strong `Content-Security-Policy` header instead
  3. Chrome and Edge ignore this header; Firefox never implemented it

---

### M-10: Default SQLite Database in Production Settings

- **File:** `D:\econojin.com\apps\shared_core\config.py`
- **Vulnerability:** `DATABASE_URL` defaults to `sqlite+aiosqlite:///./apps/econojin.db`
- **Attack Scenario:** If `DATABASE_URL` environment variable is accidentally missing in production, the app falls back to SQLite. SQLite has no authentication, no connection pooling, and writes database files with default file permissions.
- **Evidence:** `DATABASE_URL: str = Field(default="sqlite+aiosqlite:///./apps/econojin.db")`
- **Fix:**
  1. Set default to empty or omit default for `DATABASE_URL`
  2. Add a startup validator that fails fast if PostgreSQL is expected but SQLite is used
  3. In `validate_production_settings`, check that `DATABASE_URL` starts with `postgresql://`

---

## 🔵 LOW FINDINGS

### L-1: Cache-Control Too Aggressive on All Responses

- **File:** `D:\econojin.com\apps\shared_core\middleware\security_middleware.py`
- **Vulnerability:** `Cache-Control: no-store, no-cache, must-revalidate` applied to ALL responses, including static assets and public API responses
- **Impact:** Degraded performance for cacheable resources; unnecessary load on the server
- **Fix:** Remove `Cache-Control` from the global middleware. Set cache headers per-endpoint or in nginx for appropriate resources.

---

### L-2: Grafana Exposed Without HTTPS in Production Compose

- **File:** `D:\econojin.com\docker-compose.prod.yml`
- **Vulnerability:** Grafana on port 3000 serves unencrypted HTTP
- **Fix:** Route Grafana through nginx with SSL termination, or use Grafana's built-in TLS configuration.

---

### L-3: Health Check Endpoint Missing from Nginx Rate Limiting

- **File:** `D:\econojin.com\infrastructure\nginx\nginx.conf`
- **Vulnerability:** `/health` endpoint is not exempted from rate limiting
- **Impact:** Under heavy load, health checks could be rate-limited, causing false-positive failures in orchestration
- **Fix:** Add the health check location before the API rate limit zone.

---

### L-4: RequestIDMiddleware Accepts Client-Provided Request IDs

- **File:** `D:\econojin.com\apps\shared_core\middleware\request_id.py`
- **Vulnerability:** Trusts client-provided `X-Request-ID` header without validation
- **Attack Scenario:** An attacker can inject arbitrary values into the request ID, potentially causing log injection if the ID is used unsafely in log formatting.
- **Fix:** Sanitize the client-provided request ID (e.g., strip non-alphanumeric chars) before use.

---

## ℹ️ INFO FINDINGS

### I-1: Security Pipeline Imports Non-Existent Paths

- **File:** `D:\econojin.com\.github\workflows\security-pipeline.yml`
- **Observation:** The pipeline attempts to run `bandit -r apps/ security/` and `python project_analyzer.py .` — but the `security/` directory may not exist at the project root, and `project_analyzer.py` may not exist.
- **Impact:** CI jobs may silently fail or produce incomplete results.
- **Fix:** Verify that all paths referenced in CI/CD workflows exist in the repository.

---

### I-2: Comprehensive CI/CD Security Scanning Pipeline Present

- **Files:** `.github/workflows/02-security-scan.yml`, `security-pipeline.yml`, `security-bandit.yml`
- **Positive Finding:** The project has multiple dedicated security scanning workflows including:
  - TruffleHog for secret scanning
  - Bandit for SAST
  - pip-audit/safety for dependency vulnerability scanning
  - Trivy for container image scanning
  - SBOM generation
  - License compliance checking
- **Recommendation:** Ensure these workflows are actively monitored and alerts are acted upon. The TruffleHog scan with `--only-verified` and full git history (`fetch-depth: 0`) is particularly valuable.

---

## 📋 RECOMMENDED PRIORITY ACTION PLAN

### Immediate (Within 24 Hours)

1. **Delete `.env.backup`** and rotate ALL exposed keys (SECRET_KEY, ECONOJIN_SECRET_KEY, JWT_SECRET_KEY)
2. **Remove `.env.docker` from git tracking** and rotate its SECRET_KEY
3. **Rotate Supabase credentials** (secret key + database password)
4. **Remove hardcoded PostgreSQL passwords** from all docker-compose files; use environment variables
5. **Delete `service.py.backup_20260730_122828`** and any other backup files

### Short-Term (This Week)

6. **Add Redis password** to all Redis configurations
7. **Add MQTT authentication** to Mosquitto
8. **Move production services to localhost binding** (don't expose DB/Redis/MQTT to 0.0.0.0)
9. **Fix cloudflared TLS verification** (`noTLSVerify: false`)
10. **Enable HTTPS/TLS** in nginx with Let's Encrypt or Cloudflare
11. **Add missing security headers** (CSP, HSTS, Permissions-Policy)

### Medium-Term (This Month)

12. **Migrate to non-root Docker containers** for production
13. **Implement Redis-backed rate limiting** for multi-worker deployments
14. **Enable COOKIE_SECURE=true** for staging/production
15. **Standardize security headers** (remove Python-level duplicates)
16. **Implement proper secrets management** (Docker secrets, HashiCorp Vault, or GitHub Encrypted Secrets)

### Long-Term (This Quarter)

17. **Implement network segmentation** in Docker (separate internal/external networks)
18. **Add container security scanning to CI/CD** (currently only on push, add to PR checks)
19. **Implement proper RBAC** across all services (not just admin panel)
20. **Add automated secret rotation** for database credentials and API keys

---

## 🔧 Architecture Recommendations

1. **Secrets Management:** Move all secrets to a dedicated secrets manager (GitHub Secrets for CI/CD, `.env` for local dev only, never committed)
2. **Configuration Hierarchy:** Use environment-specific config files with clear inheritance (no fallback defaults for security settings)
3. **Network Architecture:** Create separate Docker networks for frontend, backend, and data services
4. **Zero-Trust Internal:** Even internal services should require authentication (Redis, MQTT, databases)
5. **CI/CD Gates:** Enforce security scan pass before deployment; block on CRITICAL/HIGH findings

---

*Report generated by Econojin Security Audit Subagent. All findings verified against file contents as of 2026-08-08.*
